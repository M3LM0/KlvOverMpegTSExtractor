"""
Module : utils/time_utils.py
Description : Conversion PTS vers temps vidéo pour synchronisation
Auteur : Mounir Elmaddaghri
Date : 2025-01-XX
"""

# Fréquence PTS standard MPEG-TS (90 kHz)
PTS_FREQUENCY = 90000.0  # Hz
PTS_MAX = 8589934592  # Maximum pour 33 bits


def pts_to_seconds(pts: int) -> float:
    """
    Convertit un PTS (33 bits) en secondes.
    
    Args:
        pts: Presentation Time Stamp en unités de 1/90000 seconde
        
    Returns:
        Temps en secondes (float) ou None si pts est None
    """
    if pts is None:
        return None
    return pts / PTS_FREQUENCY


def pts_to_timedelta(pts: int, base_pts: int = 0) -> float:
    """
    Convertit un PTS en temps relatif depuis un PTS de base.
    Gère les wraparounds (dépassement 33 bits).
    
    Args:
        pts: PTS actuel
        base_pts: PTS de référence (premier PTS généralement)
        
    Returns:
        Temps relatif en secondes ou None si pts/base_pts est None
    """
    if pts is None or base_pts is None:
        return None
    
    # Gestion du wraparound (33 bits = 8589934592)
    if pts < base_pts:
        # Wraparound détecté
        diff = (PTS_MAX - base_pts) + pts
    else:
        diff = pts - base_pts
    
    return diff / PTS_FREQUENCY


def format_time(seconds: float) -> str:
    """
    Formate un temps en secondes au format HH:MM:SS.mmm
    
    Args:
        seconds: Temps en secondes
        
    Returns:
        Chaîne formatée (ex: "00:02:17.174")
    """
    if seconds is None:
        return "00:00:00.000"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    whole_secs = int(secs)
    milliseconds = int((secs - whole_secs) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{whole_secs:02d}.{milliseconds:03d}"


def find_metadata_for_time(metadata_list: list, target_time: float) -> dict:
    """
    Trouve les métadonnées correspondant à un temps vidéo donné.
    Utilise l'interpolation si nécessaire.
    
    Args:
        metadata_list: Liste de dicts avec 'time_seconds' et 'metadata'
        target_time: Temps vidéo en secondes
        
    Returns:
        Dict des métadonnées ou None si aucune trouvée
    """
    if not metadata_list:
        return None
    
    # Recherche linéaire (optimisable avec recherche binaire si liste triée)
    for i, item in enumerate(metadata_list):
        if item.get('time_seconds') is None:
            continue
            
        if item['time_seconds'] >= target_time:
            # Trouvé : retourner cette métadonnée ou interpoler
            if i == 0:
                return item.get('metadata')
            
            # Interpolation entre item précédent et actuel
            prev_item = metadata_list[i - 1]
            prev_time = prev_item.get('time_seconds')
            
            if prev_time is not None:
                if target_time - prev_time < item['time_seconds'] - target_time:
                    return prev_item.get('metadata')
            
            return item.get('metadata')
    
    # Si après la dernière métadonnée, retourner la dernière
    return metadata_list[-1].get('metadata')

