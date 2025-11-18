"""
Module : gui/video_player.py
Description : Widget lecteur vidéo avec contrôles
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QSlider, QLabel, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QUrl, Signal, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from pathlib import Path


class VideoPlayer(QWidget):
    """
    Widget lecteur vidéo avec contrôles de lecture.
    """
    
    # Signal émis quand la position vidéo change
    position_changed = Signal(float)  # temps en secondes
    
    def __init__(self, parent=None):
        """
        Initialise le lecteur vidéo.
        
        Args:
            parent: Widget parent
        """
        super().__init__(parent)
        self._media_player = None
        self._audio_output = None
        self._video_widget = None
        self._position_timer = QTimer()
        self._position_timer.timeout.connect(self._update_position)
        self._init_ui()
    
    def _init_ui(self):
        """Initialise l'interface utilisateur."""
        layout = QVBoxLayout(self)
        
        # Widget vidéo
        self._video_widget = QVideoWidget()
        layout.addWidget(self._video_widget)
        
        # Contrôles
        controls_layout = QHBoxLayout()
        
        # Boutons de contrôle
        self.play_button = QPushButton("▶")
        self.play_button.clicked.connect(self._toggle_play)
        controls_layout.addWidget(self.play_button)
        
        self.stop_button = QPushButton("⏹")
        self.stop_button.clicked.connect(self._stop)
        controls_layout.addWidget(self.stop_button)
        
        # Slider de position
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self._set_position)
        controls_layout.addWidget(self.position_slider)
        
        # Label temps
        self.time_label = QLabel("00:00:00 / 00:00:00")
        controls_layout.addWidget(self.time_label)
        
        layout.addLayout(controls_layout)
        
        # Initialiser le lecteur média
        self._init_media_player()
    
    def _init_media_player(self):
        """Initialise le lecteur média PySide6."""
        self._audio_output = QAudioOutput()
        self._media_player = QMediaPlayer()
        self._media_player.setAudioOutput(self._audio_output)
        self._media_player.setVideoOutput(self._video_widget)
        
        # Connecter les signaux
        self._media_player.positionChanged.connect(self._on_position_changed)
        self._media_player.durationChanged.connect(self._on_duration_changed)
        self._media_player.playbackStateChanged.connect(self._on_state_changed)
    
    def load_video(self, video_path: str) -> bool:
        """
        Charge une vidéo dans le lecteur.
        
        Args:
            video_path: Chemin du fichier vidéo
            
        Returns:
            True si succès, False sinon
        """
        if not Path(video_path).exists():
            QMessageBox.warning(self, "Erreur", f"Fichier non trouvé: {video_path}")
            return False
        
        url = QUrl.fromLocalFile(video_path)
        self._media_player.setSource(url)
        return True
    
    def _toggle_play(self):
        """Bascule entre lecture et pause."""
        if self._media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._media_player.pause()
        else:
            self._media_player.play()
            self._position_timer.start(100)  # Mise à jour toutes les 100ms
    
    def _stop(self):
        """Arrête la lecture."""
        self._media_player.stop()
        self._position_timer.stop()
        self.position_slider.setValue(0)
    
    def _set_position(self, position: int):
        """
        Définit la position de la vidéo.
        
        Args:
            position: Position en millisecondes
        """
        self._media_player.setPosition(position)
    
    def _on_position_changed(self, position: int):
        """
        Appelé quand la position vidéo change.
        
        Args:
            position: Position en millisecondes
        """
        if self.position_slider.maximum() > 0:
            self.position_slider.setValue(position)
        
        # Émettre le signal avec le temps en secondes
        time_seconds = position / 1000.0
        self.position_changed.emit(time_seconds)
        
        # Mettre à jour le label
        self._update_time_label()
    
    def _on_duration_changed(self, duration: int):
        """
        Appelé quand la durée de la vidéo est connue.
        
        Args:
            duration: Durée en millisecondes
        """
        self.position_slider.setRange(0, duration)
        self._update_time_label()
    
    def _on_state_changed(self, state: QMediaPlayer.PlaybackState):
        """
        Appelé quand l'état de lecture change.
        
        Args:
            state: Nouvel état
        """
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("⏸")
            self._position_timer.start(100)
        else:
            self.play_button.setText("▶")
            self._position_timer.stop()
    
    def _update_position(self):
        """Met à jour la position (appelé par le timer)."""
        # La position est déjà mise à jour par _on_position_changed
        pass
    
    def _update_time_label(self):
        """Met à jour le label de temps."""
        position_ms = self._media_player.position()
        duration_ms = self._media_player.duration()
        
        pos_seconds = position_ms / 1000.0
        dur_seconds = duration_ms / 1000.0 if duration_ms > 0 else 0
        
        from utils.time_utils import format_time
        pos_str = format_time(pos_seconds)
        dur_str = format_time(dur_seconds) if dur_seconds > 0 else "00:00:00"
        
        self.time_label.setText(f"{pos_str} / {dur_str}")
    
    def set_position(self, time_seconds: float):
        """
        Définit la position vidéo depuis un temps en secondes.
        
        Args:
            time_seconds: Temps en secondes
        """
        position_ms = int(time_seconds * 1000)
        self._media_player.setPosition(position_ms)

