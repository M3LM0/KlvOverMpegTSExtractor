"""
Module : services/csv_exporter.py
Description : Service d'export des métadonnées en CSV
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

import csv
import logging
from typing import List
from pathlib import Path
from models.metadata import MetadataCollection, MetadataPacket

logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Service d'export des métadonnées au format CSV.
    """
    
    def __init__(self):
        """Initialise le service d'export."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def export_collection(self, collection: MetadataCollection, output_path: str) -> bool:
        """
        Exporte une collection de métadonnées en CSV.
        
        Args:
            collection: MetadataCollection à exporter
            output_path: Chemin du fichier CSV de sortie
            
        Returns:
            True si succès, False sinon
        """
        self.logger.info(f"Export CSV vers {output_path}")
        
        if not collection or not collection.packets:
            self.logger.warning("Aucune métadonnée à exporter")
            return False
        
        try:
            # Créer le répertoire si nécessaire
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Collecter toutes les clés possibles (tous les tags)
            all_keys = set()
            for packet in collection.packets:
                packet_dict = packet.to_dict()
                all_keys.update(packet_dict.keys())
            
            # Trier les clés : timestamp d'abord, puis par tag
            sorted_keys = sorted(all_keys, key=self._sort_key)
            
            # Écrire le CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=sorted_keys)
                writer.writeheader()
                
                for packet in collection.packets:
                    packet_dict = packet.to_dict()
                    # Remplir les valeurs manquantes avec des chaînes vides
                    row = {key: packet_dict.get(key, '') for key in sorted_keys}
                    writer.writerow(row)
            
            self.logger.info(f"Export réussi: {len(collection.packets)} lignes écrites")
            return True
            
        except IOError as e:
            self.logger.error(f"Erreur d'écriture: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            return False
    
    def _sort_key(self, key: str) -> tuple:
        """
        Fonction de tri pour les colonnes CSV.
        Priorité: timestamp, puis tags numériques.
        
        Args:
            key: Nom de la colonne
            
        Returns:
            Tuple pour le tri
        """
        # Colonnes de timestamp en premier
        if key in ['time_formatted', 'time_seconds', 'pts']:
            priority = 0
            if key == 'time_formatted':
                sub_priority = 0
            elif key == 'time_seconds':
                sub_priority = 1
            else:
                sub_priority = 2
            return (priority, sub_priority, key)
        
        # Tags ensuite
        if key.startswith('TAG_'):
            try:
                tag_num = int(key.split('_')[1])
                return (1, tag_num, key)
            except (ValueError, IndexError):
                return (2, 0, key)
        
        # Autres colonnes à la fin
        return (3, 0, key)
    
    def export_packets(self, packets: List[MetadataPacket], output_path: str) -> bool:
        """
        Exporte une liste de packets en CSV.
        
        Args:
            packets: Liste de MetadataPacket
            output_path: Chemin du fichier CSV de sortie
            
        Returns:
            True si succès, False sinon
        """
        # Créer une collection temporaire
        from models.metadata import MetadataCollection
        collection = MetadataCollection(
            packets=packets,
            video_path="",
            total_packets=len(packets)
        )
        
        return self.export_collection(collection, output_path)

