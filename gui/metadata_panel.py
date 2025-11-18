"""
Module : gui/metadata_panel.py
Description : Panel d'affichage des métadonnées KLV
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PySide6.QtCore import Qt
from typing import Optional, Dict
from models.metadata import KLVMetadataItem


class MetadataPanel(QWidget):
    """
    Panel d'affichage des métadonnées KLV synchronisées avec la vidéo.
    """
    
    def __init__(self, parent=None):
        """
        Initialise le panel de métadonnées.
        
        Args:
            parent: Widget parent
        """
        super().__init__(parent)
        self._metadata_loaded = False  # Indique si des métadonnées ont été chargées
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Label titre
        title_label = QLabel("Métadonnées KLV")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Label temps
        self.time_label = QLabel("Temps: 00:00:00.000")
        self.time_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.time_label)
        
        # Liste des métadonnées
        self.metadata_list = QListWidget()
        self.metadata_list.setAlternatingRowColors(True)
        layout.addWidget(self.metadata_list)
        
        # Message par défaut
        self._show_empty_message()
    
    def _show_empty_message(self):
        """Affiche un message quand aucune métadonnée n'est disponible."""
        self.metadata_list.clear()
        
        if self._metadata_loaded:
            # Métadonnées chargées mais aucune à cet instant précis
            self.metadata_list.addItem("Aucune métadonnée disponible à cet instant")
            self.metadata_list.item(0).setForeground(Qt.GlobalColor.gray)
        else:
            # Aucune métadonnée dans la vidéo (pas encore analysée ou aucune trouvée)
            self.metadata_list.addItem("Aucune métadonnée KLV dans cette vidéo")
            self.metadata_list.item(0).setForeground(Qt.GlobalColor.darkGray)
        
        self.time_label.setText("Temps: --:--:--.---")
    
    def update_metadata(self, metadata: Optional[Dict[int, KLVMetadataItem]], 
                      time_seconds: Optional[float] = None):
        """
        Met à jour l'affichage des métadonnées.
        
        Args:
            metadata: Dictionnaire de métadonnées (TAG -> KLVMetadataItem)
            time_seconds: Temps en secondes (optionnel)
        """
        self.metadata_list.clear()
        
        if not metadata:
            self._show_empty_message()
            return
        
        # Mettre à jour le temps si fourni
        if time_seconds is not None:
            from utils.time_utils import format_time
            time_str = format_time(time_seconds)
            self.time_label.setText(f"Temps: {time_str}")
        
        # Afficher les métadonnées
        # Trier par TAG pour un affichage cohérent
        sorted_items = sorted(metadata.items(), key=lambda x: x[0])
        
        for tag, item in sorted_items:
            # Format: "TAG X: LDSName = Value"
            display_name = item.lds_name or item.esd_name or item.uds_name or f"Tag {tag}"
            display_text = f"TAG {tag}: {display_name} = {item.value}"
            
            self.metadata_list.addItem(display_text)
    
    def set_metadata_loaded(self, loaded: bool):
        """
        Définit si des métadonnées ont été chargées.
        
        Args:
            loaded: True si des métadonnées ont été chargées
        """
        self._metadata_loaded = loaded
    
    def clear(self):
        """Efface l'affichage."""
        self._metadata_loaded = False
        self._show_empty_message()

