"""
Module : services/metadata_manager.py
Description : Gestionnaire de métadonnées en mémoire
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

import logging
from typing import Optional, Dict
from models.metadata import MetadataCollection, MetadataPacket, KLVMetadataItem
from models.video import VideoInfo

logger = logging.getLogger(__name__)


class MetadataManager:
    """
    Gestionnaire centralisé des métadonnées en mémoire.
    """
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._collection: Optional[MetadataCollection] = None
        self._video_info: Optional[VideoInfo] = None
    
    def load_metadata(self, collection: MetadataCollection, video_info: VideoInfo):
        """
        Charge une collection de métadonnées en mémoire.
        
        Args:
            collection: MetadataCollection à charger
            video_info: Informations sur la vidéo
        """
        self.logger.info(f"Chargement de {collection.total_packets} packets de métadonnées")
        self._collection = collection
        self._video_info = video_info
        self.logger.info("Métadonnées chargées en mémoire")
    
    def clear(self):
        """Vide les métadonnées de la mémoire."""
        self.logger.info("Vidage des métadonnées")
        self._collection = None
        self._video_info = None
    
    @property
    def has_metadata(self) -> bool:
        """
        Vérifie si des métadonnées sont chargées.
        
        Returns:
            True si des métadonnées sont disponibles
        """
        return self._collection is not None and self._collection.total_packets > 0
    
    @property
    def collection(self) -> Optional[MetadataCollection]:
        """
        Récupère la collection de métadonnées.
        
        Returns:
            MetadataCollection ou None
        """
        return self._collection
    
    @property
    def video_info(self) -> Optional[VideoInfo]:
        """
        Récupère les informations vidéo.
        
        Returns:
            VideoInfo ou None
        """
        return self._video_info
    
    def get_metadata_at_time(self, time_seconds: float) -> Optional[Dict[int, KLVMetadataItem]]:
        """
        Récupère les métadonnées à un temps donné.
        
        Args:
            time_seconds: Temps en secondes
            
        Returns:
            Dictionnaire de métadonnées ou None
        """
        if not self.has_metadata:
            return None
        
        return self._collection.get_metadata_at_time(time_seconds)
    
    def get_packet_at_time(self, time_seconds: float) -> Optional[MetadataPacket]:
        """
        Récupère le packet complet à un temps donné.
        
        Args:
            time_seconds: Temps en secondes
            
        Returns:
            MetadataPacket ou None
        """
        if not self.has_metadata:
            return None
        
        return self._collection.get_packet_at_time(time_seconds)
    
    def get_total_packets(self) -> int:
        """
        Retourne le nombre total de packets.
        
        Returns:
            Nombre de packets ou 0
        """
        if not self.has_metadata:
            return 0
        
        return self._collection.total_packets

