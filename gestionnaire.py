from typing import List, Dict, Any
from capteur import Capteur, Lecture


class GestionnaireCapteurs:
    """Gère l'ensemble des capteurs de l'unité de traitement"""
    
    def __init__(self):
        """Initialise le gestionnaire de capteurs"""
        self.capteurs: Dict[str, Capteur] = {}
        self.historique_lectures: List[Lecture] = []
    
    def ajouter_capteur(self, capteur: Capteur) -> None:
        """
        Ajoute un capteur au gestionnaire
        
        Args:
            capteur: Instance de Capteur à ajouter
            
        Raises:
            ValueError: Si l'ID du capteur existe déjà
        """
        if capteur.capteur_id in self.capteurs:
            raise ValueError(f"Un capteur avec l'ID {capteur.capteur_id} existe déjà")
        self.capteurs[capteur.capteur_id] = capteur
    
    def retirer_capteur(self, capteur_id: str) -> None:
        """
        Retire un capteur du gestionnaire
        
        Args:
            capteur_id: ID du capteur à retirer
            
        Raises:
            KeyError: Si le capteur n'existe pas
        """
        if capteur_id not in self.capteurs:
            raise KeyError(f"Capteur avec l'ID {capteur_id} non trouvé")
        del self.capteurs[capteur_id]
    
    def lire_tous_les_capteurs(self) -> List[Lecture]:
        """
        Lit tous les capteurs et retourne les lectures
        
        Returns:
            Liste de Lecture pour chaque capteur
        """
        lectures = []
        for capteur in self.capteurs.values():
            lecture = capteur.generer_lecture()
            lectures.append(lecture)
            self.historique_lectures.append(lecture)
        return lectures
    
    def lire_capteur(self, capteur_id: str) -> Lecture:
        """
        Lit un capteur spécifique
        
        Args:
            capteur_id: ID du capteur à lire
            
        Returns:
            Lecture du capteur
            
        Raises:
            KeyError: Si le capteur n'existe pas
        """
        if capteur_id not in self.capteurs:
            raise KeyError(f"Capteur avec l'ID {capteur_id} non trouvé")
        
        lecture = self.capteurs[capteur_id].generer_lecture()
        self.historique_lectures.append(lecture)
        return lecture
    
    def obtenir_info_capteur(self, capteur_id: str) -> Dict[str, str]:
        """
        Obtient les informations d'un capteur
        
        Args:
            capteur_id: ID du capteur
            
        Returns:
            Dictionnaire avec les informations du capteur
        """
        if capteur_id not in self.capteurs:
            raise KeyError(f"Capteur avec l'ID {capteur_id} non trouvé")
        return self.capteurs[capteur_id].get_info()
    
    def lister_capteurs(self) -> List[Dict[str, str]]:
        """
        Liste tous les capteurs et leurs informations
        
        Returns:
            Liste de dictionnaires avec les infos de chaque capteur
        """
        return [capteur.get_info() for capteur in self.capteurs.values()]
    
    def obtenir_historique(self) -> List[Dict[str, Any]]:
        """
        Retourne l'historique des lectures sous forme de dictionnaire
        (prêt pour MongoDB)
        
        Returns:
            Liste de dictionnaires représentant les lectures
        """
        return [lecture.to_dict() for lecture in self.historique_lectures]
    
    def obtenir_nombre_capteurs(self) -> int:
        """Retourne le nombre total de capteurs"""
        return len(self.capteurs)
    
    def obtenir_nombre_lectures(self) -> int:
        """Retourne le nombre total de lectures effectuées"""
        return len(self.historique_lectures)
    
    def reinitialiser_historique(self) -> None:
        """Réinitialise l'historique des lectures"""
        self.historique_lectures = []
    
    def __repr__(self) -> str:
        return (f"GestionnaireCapteurs(capteurs={self.obtenir_nombre_capteurs()}, "
                f"lectures={self.obtenir_nombre_lectures()})")