"""
Module : main.py
Description : Point d'entrée de l'application GUI
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Point d'entrée principal de l'application."""
    app = QApplication(sys.argv)
    app.setApplicationName("KLV Over MPEG-TS Extractor")
    
    window = MainWindow()
    window.show()
    
    logger.info("Application démarrée")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

