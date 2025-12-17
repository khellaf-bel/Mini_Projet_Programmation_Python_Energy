"""
Module base_donnees.py
Gère le stockage et la lecture des données dans un fichier JSON
(Simule une base de données)
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseDonnees:
    """Gère le stockage des données dans un fichier JSON"""
    
    def __init__(self, nom_fichier: str = "donnees_capteurs.json"):
        """
        Initialise la base de données
        
        Args:
            nom_fichier: Nom du fichier JSON (chemin relatif ou absolu)
        """
        self.chemin_fichier = Path(nom_fichier)
        self.initialiser_fichier()
    
    def initialiser_fichier(self) -> None:
        """Crée le fichier JSON s'il n'existe pas"""
        if not self.chemin_fichier.exists():
            self.sauvegarder([])
    
    def sauvegarder(self, donnees: List[Dict[str, Any]]) -> None:
        """
        Sauvegarde les données dans le fichier JSON
        
        Args:
            donnees: Liste des lectures à sauvegarder
        """
        try:
            with open(self.chemin_fichier, 'w', encoding='utf-8') as f:
                json.dump(donnees, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Erreur lors de la sauvegarde : {e}")
    
    def charger(self) -> List[Dict[str, Any]]:
        """
        Charge les données depuis le fichier JSON
        
        Returns:
            Liste des lectures stockées
        """
        try:
            with open(self.chemin_fichier, 'r', encoding='utf-8') as f:
                donnees = json.load(f)
                return donnees if isinstance(donnees, list) else []
        except (IOError, json.JSONDecodeError) as e:
            raise IOError(f"Erreur lors de la lecture : {e}")
    
    def inserer(self, lecture: Dict[str, Any]) -> None:
        """
        Insère une nouvelle lecture
        
        Args:
            lecture: Dictionnaire représentant une lecture
        """
        donnees = self.charger()
        donnees.append(lecture)
        self.sauvegarder(donnees)
    
    def inserer_multiple(self, lectures: List[Dict[str, Any]]) -> None:
        """
        Insère plusieurs lectures
        
        Args:
            lectures: Liste de lectures à insérer
        """
        donnees = self.charger()
        donnees.extend(lectures)
        self.sauvegarder(donnees)
    
    def obtenir_tous(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les lectures
        
        Returns:
            Liste de toutes les lectures
        """
        return self.charger()
    
    def obtenir_par_capteur(self, capteur_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les lectures d'un capteur spécifique
        
        Args:
            capteur_id: ID du capteur
            
        Returns:
            Liste des lectures du capteur
        """
        donnees = self.charger()
        return [d for d in donnees if d.get("capteur_id") == capteur_id]
    
    def obtenir_par_type(self, type_equipement: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les lectures d'un type d'équipement
        
        Args:
            type_equipement: Type d'équipement (pompe, compresseur, etc.)
            
        Returns:
            Liste des lectures du type
        """
        donnees = self.charger()
        return [d for d in donnees if d.get("type_equipement") == type_equipement]
    
    def obtenir_dernieres(self, nombre: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les N dernières lectures
        
        Args:
            nombre: Nombre de lectures à récupérer
            
        Returns:
            Liste des dernières lectures
        """
        donnees = self.charger()
        return donnees[-nombre:] if len(donnees) >= nombre else donnees
    
    def filtrer_par_periode(self, date_debut: str, date_fin: str) -> List[Dict[str, Any]]:
        """
        Récupère les lectures dans une période (format ISO)
        
        Args:
            date_debut: Date de début (format ISO: YYYY-MM-DDTHH:MM:SS)
            date_fin: Date de fin (format ISO)
            
        Returns:
            Liste des lectures dans la période
        """
        donnees = self.charger()
        resultats = []
        
        for lecture in donnees:
            timestamp = lecture.get("timestamp", "")
            if date_debut <= timestamp <= date_fin:
                resultats.append(lecture)
        
        return resultats
    
    def statistiques(self, capteur_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calcule les statistiques des lectures
        
        Args:
            capteur_id: ID du capteur (optionnel, sinon toutes les lectures)
            
        Returns:
            Dictionnaire avec min, max, moyenne, écart-type
        """
        if capteur_id:
            donnees = self.obtenir_par_capteur(capteur_id)
        else:
            donnees = self.charger()
        
        if not donnees:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "moyenne": None,
                "ecart_type": None
            }
        
        valeurs = [d.get("valeur", 0) for d in donnees]
        
        # Calcul moyenne
        moyenne = sum(valeurs) / len(valeurs)
        
        # Calcul écart-type
        variance = sum((v - moyenne) ** 2 for v in valeurs) / len(valeurs)
        ecart_type = variance ** 0.5
        
        return {
            "count": len(donnees),
            "min": min(valeurs),
            "max": max(valeurs),
            "moyenne": round(moyenne, 2),
            "ecart_type": round(ecart_type, 2)
        }
    
    def supprimer_tous(self) -> None:
        """Vide complètement la base de données"""
        self.sauvegarder([])
    
    def supprimer_par_capteur(self, capteur_id: str) -> int:
        """
        Supprime toutes les lectures d'un capteur
        
        Args:
            capteur_id: ID du capteur
            
        Returns:
            Nombre de lectures supprimées
        """
        donnees = self.charger()
        avant = len(donnees)
        donnees = [d for d in donnees if d.get("capteur_id") != capteur_id]
        apres = len(donnees)
        self.sauvegarder(donnees)
        return avant - apres
    
    def compter(self) -> int:
        """
        Compte le nombre total de lectures
        
        Returns:
            Nombre total de lectures
        """
        return len(self.charger())
    
    def exporter_csv(self, nom_fichier: str = "donnees_capteurs.csv") -> None:
        """
        Exporte les données en format CSV
        
        Args:
            nom_fichier: Nom du fichier CSV
        """
        import csv
        donnees = self.charger()
        
        if not donnees:
            print("Aucune donnée à exporter")
            return
        
        try:
            with open(nom_fichier, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=donnees[0].keys())
                writer.writeheader()
                writer.writerows(donnees)
            print(f"✅ Données exportées vers {nom_fichier}")
        except IOError as e:
            raise IOError(f"Erreur lors de l'export CSV : {e}")
    
    def obtenir_info(self) -> Dict[str, Any]:
        """Retourne les informations sur la base de données"""
        donnees = self.charger()
        capteurs_uniques = set(d.get("capteur_id") for d in donnees)
        
        return {
            "chemin": str(self.chemin_fichier),
            "nombre_lectures": len(donnees),
            "nombre_capteurs_uniques": len(capteurs_uniques),
            "taille_fichier": self.chemin_fichier.stat().st_size if self.chemin_fichier.exists() else 0
        }
    
    def __repr__(self) -> str:
        info = self.obtenir_info()
        return (f"BaseDonnees(fichier={info['chemin']}, "
                f"lectures={info['nombre_lectures']}, "
                f"capteurs={info['nombre_capteurs_uniques']})")
