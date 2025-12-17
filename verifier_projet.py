"""
Module verifier_projet.py
Script pour vérifier la qualité du projet :
- Exécute tous les tests Pytest
- Vérifie la qualité avec Flake8
- Génère un rapport
"""

import subprocess
import sys
from pathlib import Path


class VerificateurProjet:
    """Vérifie la qualité et le fonctionnement du projet"""
    
    def __init__(self):
        """Initialise le vérificateur"""
        self.dossier_projet = Path(__file__).parent
        self.resultats = {}
    
    def verifier_pytest(self) -> bool:
        """
        Exécute Pytest et retourne le résultat
        
        Returns:
            True si tous les tests passent, False sinon
        """
        print("\n" + "=" * 70)
        print("🧪 EXÉCUTION DES TESTS PYTEST")
        print("=" * 70 + "\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", "--tb=short"],
                capture_output=False,
                text=True
            )
            
            success = result.returncode == 0
            self.resultats["pytest"] = success
            
            if success:
                print("\n✅ Tous les tests Pytest ont réussi!")
            else:
                print("\n❌ Certains tests Pytest ont échoué!")
            
            return success
        
        except Exception as e:
            print(f"\n❌ Erreur lors de l'exécution de Pytest : {e}")
            self.resultats["pytest"] = False
            return False
    
    def verifier_flake8(self) -> bool:
        """
        Exécute Flake8 pour vérifier la qualité du code
        
        Returns:
            True si pas d'erreurs majeures, False sinon
        """
        print("\n" + "=" * 70)
        print("📋 VÉRIFICATION DE LA QUALITÉ DU CODE (FLAKE8)")
        print("=" * 70 + "\n")
        
        fichiers_python = [
            "capteur.py",
            "gestionnaire.py",
            "simulateur.py",
            "base_donnees.py",
            "anomalies.py",
            "simulateur_complet.py"
        ]
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "flake8"] + fichiers_python,
                capture_output=True,
                text=True
            )
            
            output = result.stdout
            
            if output:
                print("⚠️  Problèmes détectés par Flake8 :\n")
                print(output)
                self.resultats["flake8"] = False
                return False
            else:
                print("✅ Aucun problème détecté par Flake8!")
                self.resultats["flake8"] = True
                return True
        
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de Flake8 : {e}")
            print("   Assurez-vous que flake8 est installé : pip install flake8")
            self.resultats["flake8"] = False
            return False
    
    def verifier_imports(self) -> bool:
        """
        Vérifie que tous les modules peuvent être importés
        
        Returns:
            True si tous les imports réussissent, False sinon
        """
        print("\n" + "=" * 70)
        print("📦 VÉRIFICATION DES IMPORTS")
        print("=" * 70 + "\n")
        
        modules = [
            ("capteur", "Capteur, Lecture"),
            ("gestionnaire", "GestionnaireCapteurs"),
            ("base_donnees", "BaseDonnees"),
            ("anomalies", "DetecteurAnomalies"),
            ("simulateur_complet", "SimulateurComplet")
        ]
        
        all_ok = True
        
        for module_name, classes in modules:
            try:
                exec(f"from {module_name} import {classes}")
                print(f"✅ {module_name}.py - OK")
            except Exception as e:
                print(f"❌ {module_name}.py - ERREUR : {e}")
                all_ok = False
        
        self.resultats["imports"] = all_ok
        return all_ok
    
    def verifier_fichiers_config(self) -> bool:
        """
        Vérifie que les fichiers de configuration existent
        
        Returns:
            True si tous les fichiers existent, False sinon
        """
        print("\n" + "=" * 70)
        print("📁 VÉRIFICATION DES FICHIERS DE CONFIGURATION")
        print("=" * 70 + "\n")
        
        fichiers_requis = [
            ".flake8",
            "README.md",
            "requirements.txt",
            ".gitignore"
        ]
        
        all_ok = True
        
        for fichier in fichiers_requis:
            chemin = self.dossier_projet / fichier
            if chemin.exists():
                print(f"✅ {fichier}")
            else:
                print(f"❌ {fichier} - MANQUANT")
                all_ok = False
        
        self.resultats["fichiers_config"] = all_ok
        return all_ok
    
    def generer_rapport(self) -> None:
        """Génère un rapport récapitulatif"""
        print("\n" + "=" * 70)
        print("📊 RAPPORT FINAL")
        print("=" * 70 + "\n")
        
        resultats_texte = {
            "imports": "Imports des modules",
            "fichiers_config": "Fichiers de configuration",
            "flake8": "Qualité du code (Flake8)",
            "pytest": "Tests unitaires (Pytest)"
        }
        
        print("Résultats :\n")
        
        for cle, description in resultats_texte.items():
            if cle in self.resultats:
                status = "✅ PASS" if self.resultats[cle] else "❌ FAIL"
                print(f"  {status} - {description}")
        
        # Résumé global
        tous_ok = all(self.resultats.values())
        
        print("\n" + "─" * 70)
        if tous_ok:
            print("🎉 PROJET VALIDE - Tous les tests et vérifications ont réussi!")
        else:
            print("⚠️  ATTENTION - Certaines vérifications n'ont pas réussi")
        print("─" * 70 + "\n")
    
    def verifier_complet(self) -> bool:
        """
        Exécute toutes les vérifications
        
        Returns:
            True si tout est OK, False sinon
        """
        print("\n" + "🔍 " * 20)
        print("VÉRIFICATION COMPLÈTE DU PROJET")
        print("🔍 " * 20)
        
        # 1. Vérifier les imports
        self.verifier_imports()
        
        # 2. Vérifier les fichiers
        self.verifier_fichiers_config()
        
        # 3. Vérifier la qualité
        self.verifier_flake8()
        
        # 4. Exécuter les tests
        self.verifier_pytest()
        
        # 5. Générer le rapport
        self.generer_rapport()
        
        return all(self.resultats.values())


def main():
    """Fonction principale"""
    verificateur = VerificateurProjet()
    succes = verificateur.verifier_complet()
    
    # Code de sortie
    sys.exit(0 if succes else 1)


if __name__ == "__main__":
    main()
