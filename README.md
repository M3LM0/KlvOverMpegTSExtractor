# KLV Over MPEG-TS Extractor

Application PySide6 pour extraire, visualiser et exporter les métadonnées KLV (MISB 601) depuis des fichiers vidéo MPEG-TS conformes à STANAG 4609.

## Documentation

Voir [Docs/README.md](Docs/README.md) pour le guide d'utilisation complet.

Voir [Docs/architecture.md](Docs/architecture.md) pour l'architecture détaillée.

## Installation rapide

```bash
pip install -r requirements.txt
python main.py
```

## Utilisation CLI (ancien)

Le CLI original est toujours disponible via `run.py` :

```bash
# Pour un fichier MPEG-TS
python run.py -f video.ts

# Pour un fichier KLV binaire
python run.py -f video.klv -k
```

## Credit

KLV Data est adapté de https://github.com/paretech/klvdata.

Les modifications incluent :
* Ignore errors (write -1000 or -2000 as value).
* Output readable value when printing structure.
* Adding CRC validation to packet.
