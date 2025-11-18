"""
Module : models/metadata.py
Description : Modèles de données pour les métadonnées KLV
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from collections import OrderedDict


@dataclass
class KLVMetadataItem:
    """
    Représente un élément de métadonnée KLV individuel.
    
    Attributes:
        tag: Numéro de tag KLV
        lds_name: Nom Local Data Set
        esd_name: Nom Enhanced Sensor Data
        uds_name: Nom User Defined Set
        value: Valeur de la métadonnée (string)
    """
    tag: int
    lds_name: str
    esd_name: str
    uds_name: str
    value: str


@dataclass
class MetadataPacket:
    """
    Représente un packet KLV complet avec son timestamp.
    
    Attributes:
        pts: Presentation Time Stamp (33 bits, unités de 1/90000 seconde)
        time_seconds: Temps en secondes (calculé depuis PTS)
        time_formatted: Temps formaté (HH:MM:SS.mmm)
        metadata: Dictionnaire des métadonnées (TAG -> KLVMetadataItem)
    """
    pts: Optional[int]
    time_seconds: Optional[float]
    time_formatted: str
    metadata: Dict[int, KLVMetadataItem]
    
    @classmethod
    def from_klv_packet(cls, packet, pts: Optional[int] = None, 
                       time_seconds: Optional[float] = None,
                       time_formatted: str = "00:00:00.000") -> 'MetadataPacket':
        """
        Crée un MetadataPacket depuis un packet KLV parsé.
        
        Args:
            packet: Packet KLV parsé (avec méthode MetadataList)
            pts: PTS associé
            time_seconds: Temps en secondes
            time_formatted: Temps formaté
            
        Returns:
            MetadataPacket
        """
        metadata_dict = {}
        
        if hasattr(packet, 'MetadataList'):
            metadata_raw = packet.MetadataList()
            
            for tag, (lds_name, esd_name, uds_name, value) in metadata_raw.items():
                metadata_dict[tag] = KLVMetadataItem(
                    tag=tag,
                    lds_name=lds_name or "",
                    esd_name=esd_name or "",
                    uds_name=uds_name or "",
                    value=value or ""
                )
        
        return cls(
            pts=pts,
            time_seconds=time_seconds,
            time_formatted=time_formatted,
            metadata=metadata_dict
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le packet en dictionnaire pour export CSV.
        
        Returns:
            Dictionnaire avec toutes les métadonnées
        """
        result = {
            'pts': self.pts,
            'time_seconds': self.time_seconds,
            'time_formatted': self.time_formatted
        }
        
        # Ajouter chaque métadonnée avec son tag comme clé
        for tag, item in self.metadata.items():
            result[f'TAG_{tag}'] = item.value
            result[f'TAG_{tag}_LDSName'] = item.lds_name
            result[f'TAG_{tag}_ESDName'] = item.esd_name
            result[f'TAG_{tag}_UDSName'] = item.uds_name
        
        return result


@dataclass
class MetadataCollection:
    """
    Collection ordonnée de packets de métadonnées.
    
    Attributes:
        packets: Liste ordonnée de MetadataPacket
        video_path: Chemin du fichier vidéo source
        total_packets: Nombre total de packets
    """
    packets: list[MetadataPacket]
    video_path: str
    total_packets: int = 0
    
    def __post_init__(self):
        """Initialise total_packets après création."""
        if self.total_packets == 0:
            self.total_packets = len(self.packets)
    
    def get_metadata_at_time(self, time_seconds: float) -> Optional[Dict[int, KLVMetadataItem]]:
        """
        Récupère les métadonnées à un temps donné.
        
        Args:
            time_seconds: Temps en secondes
            
        Returns:
            Dictionnaire de métadonnées ou None
        """
        from utils.time_utils import find_metadata_for_time
        
        metadata_list = [
            {'time_seconds': p.time_seconds, 'metadata': p.metadata}
            for p in self.packets
        ]
        
        return find_metadata_for_time(metadata_list, time_seconds)
    
    def get_packet_at_time(self, time_seconds: float) -> Optional[MetadataPacket]:
        """
        Récupère le packet complet à un temps donné.
        
        Args:
            time_seconds: Temps en secondes
            
        Returns:
            MetadataPacket ou None
        """
        if not self.packets:
            return None
        
        # Recherche linéaire (optimisable)
        for packet in self.packets:
            if packet.time_seconds is not None and packet.time_seconds >= time_seconds:
                return packet
        
        # Retourner le dernier packet si après la fin
        return self.packets[-1] if self.packets else None

