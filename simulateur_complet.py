"""
Module simulateur_complet.py
Intégration complète : capteurs → stockage → détection d'anomalies
"""

from gestionnaire import GestionnaireCapteurs
from capteur import Capteur
from base_donnees import BaseDonnees
from anomalies import DetecteurAnomalies
import json


class SimulateurComplet:
    """Simulateur complet du système d'énergie"""
    
    def __init__(self, nom_base: str = "donnees_capteurs.json"):
        """
        Initialise le simulateur complet
        
        Args:
            nom_base: Nom du fichier JSON pour la base de données
        """
        self.gestionnaire = GestionnaireCapteurs()
        self.base_donnees = BaseDonnees(nom_base)
        self.detecteur = DetecteurAnomalies()
        self._initialiser_capteurs()
    
    def _initialiser_capteurs(self) -> None:
        """Initialise les capteurs de l'unité"""
        capteurs_config = [
            ("CAP_POMPE_01", "pompe", "Bassin de réception"),
            ("CAP_POMPE_02", "pompe", "Bassin de traitement"),
            ("CAP_COMPRESSEUR_01", "compresseur", "Station aération"),
            ("CAP_ECLAIRAGE_01", "eclairage", "Salle de contrôle"),
            ("CAP_VENTILATION_01", "ventilation", "Zone de traitement"),
        ]
        
        for capteur_id, type_eq, localisation in capteurs_config:
            capteur = Capteur(capteur_id, type_eq, localisation)
            self.gestionnaire.ajouter_capteur(capteur)
    
    def cycle_complet(self, nombre_cycles: int = 1) -> None:
        """
        Exécute un cycle complet : lecture → stockage → détection
        
        Args:
            nombre_cycles: Nombre de cycles à exécuter
        """
        print("\n" + "=" * 70)
        print("🔄 CYCLE COMPLET - Capteurs → Base → Anomalies")
        print("=" * 70)
        
        for cycle in range(1, nombre_cycles + 1):
            print(f"\n📍 Cycle {cycle}/{nombre_cycles}")
            print("─" * 70)
            
            # ÉTAPE 1 : Lire les capteurs
            lectures = self.gestionnaire.lire_tous_les_capteurs()
            print(f"\n✓ Étape 1 : Lecture des {len(lectures)} capteurs")
            
            # Convertir en format dict avec type_equipement
            lectures_dict = []
            for lecture in lectures:
                capteur = self.gestionnaire.capteurs[lecture.capteur_id]
                lecture_dict = lecture.to_dict()
                lecture_dict["type_equipement"] = capteur.type_equipement
                lectures_dict.append(lecture_dict)
            
            # ÉTAPE 2 : Stocker dans la base
            self.base_donnees.inserer_multiple(lectures_dict)
            print(f"✓ Étape 2 : Stockage dans la base ({self.base_donnees.compter()} enregistrements)")
            
            # ÉTAPE 3 : Détection d'anomalies
            lectures_avec_anomalies = self.detecteur.detecter_anomalies(
                self.base_donnees.obtenir_tous()
            )
            anomalies = [l for l in lectures_avec_anomalies if l.get("anomalie", False)]
            
            print(f"✓ Étape 3 : Détection d'anomalies ({len(anomalies)} détectées)")
            
            # Afficher les anomalies du cycle
            if anomalies:
                print("\n  ⚠️  Anomalies détectées :")
                for anom in anomalies:
                    print(f"     • {anom['capteur_id']:<20} | "
                          f"{anom['valeur']:>7.2f} {anom['unite']:<5} | "
                          f"{anom['type_anomalie']}")
    
    def afficher_statistiques(self) -> None:
        """Affiche les statistiques actuelles"""
        print("\n" + "=" * 70)
        print("📊 STATISTIQUES ACTUELLES")
        print("=" * 70)
        
        info_base = self.base_donnees.obtenir_info()
        print(f"\n💾 Base de données :")
        print(f"  • Fichier : {info_base['chemin']}")
        print(f"  • Total enregistrements : {info_base['nombre_lectures']}")
        print(f"  • Capteurs uniques : {info_base['nombre_capteurs_uniques']}")
        
        # Statistiques par type
        print(f"\n📈 Statistiques par type d'équipement :")
        types_eq = ["pompe", "compresseur", "eclairage", "ventilation"]
        
        for type_eq in types_eq:
            lectures = self.base_donnees.obtenir_par_type(type_eq)
            if lectures:
                stats = self.base_donnees.statistiques()
                print(f"  • {type_eq:<15} : "
                      f"{len(lectures):>3} mesures | "
                      f"Moy: {stats.get('moyenne', 0):>6.2f} kW")
        
        # Statistiques anomalies
        toutes_lectures = self.base_donnees.obtenir_tous()
        if toutes_lectures:
            lectures_analysees = self.detecteur.detecter_anomalies(toutes_lectures)
            rapport = self.detecteur.rapport_anomalies(lectures_analysees)
            
            print(f"\n⚠️  Anomalies :")
            print(f"  • Total anomalies : {rapport['nombre_anomalies']}")
            print(f"  • Pourcentage : {rapport['pourcentage_anomalies']}%")
        
        print()
    
    def afficher_dernieres_lectures(self, nombre: int = 5) -> None:
        """Affiche les dernières lectures"""
        print("\n" + "=" * 70)
        print(f"📡 {nombre} DERNIÈRES LECTURES")
        print("=" * 70 + "\n")
        
        dernieres = self.base_donnees.obtenir_dernieres(nombre)
        
        if not dernieres:
            print("  Aucune donnée disponible\n")
            return
        
        for i, lecture in enumerate(dernieres, 1):
            print(f"  {i}. {lecture.get('capteur_id', 'N/A'):<20} | "
                  f"{lecture.get('valeur', 0):>7.2f} {lecture.get('unite', 'kW'):<5} | "
                  f"{lecture.get('timestamp', 'N/A')}")
        print()
    
    def afficher_anomalies_detaillees(self) -> None:
        """Affiche un rapport détaillé des anomalies"""
        toutes_lectures = self.base_donnees.obtenir_tous()
        
        if not toutes_lectures:
            print("\nAucune donnée disponible pour l'analyse\n")
            return
        
        lectures_analysees = self.detecteur.detecter_anomalies(toutes_lectures)
        self.detecteur.afficher_rapport(lectures_analysees)
    
    def reinitialiser_base(self) -> None:
        """Réinitialise la base de données"""
        self.base_donnees.supprimer_tous()
        print("\n✅ Base de données réinitialisée\n")
    
    def exporter_json(self, nom_fichier: str = "export_donnees.json") -> None:
        """Exporte les données en JSON"""
        donnees = self.base_donnees.obtenir_tous()
        
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Export réussi : {nom_fichier}")
        print(f"   ({len(donnees)} enregistrements)\n")
    
    def menu_principal(self) -> None:
        """Affiche le menu principal interactif"""
        while True:
            print("\n" + "=" * 70)
            print("🏭 SYSTÈME DE SUIVI ÉNERGÉTIQUE - MENU PRINCIPAL")
            print("=" * 70)
            print("""
  1 - Exécuter 1 cycle complet (capteurs → stockage → anomalies)
  2 - Exécuter 5 cycles complets
  3 - Afficher les statistiques
  4 - Afficher les 5 dernières lectures
  5 - Afficher le rapport détaillé des anomalies
  6 - Exporter les données en JSON
  7 - Réinitialiser la base de données
  8 - Quitter
            """)
            
            choix = input("Choisissez une option (1-8) : ").strip()
            
            if choix == "1":
                self.cycle_complet(1)
            elif choix == "2":
                self.cycle_complet(5)
            elif choix == "3":
                self.afficher_statistiques()
            elif choix == "4":
                self.afficher_dernieres_lectures(5)
            elif choix == "5":
                self.afficher_anomalies_detaillees()
            elif choix == "6":
                nom = input("Nom du fichier d'export (défaut: export_donnees.json) : ").strip()
                if not nom:
                    nom = "export_donnees.json"
                self.exporter_json(nom)
            elif choix == "7":
                confirm = input("⚠️  Êtes-vous sûr de vouloir réinitialiser ? (o/n) : ").strip().lower()
                if confirm == 'o':
                    self.reinitialiser_base()
            elif choix == "8":
                print("\n👋 Au revoir!\n")
                break
            else:
                print("\n❌ Option invalide. Veuillez réessayer.\n")


def main():
    """Fonction principale"""
    print("\n" + "=" * 70)
    print("🏭 DÉMARRAGE DU SYSTÈME DE SUIVI ÉNERGÉTIQUE")
    print("=" * 70)
    
    simulateur = SimulateurComplet("donnees_capteurs.json")
    
    print("\n✅ Système initialisé")
    print(f"   Capteurs actifs : {simulateur.gestionnaire.obtenir_nombre_capteurs()}")
    
    # Lancer le menu interactif
    simulateur.menu_principal()


if __name__ == "__main__":
    main()
