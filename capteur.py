from datetime import datetime
from typing import Dict, Any
import random


class Lecture:
    """Représente une lecture individuelle d'un capteur"""
    
    def __init__(self, capteur_id: str, valeur: float, unite: str = "kWh"):
        """
        Initialise une lecture
        
        Args:
            capteur_id: Identifiant unique du capteur
            valeur: Valeur mesurée
            unite: Unité de mesure (par défaut kWh)
        """
        self.capteur_id = capteur_id
        self.valeur = valeur
        self.unite = unite
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la lecture en dictionnaire pour MongoDB"""
        return {
            "capteur_id": self.capteur_id,
            "valeur": round(self.valeur, 2),
            "unite": self.unite,
            "timestamp": self.timestamp
        }
    
    def __repr__(self) -> str:
        return (f"Lecture(capteur_id={self.capteur_id}, "
                f"valeur={self.valeur:.2f} {self.unite}, "
                f"timestamp={self.timestamp})")


class Capteur:
    """Représente un capteur IoT pour mesurer la consommation énergétique"""
    
    # Plages de consommation réalistes pour chaque type d'équipement (en kW)
    PLAGES_CONSOMMATION = {
        "pompe": (0.5, 3.0),
        "compresseur": (2.0, 7.5),
        "eclairage": (0.2, 1.5),
        "ventilation": (0.3, 2.0)
    }
    
    def __init__(self, capteur_id: str, type_equipement: str, localisation: str):
        """
        Initialise un capteur
        
        Args:
            capteur_id: Identifiant unique du capteur
            type_equipement: Type d'équipement (pompe, compresseur, etc.)
            localisation: Localisation dans l'usine
            
        Raises:
            ValueError: Si le type d'équipement est invalide
        """
        if type_equipement not in self.PLAGES_CONSOMMATION:
            raise ValueError(f"Type d'équipement invalide: {type_equipement}")
        
        self.capteur_id = capteur_id
        self.type_equipement = type_equipement
        self.localisation = localisation
        self.actif = True
    
    def generer_lecture(self) -> Lecture:
        """
        Génère une lecture aléatoire réaliste
        
        Returns:
            Lecture: Une nouvelle lecture du capteur
        """
        if not self.actif:
            valeur = 0.0
        else:
            min_val, max_val = self.PLAGES_CONSOMMATION[self.type_equipement]
            # Génère une valeur réaliste avec variation normale
            valeur = random.uniform(min_val, max_val)
        
        return Lecture(self.capteur_id, valeur, "kW")
    
    def get_info(self) -> Dict[str, str]:
        """Retourne les informations du capteur"""
        return {
            "capteur_id": self.capteur_id,
            "type_equipement": self.type_equipement,
            "localisation": self.localisation,
            "actif": self.actif
        }
    
    def __repr__(self) -> str:
        return (f"Capteur(id={self.capteur_id}, "
                f"type={self.type_equipement}, "
                f"localisation={self.localisation})")