# KLV Over MPEG-TS Extractor - Application GUI

Application PySide6 pour extraire, visualiser et exporter les métadonnées KLV (MISB 601) depuis des fichiers vidéo MPEG-TS conformes à STANAG 4609.

## Fonctionnalités

- **Extraction automatique** : Extraction des métadonnées KLV depuis les fichiers `.m2ts` et `.ts`
- **Lecteur vidéo intégré** : Visualisation de la vidéo avec contrôles de lecture
- **Synchronisation temps réel** : Affichage des métadonnées synchronisé avec la timeline vidéo
- **Export CSV** : Export des métadonnées au format CSV pour analyse externe
- **Interface intuitive** : Interface graphique simple et claire

## Installation

### Prérequis

- Python 3.9 ou supérieur
- Environnement virtuel (recommandé)

### Étapes d'installation

1. Cloner le dépôt (ou utiliser le projet existant)

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

### Lancement de l'application GUI

```bash
python main.py
```

### Workflow

1. **Ouvrir une vidéo** : Cliquer sur "Ouvrir vidéo" et sélectionner un fichier `.m2ts` ou `.ts`

2. **Analyser les métadonnées** : Cliquer sur "Analyser métadonnées" pour extraire les métadonnées KLV

3. **Visualiser** : 
   - Lire la vidéo avec les contrôles
   - Les métadonnées s'affichent automatiquement en dessous, synchronisées avec la timeline
   - Déplacer la barre de progression pour voir les métadonnées à différents moments

4. **Exporter** : Cliquer sur "Exporter CSV" pour sauvegarder les métadonnées dans un fichier CSV

### Utilisation en ligne de commande (CLI)

L'ancien CLI est toujours disponible :

```bash
# Pour un fichier MPEG-TS
python run.py -f video.ts

# Pour un fichier KLV binaire
python run.py -f video.klv -k
```

## Structure du projet

Voir [architecture.md](architecture.md) pour les détails de l'architecture.

## Format CSV

Le fichier CSV exporté contient :
- `time_formatted` : Temps formaté (HH:MM:SS.mmm)
- `time_seconds` : Temps en secondes
- `pts` : Presentation Time Stamp
- `TAG_X` : Valeur de la métadonnée avec tag X
- `TAG_X_LDSName`, `TAG_X_ESDName`, `TAG_X_UDSName` : Noms des métadonnées

## Standards supportés

- **STANAG 4609** : Format d'échange OTAN pour imagerie numérique
- **SMPTE ST 336** : Format KLV (Key-Length-Value)
- **MISB ST 0601** : Standard de métadonnées UAS (UAS Datalink Local Set)

## Dépannage

### Le lecteur vidéo ne charge pas la vidéo

- Vérifier que le fichier est un format MPEG-TS valide (`.m2ts`, `.ts`)
- Certains codecs peuvent nécessiter des plugins supplémentaires pour PySide6

### Aucune métadonnée trouvée

- Vérifier que la vidéo contient bien des métadonnées KLV
- Tester avec `run.py` en ligne de commande pour voir les messages de debug

### Erreurs d'extraction

- Vérifier les logs dans la console
- S'assurer que le fichier n'est pas corrompu
- Vérifier les permissions de lecture du fichier

## Développement

Voir [architecture.md](architecture.md) pour l'architecture et les patterns utilisés.

## Licence

Voir le fichier LICENSE du projet original.

