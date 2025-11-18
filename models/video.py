"""
Module : models/video.py
Description : Modèle pour les informations vidéo
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class VideoInfo:
    """
    Informations sur un fichier vidéo.
    
    Attributes:
        path: Chemin du fichier vidéo
        filename: Nom du fichier
        size_bytes: Taille du fichier en bytes
        duration_seconds: Durée en secondes (si disponible)
        has_klv: Indique si le fichier contient des métadonnées KLV
    """
    path: str
    filename: str
    size_bytes: int = 0
    duration_seconds: Optional[float] = None
    has_klv: bool = False
    
    @classmethod
    def from_path(cls, path: str) -> 'VideoInfo':
        """
        Crée un VideoInfo depuis un chemin de fichier.
        
        Args:
            path: Chemin du fichier
            
        Returns:
            VideoInfo
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            return cls(
                path=path,
                filename=path_obj.name,
                size_bytes=0
            )
        
        return cls(
            path=str(path_obj.absolute()),
            filename=path_obj.name,
            size_bytes=path_obj.stat().st_size
        )
    
    def format_size(self) -> str:
        """
        Formate la taille en format lisible.
        
        Returns:
            Chaîne formatée (ex: "600.5 MB")
        """
        if self.size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size_bytes < 1024.0:
                return f"{self.size_bytes:.1f} {unit}"
            self.size_bytes /= 1024.0
        
        return f"{self.size_bytes:.1f} TB"

