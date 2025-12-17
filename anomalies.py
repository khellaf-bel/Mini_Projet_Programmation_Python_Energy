"""
Module anomalies.py
Détecte les anomalies dans la consommation énergétique
Utilise deux critères : seuils fixes et écart-type
"""

from typing import List, Dict, Any, Tuple
import statistics


class DetecteurAnomalies:
    """Détecte les anomalies de consommation énergétique"""
    
    # Seuils fixes par type d'équipement (en kW)
    SEUILS_FIXES = {
        "pompe": 3.2,              # Au-delà de la plage max (3.2)
        "compresseur": 8.0,        # Au-delà de la plage max (7.5)
        "eclairage": 1.7,          # Au-delà de la plage max (1.5)
        "ventilation": 2.2         # Au-delà de la plage max (2.0)
    }
    
    # Multiplicateur d'écart-type pour déterminer une anomalie
    MULTIPLICATEUR_ECART_TYPE = 2.0
    
    def __init__(self):
        """Initialise le détecteur d'anomalies"""
        pass
    
    def detecter_anomalies(self, lectures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Détecte les anomalies dans une liste de lectures
        
        Args:
            lectures: Liste des lectures (avec capteur_id, valeur, type_equipement)
            
        Returns:
            Liste des lectures avec flagging d'anomalie et type d'anomalie
        """
        if not lectures:
            return []
        
        # Grouper les lectures par type d'équipement
        lectures_par_type = self._grouper_par_type(lectures)
        
        # Calculer les statistiques par type
        stats_par_type = {
            type_eq: self._calculer_stats(readings)
            for type_eq, readings in lectures_par_type.items()
        }
        
        # Analyser chaque lecture
        resultats = []
        for lecture in lectures:
            lecture_augmentee = lecture.copy()
            type_eq = lecture.get("type_equipement", "")
            valeur = lecture.get("valeur", 0)
            
            # Vérifier les anomalies
            est_anomalie, type_anomalie = self._analyser_lecture(
                valeur,
                type_eq,
                stats_par_type.get(type_eq, {})
            )
            
            lecture_augmentee["anomalie"] = est_anomalie
            lecture_augmentee["type_anomalie"] = type_anomalie
            resultats.append(lecture_augmentee)
        
        return resultats
    
    def _grouper_par_type(self, lectures: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Groupe les lectures par type d'équipement
        
        Args:
            lectures: Liste des lectures
            
        Returns:
            Dictionnaire {type_equipement: [lectures]}
        """
        groupes = {}
        for lecture in lectures:
            type_eq = lecture.get("type_equipement", "inconnu")
            if type_eq not in groupes:
                groupes[type_eq] = []
            groupes[type_eq].append(lecture)
        return groupes
    
    def _calculer_stats(self, lectures: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcule les statistiques pour un groupe de lectures
        
        Args:
            lectures: Liste des lectures
            
        Returns:
            Dictionnaire avec moyenne, écart-type, min, max
        """
        valeurs = [l.get("valeur", 0) for l in lectures]
        
        if len(valeurs) < 2:
            return {
                "moyenne": valeurs[0] if valeurs else 0,
                "ecart_type": 0,
                "min": min(valeurs) if valeurs else 0,
                "max": max(valeurs) if valeurs else 0
            }
        
        moyenne = statistics.mean(valeurs)
        ecart_type = statistics.stdev(valeurs)
        
        return {
            "moyenne": round(moyenne, 2),
            "ecart_type": round(ecart_type, 2),
            "min": min(valeurs),
            "max": max(valeurs)
        }
    
    def _analyser_lecture(self, valeur: float, type_eq: str, stats: Dict[str, float]) -> Tuple[bool, str]:
        """
        Analyse une lecture pour détecter les anomalies
        
        Args:
            valeur: Valeur mesurée (kW)
            type_eq: Type d'équipement
            stats: Statistiques du type d'équipement
            
        Returns:
            Tuple (est_anomalie: bool, type_anomalie: str)
        """
        est_anomalie = False
        types_anomalie = []
        
        # Critère 1 : Seuil fixe
        seuil = self.SEUILS_FIXES.get(type_eq)
        if seuil and valeur > seuil:
            est_anomalie = True
            types_anomalie.append("dépassement_seuil")
        
        # Critère 2 : Écart-type
        if stats and "moyenne" in stats and "ecart_type" in stats:
            moyenne = stats["moyenne"]
            ecart_type = stats["ecart_type"]
            
            # Éviter la division par zéro
            if ecart_type > 0:
                limite_sup = moyenne + (self.MULTIPLICATEUR_ECART_TYPE * ecart_type)
                limite_inf = moyenne - (self.MULTIPLICATEUR_ECART_TYPE * ecart_type)
                
                if valeur > limite_sup or valeur < limite_inf:
                    est_anomalie = True
                    if valeur > limite_sup:
                        types_anomalie.append("écart_type_élevé")
                    else:
                        types_anomalie.append("écart_type_faible")
        
        # Formater le type d'anomalie
        type_anomalie = " + ".join(types_anomalie) if types_anomalie else "aucune"
        
        return est_anomalie, type_anomalie
    
    def obtenir_anomalies(self, lectures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Retourne uniquement les anomalies détectées
        
        Args:
            lectures: Liste des lectures analysées
            
        Returns:
            Liste des lectures marquées comme anomalies
        """
        return [l for l in lectures if l.get("anomalie", False)]
    
    def rapport_anomalies(self, lectures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un rapport sur les anomalies
        
        Args:
            lectures: Liste des lectures analysées
            
        Returns:
            Dictionnaire avec statistiques sur les anomalies
        """
        anomalies = self.obtenir_anomalies(lectures)
        
        if not anomalies:
            return {
                "nombre_total": len(lectures),
                "nombre_anomalies": 0,
                "pourcentage_anomalies": 0.0,
                "anomalies_par_type": {},
                "anomalies_par_capteur": {},
                "types_anomalies": {}
            }
        
        # Grouper par type d'équipement
        anomalies_par_type = {}
        for anomalie in anomalies:
            type_eq = anomalie.get("type_equipement", "inconnu")
            if type_eq not in anomalies_par_type:
                anomalies_par_type[type_eq] = []
            anomalies_par_type[type_eq].append(anomalie)
        
        # Grouper par capteur
        anomalies_par_capteur = {}
        for anomalie in anomalies:
            capteur_id = anomalie.get("capteur_id", "inconnu")
            if capteur_id not in anomalies_par_capteur:
                anomalies_par_capteur[capteur_id] = []
            anomalies_par_capteur[capteur_id].append(anomalie)
        
        # Compter les types d'anomalies
        types_anomalies = {}
        for anomalie in anomalies:
            type_anom = anomalie.get("type_anomalie", "aucune")
            types_anomalies[type_anom] = types_anomalies.get(type_anom, 0) + 1
        
        pourcentage = (len(anomalies) / len(lectures) * 100) if lectures else 0
        
        return {
            "nombre_total": len(lectures),
            "nombre_anomalies": len(anomalies),
            "pourcentage_anomalies": round(pourcentage, 2),
            "anomalies_par_type": {k: len(v) for k, v in anomalies_par_type.items()},
            "anomalies_par_capteur": {k: len(v) for k, v in anomalies_par_capteur.items()},
            "types_anomalies": types_anomalies
        }
    
    def afficher_rapport(self, lectures: List[Dict[str, Any]]) -> None:
        """
        Affiche un rapport formaté des anomalies
        
        Args:
            lectures: Liste des lectures analysées
        """
        rapport = self.rapport_anomalies(lectures)
        
        print("\n" + "=" * 70)
        print("📊 RAPPORT D'ANOMALIES")
        print("=" * 70)
        
        print(f"\n📈 Résumé général :")
        print(f"  • Total lectures : {rapport['nombre_total']}")
        print(f"  • Anomalies détectées : {rapport['nombre_anomalies']}")
        print(f"  • Pourcentage : {rapport['pourcentage_anomalies']}%")
        
        if rapport['anomalies_par_type']:
            print(f"\n🏭 Anomalies par type d'équipement :")
            for type_eq, count in rapport['anomalies_par_type'].items():
                print(f"  • {type_eq:<15} : {count} anomalies")
        
        if rapport['anomalies_par_capteur']:
            print(f"\n📡 Anomalies par capteur :")
            for capteur_id, count in rapport['anomalies_par_capteur'].items():
                print(f"  • {capteur_id:<20} : {count} anomalies")
        
        if rapport['types_anomalies']:
            print(f"\n⚠️  Types d'anomalies :")
            for type_anom, count in rapport['types_anomalies'].items():
                print(f"  • {type_anom:<30} : {count} fois")
        
        print("\n" + "=" * 70 + "\n")
    
    def __repr__(self) -> str:
        return f"DetecteurAnomalies(seuils={self.SEUILS_FIXES})"
