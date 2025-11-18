"""
Module : services/klv_extractor.py
Description : Service d'extraction des métadonnées KLV depuis MPEG-TS
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

import logging
from typing import List, Optional
from models.metadata import MetadataPacket
from models.video import VideoInfo
from utils.time_utils import pts_to_timedelta, format_time
import klvdata
import mpegtsdata
from klvreconstructor import reconstruct_klv_packets

logger = logging.getLogger(__name__)


class KLVExtractor:
    """
    Service d'extraction des métadonnées KLV depuis des fichiers MPEG-TS.
    """
    
    def __init__(self):
        """Initialise le service d'extraction."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_from_mpegts(self, video_path: str) -> List[MetadataPacket]:
        """
        Extrait les métadonnées KLV depuis un fichier MPEG-TS.
        
        Args:
            video_path: Chemin du fichier vidéo
            
        Returns:
            Liste de MetadataPacket avec timestamps
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            IOError: Si erreur de lecture
        """
        self.logger.info(f"Extraction KLV depuis {video_path}")
        
        try:
            with open(video_path, 'rb') as stream:
                streams_packets = mpegtsdata.extract_streams(stream)
        except FileNotFoundError:
            self.logger.error(f"Fichier non trouvé: {video_path}")
            raise
        except IOError as e:
            self.logger.error(f"Erreur de lecture: {e}")
            raise
        
        all_packets = []
        base_pts = None
        
        for stream_id in streams_packets:
            packets = streams_packets[stream_id]
            self.logger.debug(f"Stream 0x{stream_id:X}: {len(packets)} packets")
            
            klv_data, pts_per_packet = reconstruct_klv_packets(packets)
            
            if not pts_per_packet:
                self.logger.debug(f"Aucune métadonnée KLV dans stream 0x{stream_id:X}")
                continue
            
            # Déterminer le PTS de base (premier PTS valide)
            valid_pts = [pts for pts in pts_per_packet if pts is not None]
            if valid_pts:
                if base_pts is None:
                    base_pts = valid_pts[0]
                    self.logger.info(f"PTS de base: {base_pts}")
            
            # Parser les métadonnées KLV
            index = 0
            for packet in klvdata.StreamParser(klv_data):
                if not hasattr(packet, 'MetadataList'):
                    self.logger.warning(f"Packet sans MetadataList: {type(packet).__name__}")
                    index += 1
                    continue
                
                pts = pts_per_packet[index] if index < len(pts_per_packet) else None
                
                # Convertir PTS en temps
                if pts is not None and base_pts is not None:
                    time_seconds = pts_to_timedelta(pts, base_pts)
                    time_formatted = format_time(time_seconds)
                else:
                    time_seconds = None
                    time_formatted = "00:00:00.000"
                
                # Créer le MetadataPacket
                try:
                    metadata_packet = MetadataPacket.from_klv_packet(
                        packet=packet,
                        pts=pts,
                        time_seconds=time_seconds,
                        time_formatted=time_formatted
                    )
                    all_packets.append(metadata_packet)
                except Exception as e:
                    self.logger.error(f"Erreur lors de la création du MetadataPacket: {e}")
                
                index += 1
        
        self.logger.info(f"Extraction terminée: {len(all_packets)} packets KLV trouvés")
        return all_packets
    
    def extract_from_klv_file(self, klv_path: str) -> List[MetadataPacket]:
        """
        Extrait les métadonnées KLV depuis un fichier KLV binaire.
        Note: Sans PTS, les timestamps seront None.
        
        Args:
            klv_path: Chemin du fichier KLV
            
        Returns:
            Liste de MetadataPacket (sans timestamps)
        """
        self.logger.info(f"Extraction KLV depuis fichier binaire: {klv_path}")
        
        try:
            with open(klv_path, 'rb') as stream:
                packets = []
                index = 0
                
                for packet in klvdata.StreamParser(stream):
                    if not hasattr(packet, 'MetadataList'):
                        continue
                    
                    metadata_packet = MetadataPacket.from_klv_packet(
                        packet=packet,
                        pts=None,
                        time_seconds=None,
                        time_formatted=f"00:00:00.{index:03d}"
                    )
                    packets.append(metadata_packet)
                    index += 1
                
                self.logger.info(f"Extraction terminée: {len(packets)} packets KLV trouvés")
                return packets
                
        except FileNotFoundError:
            self.logger.error(f"Fichier non trouvé: {klv_path}")
            raise
        except IOError as e:
            self.logger.error(f"Erreur de lecture: {e}")
            raise

