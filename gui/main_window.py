"""
Module : gui/main_window.py
Description : Fenêtre principale de l'application
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QFileDialog, QMessageBox, QProgressDialog,
                               QLabel, QStatusBar)
from PySide6.QtCore import Qt, QThread, Signal
from gui.video_player import VideoPlayer
from gui.metadata_panel import MetadataPanel
from services.klv_extractor import KLVExtractor
from services.metadata_manager import MetadataManager
from services.csv_exporter import CSVExporter
from models.metadata import MetadataCollection
from models.video import VideoInfo

logger = logging.getLogger(__name__)


class ExtractionThread(QThread):
    """
    Thread pour l'extraction des métadonnées (évite de bloquer l'UI).
    """
    
    finished = Signal(object, object)  # MetadataCollection, VideoInfo
    error = Signal(str)
    progress = Signal(str, int)  # Message de progression, pourcentage (0-100)
    
    def __init__(self, video_path: str):
        """
        Initialise le thread d'extraction.
        
        Args:
            video_path: Chemin du fichier vidéo
        """
        super().__init__()
        self.video_path = video_path
        self.extractor = KLVExtractor()
    
    def run(self):
        """Exécute l'extraction dans le thread."""
        try:
            self.progress.emit("Lecture du fichier MPEG-TS...", 10)
            packets = self.extractor.extract_from_mpegts(self.video_path)
            
            self.progress.emit("Analyse des métadonnées KLV...", 80)
            
            if not packets:
                self.error.emit("Aucune métadonnée KLV trouvée dans la vidéo.\n\n"
                              "Cette vidéo ne contient pas de métadonnées KLV (MISB 601) "
                              "conformes à STANAG 4609.\n\n"
                              "Seuls les fichiers MPEG-TS avec métadonnées KLV embarquées "
                              "peuvent être analysés.")
                return
            
            self.progress.emit("Création de la collection...", 90)
            video_info = VideoInfo.from_path(self.video_path)
            video_info.has_klv = True
            
            collection = MetadataCollection(
                packets=packets,
                video_path=self.video_path,
                total_packets=len(packets)
            )
            
            self.progress.emit("Terminé", 100)
            self.finished.emit(collection, video_info)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction: {e}", exc_info=True)
            self.error.emit(f"Erreur lors de l'extraction: {str(e)}")


class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application.
    """
    
    def __init__(self):
        """Initialise la fenêtre principale."""
        super().__init__()
        self._metadata_manager = MetadataManager()
        self._extraction_thread = None
        self._init_ui()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure le logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _init_ui(self):
        """Initialise l'interface utilisateur."""
        self.setWindowTitle("KLV Over MPEG-TS Extractor")
        self.setMinimumSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Barre d'outils
        toolbar_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Ouvrir vidéo")
        self.open_button.clicked.connect(self._open_video)
        toolbar_layout.addWidget(self.open_button)
        
        self.analyze_button = QPushButton("Analyser métadonnées")
        self.analyze_button.clicked.connect(self._analyze_video)
        self.analyze_button.setEnabled(False)
        toolbar_layout.addWidget(self.analyze_button)
        
        self.export_button = QPushButton("Exporter CSV")
        self.export_button.clicked.connect(self._export_csv)
        self.export_button.setEnabled(False)
        toolbar_layout.addWidget(self.export_button)
        
        toolbar_layout.addStretch()
        
        self.video_path_label = QLabel("Aucune vidéo chargée")
        toolbar_layout.addWidget(self.video_path_label)
        
        main_layout.addLayout(toolbar_layout)
        
        # Lecteur vidéo
        self.video_player = VideoPlayer()
        self.video_player.position_changed.connect(self._on_video_position_changed)
        main_layout.addWidget(self.video_player)
        
        # Panel métadonnées
        self.metadata_panel = MetadataPanel()
        main_layout.addWidget(self.metadata_panel)
        
        # Barre de statut
        self.statusBar().showMessage("Prêt")
    
    def _open_video(self):
        """Ouvre un fichier vidéo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir une vidéo",
            "",
            "Fichiers MPEG-TS (*.m2ts *.ts);;Tous les fichiers (*)"
        )
        
        if file_path:
            # Vérifier l'extension et avertir si format non standard
            path_obj = Path(file_path)
            if path_obj.suffix.lower() not in ['.m2ts', '.ts']:
                reply = QMessageBox.question(
                    self,
                    "Format de fichier",
                    f"Le fichier sélectionné ({path_obj.suffix}) n'est pas un format MPEG-TS standard.\n\n"
                    "Cette application est conçue pour les fichiers MPEG-TS (.m2ts, .ts) "
                    "contenant des métadonnées KLV conformes à STANAG 4609.\n\n"
                    "Les fichiers .mp4 ou autres formats peuvent ne pas contenir de métadonnées KLV.\n\n"
                    "Voulez-vous continuer quand même ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self._load_video(file_path)
    
    def _load_video(self, video_path: str):
        """
        Charge une vidéo dans le lecteur.
        
        Args:
            video_path: Chemin du fichier vidéo
        """
        if self.video_player.load_video(video_path):
            self.video_path_label.setText(Path(video_path).name)
            self.analyze_button.setEnabled(True)
            self._metadata_manager.clear()
            self.metadata_panel.clear()
            self.metadata_panel.set_metadata_loaded(False)
            self.export_button.setEnabled(False)
            self.statusBar().showMessage(f"Vidéo chargée: {Path(video_path).name}")
    
    def _analyze_video(self):
        """Lance l'analyse des métadonnées KLV."""
        video_path = self.video_player._media_player.source().toLocalFile()
        
        if not video_path:
            QMessageBox.warning(self, "Erreur", "Aucune vidéo chargée")
            return
        
        # Désactiver le bouton pendant l'extraction
        self.analyze_button.setEnabled(False)
        
        # Créer la barre de progression
        self._progress_dialog = QProgressDialog("Extraction en cours...", "Annuler", 0, 100, self)
        self._progress_dialog.setWindowTitle("Extraction des métadonnées KLV")
        self._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress_dialog.setMinimumDuration(0)
        self._progress_dialog.setValue(0)
        self._progress_dialog.show()
        
        # Créer et lancer le thread d'extraction
        self._extraction_thread = ExtractionThread(video_path)
        self._extraction_thread.finished.connect(self._on_extraction_finished)
        self._extraction_thread.error.connect(self._on_extraction_error)
        self._extraction_thread.progress.connect(self._update_progress)
        self._extraction_thread.start()
    
    def _on_extraction_finished(self, collection: MetadataCollection, video_info: VideoInfo):
        """
        Appelé quand l'extraction est terminée.
        
        Args:
            collection: Collection de métadonnées
            video_info: Informations vidéo
        """
        # Fermer la barre de progression
        if hasattr(self, '_progress_dialog'):
            self._progress_dialog.close()
            del self._progress_dialog
        
        self._metadata_manager.load_metadata(collection, video_info)
        self.export_button.setEnabled(True)
        self.analyze_button.setEnabled(True)
        
        count = collection.total_packets
        self.statusBar().showMessage(
            f"Extraction terminée: {count} packet(s) de métadonnées trouvé(s)"
        )
        
        # Mettre à jour le panel pour indiquer que les métadonnées sont chargées
        self.metadata_panel.set_metadata_loaded(True)
        
        QMessageBox.information(
            self,
            "Extraction terminée",
            f"{count} packet(s) de métadonnées KLV extrait(s) avec succès."
        )
    
    def _update_progress(self, message: str, value: int):
        """
        Met à jour la barre de progression.
        
        Args:
            message: Message à afficher
            value: Valeur de progression (0-100)
        """
        if hasattr(self, '_progress_dialog'):
            self._progress_dialog.setLabelText(message)
            self._progress_dialog.setValue(value)
        self.statusBar().showMessage(message)
    
    def _on_extraction_error(self, error_message: str):
        """
        Appelé en cas d'erreur lors de l'extraction.
        
        Args:
            error_message: Message d'erreur
        """
        # Fermer la barre de progression
        if hasattr(self, '_progress_dialog'):
            self._progress_dialog.close()
            del self._progress_dialog
        
        self.analyze_button.setEnabled(True)
        self.statusBar().showMessage("Erreur lors de l'extraction")
        
        # Indiquer qu'aucune métadonnée n'a été trouvée
        self.metadata_panel.set_metadata_loaded(False)
        
        QMessageBox.warning(self, "Aucune métadonnée trouvée", error_message)
    
    def _on_video_position_changed(self, time_seconds: float):
        """
        Appelé quand la position vidéo change.
        
        Args:
            time_seconds: Temps en secondes
        """
        if not self._metadata_manager.has_metadata:
            return
        
        # Récupérer les métadonnées pour ce temps
        metadata = self._metadata_manager.get_metadata_at_time(time_seconds)
        self.metadata_panel.update_metadata(metadata, time_seconds)
    
    def _export_csv(self):
        """Exporte les métadonnées en CSV."""
        if not self._metadata_manager.has_metadata:
            QMessageBox.warning(self, "Erreur", "Aucune métadonnée à exporter")
            return
        
        collection = self._metadata_manager.collection
        if not collection:
            return
        
        # Demander le chemin de sortie
        video_path = Path(collection.video_path)
        default_path = video_path.parent / f"{video_path.stem}_metadata.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en CSV",
            str(default_path),
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        
        if file_path:
            exporter = CSVExporter()
            if exporter.export_collection(collection, file_path):
                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"Métadonnées exportées vers:\n{file_path}"
                )
                self.statusBar().showMessage(f"Export réussi: {Path(file_path).name}")
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Erreur lors de l'export CSV"
                )

