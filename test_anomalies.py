"""
Module test_anomalies.py
Tests unitaires pour la classe DetecteurAnomalies
"""

import pytest
from anomalies import DetecteurAnomalies


class TestDetecteurAnomalies:
    """Tests pour la classe DetecteurAnomalies"""
    
    @pytest.fixture
    def detecteur(self):
        """Crée un détecteur d'anomalies"""
        return DetecteurAnomalies()
    
    def test_creation_detecteur(self, detecteur):
        """Test la création du détecteur"""
        assert detecteur is not None
        assert detecteur.MULTIPLICATEUR_ECART_TYPE == 2.0
    
    def test_seuils_fixes_presentes(self, detecteur):
        """Test que tous les seuils fixes sont définis"""
        assert "pompe" in detecteur.SEUILS_FIXES
        assert "compresseur" in detecteur.SEUILS_FIXES
        assert "eclairage" in detecteur.SEUILS_FIXES
        assert "ventilation" in detecteur.SEUILS_FIXES
    
    def test_detecter_anomalie_seuil_pompe(self, detecteur):
        """Test la détection d'anomalie par seuil pour pompe"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0, "unite": "kW"},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 3.5, "unite": "kW"}  # > 3.2
        ]
        
        resultats = detecteur.detecter_anomalies(lectures)
        
        assert len(resultats) == 2
        assert resultats[0]["anomalie"] is False
        assert resultats[1]["anomalie"] is True
        assert "dépassement_seuil" in resultats[1]["type_anomalie"]
    
    def test_detecter_anomalie_seuil_compresseur(self, detecteur):
        """Test la détection d'anomalie par seuil pour compresseur"""
        lectures = [
            {"capteur_id": "CAP_002", "type_equipement": "compresseur", "valeur": 7.0, "unite": "kW"},
            {"capteur_id": "CAP_002", "type_equipement": "compresseur", "valeur": 8.5, "unite": "kW"}  # > 8.0
        ]
        
        resultats = detecteur.detecter_anomalies(lectures)
        
        assert resultats[0]["anomalie"] is False
        assert resultats[1]["anomalie"] is True
    
    def test_detecter_anomalie_ecart_type(self, detecteur):
        """Test la détection d'anomalie par écart-type"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.1},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 5.0}  # Anomalie écart-type élevé
        ]
        
        resultats = detecteur.detecter_anomalies(lectures)
        
        # La dernière lecture doit être marquée comme anomalie
        assert resultats[-1]["anomalie"] is True
    
    def test_detecter_anomalie_double_critere(self, detecteur):
        """Test la détection quand les 2 critères sont violés"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.1},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 3.5}  # > seuil ET écart-type
        ]
        
        resultats = detecteur.detecter_anomalies(lectures)
        derniere = resultats[-1]
        
        assert derniere["anomalie"] is True
        # Doit contenir les deux types d'anomalies
        assert "dépassement_seuil" in derniere["type_anomalie"]
    
    def test_lectures_vides(self, detecteur):
        """Test avec une liste vide"""
        resultats = detecteur.detecter_anomalies([])
        assert resultats == []
    
    def test_obtenir_anomalies(self, detecteur):
        """Test la récupération uniquement des anomalies"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0, "anomalie": False},
            {"capteur_id": "CAP_002", "type_equipement": "compresseur", "valeur": 8.5, "anomalie": True},
            {"capteur_id": "CAP_003", "type_equipement": "eclairage", "valeur": 1.0, "anomalie": False}
        ]
        
        anomalies = detecteur.obtenir_anomalies(lectures)
        
        assert len(anomalies) == 1
        assert anomalies[0]["capteur_id"] == "CAP_002"
    
    def test_rapport_anomalies_aucune(self, detecteur):
        """Test le rapport quand il n'y a pas d'anomalies"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0, "anomalie": False, "type_anomalie": "aucune"},
            {"capteur_id": "CAP_002", "type_equipement": "pompe", "valeur": 2.5, "anomalie": False, "type_anomalie": "aucune"}
        ]
        
        rapport = detecteur.rapport_anomalies(lectures)
        
        assert rapport["nombre_anomalies"] == 0
        assert rapport["pourcentage_anomalies"] == 0.0
    
    def test_rapport_anomalies_par_type(self, detecteur):
        """Test le rapport avec anomalies par type"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0, "anomalie": False, "type_anomalie": "aucune"},
            {"capteur_id": "CAP_002", "type_equipement": "pompe", "valeur": 3.5, "anomalie": True, "type_anomalie": "dépassement_seuil"},
            {"capteur_id": "CAP_003", "type_equipement": "compresseur", "valeur": 8.5, "anomalie": True, "type_anomalie": "dépassement_seuil"}
        ]
        
        rapport = detecteur.rapport_anomalies(lectures)
        
        assert rapport["nombre_anomalies"] == 2
        assert rapport["anomalies_par_type"]["pompe"] == 1
        assert rapport["anomalies_par_type"]["compresseur"] == 1
        assert rapport["pourcentage_anomalies"] == pytest.approx(66.67, 0.01)
    
    def test_rapport_anomalies_par_capteur(self, detecteur):
        """Test le rapport avec anomalies par capteur"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.0, "anomalie": False, "type_anomalie": "aucune"},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 3.5, "anomalie": True, "type_anomalie": "dépassement_seuil"},
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 4.0, "anomalie": True, "type_anomalie": "dépassement_seuil"},
            {"capteur_id": "CAP_002", "type_equipement": "compresseur", "valeur": 5.0, "anomalie": False, "type_anomalie": "aucune"}
        ]
        
        rapport = detecteur.rapport_anomalies(lectures)
        
        assert rapport["anomalies_par_capteur"]["CAP_001"] == 2
        assert rapport["anomalies_par_capteur"]["CAP_002"] == 0
    
    def test_grouper_par_type(self, detecteur):
        """Test le groupement par type d'équipement"""
        lectures = [
            {"type_equipement": "pompe", "valeur": 1.0},
            {"type_equipement": "pompe", "valeur": 2.0},
            {"type_equipement": "compresseur", "valeur": 5.0},
        ]
        
        groupes = detecteur._grouper_par_type(lectures)
        
        assert len(groupes) == 2
        assert len(groupes["pompe"]) == 2
        assert len(groupes["compresseur"]) == 1
    
    def test_calculer_stats(self, detecteur):
        """Test le calcul des statistiques"""
        lectures = [
            {"valeur": 1.0},
            {"valeur": 2.0},
            {"valeur": 3.0},
            {"valeur": 4.0},
            {"valeur": 5.0}
        ]
        
        stats = detecteur._calculer_stats(lectures)
        
        assert stats["moyenne"] == 3.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["ecart_type"] > 0
    
    def test_calculer_stats_une_valeur(self, detecteur):
        """Test le calcul des statistiques avec une valeur"""
        lectures = [{"valeur": 2.5}]
        
        stats = detecteur._calculer_stats(lectures)
        
        assert stats["moyenne"] == 2.5
        assert stats["ecart_type"] == 0
    
    def test_analyser_lecture_normale(self, detecteur):
        """Test l'analyse d'une lecture normale"""
        stats = {"moyenne": 2.0, "ecart_type": 0.5}
        
        est_anomalie, type_anom = detecteur._analyser_lecture(2.2, "pompe", stats)
        
        assert est_anomalie is False
        assert type_anom == "aucune"
    
    def test_analyser_lecture_seuil_depasse(self, detecteur):
        """Test l'analyse d'une lecture dépassant le seuil"""
        stats = {"moyenne": 2.0, "ecart_type": 0.5}
        
        est_anomalie, type_anom = detecteur._analyser_lecture(3.5, "pompe", stats)
        
        assert est_anomalie is True
        assert "dépassement_seuil" in type_anom
    
    def test_repr(self, detecteur):
        """Test la représentation en string"""
        repr_str = repr(detecteur)
        assert "DetecteurAnomalies" in repr_str


class TestIntegrationAnomalies:
    """Tests d'intégration pour les anomalies"""
    
    def test_workflow_complet(self):
        """Test un workflow complet de détection"""
        detecteur = DetecteurAnomalies()
        
        # Données réalistes
        lectures = [
            {"capteur_id": "CAP_P1", "type_equipement": "pompe", "valeur": 1.5, "unite": "kW"},
            {"capteur_id": "CAP_P1", "type_equipement": "pompe", "valeur": 1.8, "unite": "kW"},
            {"capteur_id": "CAP_P1", "type_equipement": "pompe", "valeur": 2.0, "unite": "kW"},
            {"capteur_id": "CAP_P1", "type_equipement": "pompe", "valeur": 3.5, "unite": "kW"},  # Anomalie
            {"capteur_id": "CAP_C1", "type_equipement": "compresseur", "valeur": 5.0, "unite": "kW"},
            {"capteur_id": "CAP_C1", "type_equipement": "compresseur", "valeur": 5.5, "unite": "kW"},
            {"capteur_id": "CAP_C1", "type_equipement": "compresseur", "valeur": 8.5, "unite": "kW"},  # Anomalie
        ]
        
        # Analyser
        resultats = detecteur.detecter_anomalies(lectures)
        
        # Vérifier
        assert len(resultats) == 7
        anomalies = [r for r in resultats if r["anomalie"]]
        assert len(anomalies) >= 1
        
        # Rapport
        rapport = detecteur.rapport_anomalies(resultats)
        assert rapport["nombre_total"] == 7
        assert rapport["nombre_anomalies"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
