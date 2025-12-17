"""
Module test_base_donnees.py
Tests unitaires pour la classe BaseDonnees
"""

import pytest
import json
from pathlib import Path
import tempfile
from base_donnees import BaseDonnees


class TestBaseDonnees:
    """Tests pour la classe BaseDonnees"""
    
    @pytest.fixture
    def bd_temp(self):
        """Crée une base de données temporaire pour les tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fichier = Path(tmpdir) / "test_donnees.json"
            bd = BaseDonnees(str(fichier))
            yield bd
            # Cleanup automatique
    
    def test_creation_fichier(self, bd_temp):
        """Test que le fichier est créé"""
        assert bd_temp.chemin_fichier.exists()
    
    def test_initialisation_vide(self, bd_temp):
        """Test que la base est vide au démarrage"""
        assert bd_temp.obtenir_tous() == []
    
    def test_inserer_une_lecture(self, bd_temp):
        """Test l'insertion d'une lecture"""
        lecture = {
            "capteur_id": "CAP_001",
            "valeur": 2.5,
            "unite": "kW",
            "timestamp": "2025-12-17T12:00:00"
        }
        bd_temp.inserer(lecture)
        
        assert bd_temp.compter() == 1
        assert bd_temp.obtenir_tous()[0]["capteur_id"] == "CAP_001"
    
    def test_inserer_multiple(self, bd_temp):
        """Test l'insertion de plusieurs lectures"""
        lectures = [
            {
                "capteur_id": "CAP_001",
                "valeur": 2.5,
                "unite": "kW",
                "timestamp": "2025-12-17T12:00:00"
            },
            {
                "capteur_id": "CAP_002",
                "valeur": 5.0,
                "unite": "kW",
                "timestamp": "2025-12-17T12:01:00"
            }
        ]
        bd_temp.inserer_multiple(lectures)
        
        assert bd_temp.compter() == 2
    
    def test_obtenir_par_capteur(self, bd_temp):
        """Test la récupération par capteur"""
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 2.5, "timestamp": "2025-12-17T12:00:00"},
            {"capteur_id": "CAP_001", "valeur": 2.7, "timestamp": "2025-12-17T12:01:00"},
            {"capteur_id": "CAP_002", "valeur": 5.0, "timestamp": "2025-12-17T12:00:00"}
        ]
        bd_temp.inserer_multiple(lectures)
        
        lectures_cap1 = bd_temp.obtenir_par_capteur("CAP_001")
        
        assert len(lectures_cap1) == 2
        assert all(l["capteur_id"] == "CAP_001" for l in lectures_cap1)
    
    def test_obtenir_par_type(self, bd_temp):
        """Test la récupération par type d'équipement"""
        lectures = [
            {"capteur_id": "CAP_001", "type_equipement": "pompe", "valeur": 2.5},
            {"capteur_id": "CAP_002", "type_equipement": "pompe", "valeur": 2.8},
            {"capteur_id": "CAP_003", "type_equipement": "compresseur", "valeur": 5.0}
        ]
        bd_temp.inserer_multiple(lectures)
        
        pompes = bd_temp.obtenir_par_type("pompe")
        
        assert len(pompes) == 2
        assert all(l["type_equipement"] == "pompe" for l in pompes)
    
    def test_obtenir_dernieres(self, bd_temp):
        """Test la récupération des dernières lectures"""
        lectures = [
            {"capteur_id": f"CAP_{i:03d}", "valeur": float(i)}
            for i in range(15)
        ]
        bd_temp.inserer_multiple(lectures)
        
        dernieres = bd_temp.obtenir_dernieres(5)
        
        assert len(dernieres) == 5
        assert dernieres[-1]["capteur_id"] == "CAP_014"
    
    def test_filtrer_par_periode(self, bd_temp):
        """Test le filtrage par période"""
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 1.0, "timestamp": "2025-12-17T12:00:00"},
            {"capteur_id": "CAP_002", "valeur": 2.0, "timestamp": "2025-12-17T12:30:00"},
            {"capteur_id": "CAP_003", "valeur": 3.0, "timestamp": "2025-12-17T13:00:00"}
        ]
        bd_temp.inserer_multiple(lectures)
        
        periode = bd_temp.filtrer_par_periode(
            "2025-12-17T12:00:00",
            "2025-12-17T12:59:59"
        )
        
        assert len(periode) == 2
    
    def test_statistiques_globales(self, bd_temp):
        """Test les statistiques globales"""
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 1.0},
            {"capteur_id": "CAP_002", "valeur": 2.0},
            {"capteur_id": "CAP_003", "valeur": 3.0},
            {"capteur_id": "CAP_004", "valeur": 4.0},
            {"capteur_id": "CAP_005", "valeur": 5.0}
        ]
        bd_temp.inserer_multiple(lectures)
        
        stats = bd_temp.statistiques()
        
        assert stats["count"] == 5
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["moyenne"] == 3.0
    
    def test_statistiques_par_capteur(self, bd_temp):
        """Test les statistiques par capteur"""
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 2.0},
            {"capteur_id": "CAP_001", "valeur": 4.0},
            {"capteur_id": "CAP_001", "valeur": 6.0},
            {"capteur_id": "CAP_002", "valeur": 10.0}
        ]
        bd_temp.inserer_multiple(lectures)
        
        stats = bd_temp.statistiques("CAP_001")
        
        assert stats["count"] == 3
        assert stats["moyenne"] == 4.0
        assert stats["min"] == 2.0
        assert stats["max"] == 6.0
    
    def test_supprimer_tous(self, bd_temp):
        """Test la suppression complète"""
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 1.0},
            {"capteur_id": "CAP_002", "valeur": 2.0}
        ]
        bd_temp.inserer_multiple(lectures)
        
        bd_temp.supprimer_tous()
        
        assert bd_temp.compter() == 0
    
    def test_supprimer_par_capteur(self, bd_temp):
        """Test la suppression par capteur"""
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 1.0},
            {"capteur_id": "CAP_001", "valeur": 1.5},
            {"capteur_id": "CAP_002", "valeur": 2.0}
        ]
        bd_temp.inserer_multiple(lectures)
        
        nombre_supprime = bd_temp.supprimer_par_capteur("CAP_001")
        
        assert nombre_supprime == 2
        assert bd_temp.compter() == 1
    
    def test_charger_fichier_existant(self, bd_temp):
        """Test le chargement depuis un fichier existant"""
        # Insérer des données
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 2.5},
            {"capteur_id": "CAP_002", "valeur": 5.0}
        ]
        bd_temp.inserer_multiple(lectures)
        
        # Créer une nouvelle instance du même fichier
        bd2 = BaseDonnees(str(bd_temp.chemin_fichier))
        
        assert bd2.compter() == 2
        assert len(bd2.obtenir_tous()) == 2
    
    def test_obtenir_info(self, bd_temp):
        """Test l'obtention des infos"""
        lectures = [
            {"capteur_id": "CAP_001", "valeur": 1.0},
            {"capteur_id": "CAP_001", "valeur": 1.5},
            {"capteur_id": "CAP_002", "valeur": 2.0}
        ]
        bd_temp.inserer_multiple(lectures)
        
        info = bd_temp.obtenir_info()
        
        assert info["nombre_lectures"] == 3
        assert info["nombre_capteurs_uniques"] == 2
    
    def test_erreur_fichier_corrompu(self):
        """Test la gestion des fichiers JSON corrompus"""
        with tempfile.TemporaryDirectory() as tmpdir:
            fichier = Path(tmpdir) / "corrupted.json"
            fichier.write_text("{ invalid json")
            
            with pytest.raises(IOError):
                bd = BaseDonnees(str(fichier))
                bd.charger()
    
    def test_repr(self, bd_temp):
        """Test la représentation en string"""
        lectures = [{"capteur_id": "CAP_001", "valeur": 1.0}]
        bd_temp.inserer_multiple(lectures)
        
        repr_str = repr(bd_temp)
        assert "BaseDonnees" in repr_str
        assert "lectures=1" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
