import pytest
from datetime import datetime
from capteur import Capteur, Lecture
from gestionnaire import GestionnaireCapteurs


class TestLecture:
    """Tests pour la classe Lecture"""
    
    def test_creation_lecture(self):
        """Test la création d'une lecture"""
        lecture = Lecture("CAP_001", 2.5, "kW")
        assert lecture.capteur_id == "CAP_001"
        assert lecture.valeur == 2.5
        assert lecture.unite == "kW"
    
    def test_lecture_to_dict(self):
        """Test la conversion d'une lecture en dictionnaire"""
        lecture = Lecture("CAP_001", 2.5, "kW")
        dict_lecture = lecture.to_dict()
        
        assert isinstance(dict_lecture, dict)
        assert dict_lecture["capteur_id"] == "CAP_001"
        assert dict_lecture["valeur"] == 2.5
        assert dict_lecture["unite"] == "kW"
        assert "timestamp" in dict_lecture
    
    def test_lecture_timestamp(self):
        """Test que le timestamp est en format ISO"""
        lecture = Lecture("CAP_001", 1.0, "kW")
        # Vérifier que le timestamp peut être parsé
        timestamp = datetime.fromisoformat(lecture.timestamp)
        assert isinstance(timestamp, datetime)
    
    def test_lecture_unite_defaut(self):
        """Test l'unité par défaut"""
        lecture = Lecture("CAP_001", 1.0)
        assert lecture.unite == "kWh"
    
    def test_lecture_repr(self):
        """Test la représentation en string"""
        lecture = Lecture("CAP_001", 2.5, "kW")
        repr_str = repr(lecture)
        assert "CAP_001" in repr_str
        assert "2.50" in repr_str


class TestCapteur:
    """Tests pour la classe Capteur"""
    
    def test_creation_capteur_pompe(self):
        """Test la création d'un capteur pompe"""
        capteur = Capteur("CAP_POMPE_01", "pompe", "Bassin")
        assert capteur.capteur_id == "CAP_POMPE_01"
        assert capteur.type_equipement == "pompe"
        assert capteur.localisation == "Bassin"
        assert capteur.actif is True
    
    def test_creation_capteur_compresseur(self):
        """Test la création d'un capteur compresseur"""
        capteur = Capteur("CAP_COMP_01", "compresseur", "Station aération")
        assert capteur.type_equipement == "compresseur"
    
    def test_type_equipement_invalide(self):
        """Test qu'une exception est levée pour un type invalide"""
        with pytest.raises(ValueError):
            Capteur("CAP_001", "type_invalide", "Localisation")
    
    def test_generer_lecture_pompe(self):
        """Test la génération de lecture pour une pompe"""
        capteur = Capteur("CAP_POMPE_01", "pompe", "Bassin")
        lecture = capteur.generer_lecture()
        
        assert isinstance(lecture, Lecture)
        assert lecture.capteur_id == "CAP_POMPE_01"
        # Vérifier que la valeur est dans la plage correcte (0.5-3.0)
        assert 0.5 <= lecture.valeur <= 3.0
    
    def test_generer_lecture_compresseur(self):
        """Test la génération de lecture pour un compresseur"""
        capteur = Capteur("CAP_COMP_01", "compresseur", "Station")
        lecture = capteur.generer_lecture()
        
        # Vérifier que la valeur est dans la plage correcte (2.0-7.5)
        assert 2.0 <= lecture.valeur <= 7.5
    
    def test_generer_lecture_eclairage(self):
        """Test la génération de lecture pour l'éclairage"""
        capteur = Capteur("CAP_ECL_01", "eclairage", "Salle")
        lecture = capteur.generer_lecture()
        
        # Vérifier que la valeur est dans la plage correcte (0.2-1.5)
        assert 0.2 <= lecture.valeur <= 1.5
    
    def test_generer_lecture_ventilation(self):
        """Test la génération de lecture pour la ventilation"""
        capteur = Capteur("CAP_VENT_01", "ventilation", "Zone")
        lecture = capteur.generer_lecture()
        
        # Vérifier que la valeur est dans la plage correcte (0.3-2.0)
        assert 0.3 <= lecture.valeur <= 2.0
    
    def test_capteur_inactif(self):
        """Test qu'un capteur inactif produit une lecture zéro"""
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        capteur.actif = False
        lecture = capteur.generer_lecture()
        
        assert lecture.valeur == 0.0
    
    def test_get_info_capteur(self):
        """Test l'obtention des infos du capteur"""
        capteur = Capteur("CAP_POMPE_01", "pompe", "Bassin")
        info = capteur.get_info()
        
        assert info["capteur_id"] == "CAP_POMPE_01"
        assert info["type_equipement"] == "pompe"
        assert info["localisation"] == "Bassin"
        assert info["actif"] is True
    
    def test_capteur_repr(self):
        """Test la représentation en string"""
        capteur = Capteur("CAP_POMPE_01", "pompe", "Bassin")
        repr_str = repr(capteur)
        assert "CAP_POMPE_01" in repr_str
        assert "pompe" in repr_str


class TestGestionnaireCapteurs:
    """Tests pour la classe GestionnaireCapteurs"""
    
    def test_creation_gestionnaire(self):
        """Test la création d'un gestionnaire"""
        gestionnaire = GestionnaireCapteurs()
        assert gestionnaire.obtenir_nombre_capteurs() == 0
        assert gestionnaire.obtenir_nombre_lectures() == 0
    
    def test_ajouter_capteur(self):
        """Test l'ajout d'un capteur"""
        gestionnaire = GestionnaireCapteurs()
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        gestionnaire.ajouter_capteur(capteur)
        
        assert gestionnaire.obtenir_nombre_capteurs() == 1
    
    def test_ajouter_capteur_doublon(self):
        """Test qu'on ne peut pas ajouter deux capteurs avec le même ID"""
        gestionnaire = GestionnaireCapteurs()
        capteur1 = Capteur("CAP_001", "pompe", "Bassin1")
        capteur2 = Capteur("CAP_001", "pompe", "Bassin2")
        
        gestionnaire.ajouter_capteur(capteur1)
        
        with pytest.raises(ValueError):
            gestionnaire.ajouter_capteur(capteur2)
    
    def test_retirer_capteur(self):
        """Test le retrait d'un capteur"""
        gestionnaire = GestionnaireCapteurs()
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        gestionnaire.ajouter_capteur(capteur)
        gestionnaire.retirer_capteur("CAP_001")
        
        assert gestionnaire.obtenir_nombre_capteurs() == 0
    
    def test_retirer_capteur_inexistant(self):
        """Test qu'on ne peut pas retirer un capteur inexistant"""
        gestionnaire = GestionnaireCapteurs()
        
        with pytest.raises(KeyError):
            gestionnaire.retirer_capteur("CAP_INEXISTANT")
    
    def test_lire_tous_les_capteurs(self):
        """Test la lecture de tous les capteurs"""
        gestionnaire = GestionnaireCapteurs()
        capteur1 = Capteur("CAP_001", "pompe", "Bassin")
        capteur2 = Capteur("CAP_002", "compresseur", "Station")
        
        gestionnaire.ajouter_capteur(capteur1)
        gestionnaire.ajouter_capteur(capteur2)
        
        lectures = gestionnaire.lire_tous_les_capteurs()
        
        assert len(lectures) == 2
        assert gestionnaire.obtenir_nombre_lectures() == 2
    
    def test_lire_capteur_specifique(self):
        """Test la lecture d'un capteur spécifique"""
        gestionnaire = GestionnaireCapteurs()
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        gestionnaire.ajouter_capteur(capteur)
        
        lecture = gestionnaire.lire_capteur("CAP_001")
        
        assert isinstance(lecture, Lecture)
        assert lecture.capteur_id == "CAP_001"
        assert gestionnaire.obtenir_nombre_lectures() == 1
    
    def test_lire_capteur_inexistant(self):
        """Test qu'on ne peut pas lire un capteur inexistant"""
        gestionnaire = GestionnaireCapteurs()
        
        with pytest.raises(KeyError):
            gestionnaire.lire_capteur("CAP_INEXISTANT")
    
    def test_obtenir_info_capteur(self):
        """Test l'obtention des infos d'un capteur"""
        gestionnaire = GestionnaireCapteurs()
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        gestionnaire.ajouter_capteur(capteur)
        
        info = gestionnaire.obtenir_info_capteur("CAP_001")
        
        assert info["capteur_id"] == "CAP_001"
        assert info["type_equipement"] == "pompe"
    
    def test_lister_capteurs(self):
        """Test la liste de tous les capteurs"""
        gestionnaire = GestionnaireCapteurs()
        capteur1 = Capteur("CAP_001", "pompe", "Bassin")
        capteur2 = Capteur("CAP_002", "compresseur", "Station")
        
        gestionnaire.ajouter_capteur(capteur1)
        gestionnaire.ajouter_capteur(capteur2)
        
        liste = gestionnaire.lister_capteurs()
        
        assert len(liste) == 2
        assert liste[0]["capteur_id"] == "CAP_001"
        assert liste[1]["capteur_id"] == "CAP_002"
    
    def test_obtenir_historique(self):
        """Test l'obtention de l'historique en format dictionnaire"""
        gestionnaire = GestionnaireCapteurs()
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        gestionnaire.ajouter_capteur(capteur)
        gestionnaire.lire_capteur("CAP_001")
        
        historique = gestionnaire.obtenir_historique()
        
        assert len(historique) == 1
        assert isinstance(historique[0], dict)
        assert "capteur_id" in historique[0]
        assert "valeur" in historique[0]
        assert "timestamp" in historique[0]
    
    def test_reinitialiser_historique(self):
        """Test la réinitialisation de l'historique"""
        gestionnaire = GestionnaireCapteurs()
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        gestionnaire.ajouter_capteur(capteur)
        gestionnaire.lire_capteur("CAP_001")
        
        assert gestionnaire.obtenir_nombre_lectures() == 1
        
        gestionnaire.reinitialiser_historique()
        
        assert gestionnaire.obtenir_nombre_lectures() == 0
    
    def test_gestionnaire_repr(self):
        """Test la représentation du gestionnaire"""
        gestionnaire = GestionnaireCapteurs()
        capteur = Capteur("CAP_001", "pompe", "Bassin")
        gestionnaire.ajouter_capteur(capteur)
        
        repr_str = repr(gestionnaire)
        assert "capteurs=1" in repr_str


class TestIntegration:
    """Tests d'intégration"""
    
    def test_workflow_complet(self):
        """Test un workflow complet"""
        # Créer gestionnaire et capteurs
        gestionnaire = GestionnaireCapteurs()
        capteur1 = Capteur("CAP_POMPE_01", "pompe", "Bassin réception")
        capteur2 = Capteur("CAP_COMP_01", "compresseur", "Station aération")
        
        gestionnaire.ajouter_capteur(capteur1)
        gestionnaire.ajouter_capteur(capteur2)
        
        # Effectuer des lectures
        for _ in range(3):
            gestionnaire.lire_tous_les_capteurs()
        
        # Vérifier les résultats
        assert gestionnaire.obtenir_nombre_capteurs() == 2
        assert gestionnaire.obtenir_nombre_lectures() == 6
        
        # Obtenir l'historique
        historique = gestionnaire.obtenir_historique()
        assert len(historique) == 6
        
        # Vérifier que toutes les lectures ont les bonnes plages
        for lecture in historique:
            capteur = gestionnaire.capteurs[lecture["capteur_id"]]
            min_val, max_val = capteur.PLAGES_CONSOMMATION[capteur.type_equipement]
            assert min_val <= lecture["valeur"] <= max_val


# Configuration Pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])