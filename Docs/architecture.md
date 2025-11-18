# Architecture de l'application KLV Over MPEG-TS Extractor

## Vue d'ensemble

Application GUI PySide6 pour extraire, visualiser et exporter les métadonnées KLV (MISB 601) depuis des fichiers vidéo MPEG-TS (.m2ts, .ts) conformes à STANAG 4609.

## Structure du projet

```
project/
├── main.py                 # Point d'entrée GUI
├── run.py                  # CLI existant (conservé pour compatibilité)
├── models/                 # Modèles de données (dataclasses)
│   ├── metadata.py        # MetadataPacket, MetadataCollection
│   └── video.py           # VideoInfo
├── services/              # Logique métier
│   ├── klv_extractor.py  # Extraction KLV depuis MPEG-TS
│   ├── metadata_manager.py # Gestion métadonnées en mémoire
│   └── csv_exporter.py    # Export CSV
├── gui/                   # Interface graphique PySide6
│   ├── main_window.py     # Fenêtre principale
│   ├── video_player.py    # Widget lecteur vidéo
│   └── metadata_panel.py  # Panel affichage métadonnées
├── utils/                 # Fonctions utilitaires
│   └── time_utils.py      # Conversion PTS → temps vidéo
├── tests/                 # Tests unitaires
├── Docs/                  # Documentation
└── klvdata/               # Modules existants (non modifiés)
```

## Flux de données

### 1. Extraction des métadonnées

```
Fichier .m2ts
    ↓
services/klv_extractor.py
    ↓
Extraction MPEG-TS → Reconstruction KLV → Parsing MISB 601
    ↓
Liste de MetadataPacket (avec PTS)
    ↓
Conversion PTS → temps (utils/time_utils.py)
    ↓
MetadataCollection (préchargée en mémoire)
```

### 2. Affichage et synchronisation

```
Lecteur vidéo (PySide6)
    ↓
Position vidéo (ms) → temps (secondes)
    ↓
MetadataCollection.get_metadata_at_time()
    ↓
Affichage dans metadata_panel
```

### 3. Export CSV

```
MetadataCollection
    ↓
services/csv_exporter.py
    ↓
Conversion MetadataPacket → dict
    ↓
Fichier CSV
```

## Technologies

- **Python 3.9+**
- **PySide6** : Interface graphique
- **Standards** : STANAG 4609, SMPTE ST 336, MISB ST 0601

## Décisions techniques

### Synchronisation vidéo/métadonnées

- Utilisation des PTS (Presentation Time Stamp) extraits des packets MPEG-TS
- Conversion PTS (90 kHz) → secondes
- Gestion des wraparounds (33 bits)
- Interpolation entre packets si nécessaire

### Gestion mémoire

- Préchargement complet des métadonnées en mémoire
- Structure optimisée pour recherche rapide par temps
- Estimation : ~1-10 MB de métadonnées pour une vidéo de 600 MB

### Format CSV

- Une ligne par packet KLV
- Colonnes : `time_formatted`, `time_seconds`, `pts`, puis `TAG_X`, `TAG_X_LDSName`, etc.
- Encodage UTF-8

## Patterns utilisés

- **Dataclasses** : Modélisation des données
- **Services** : Logique métier isolée
- **Composition** : Préférée à l'héritage
- **Injection de dépendances** : Services indépendants

