from gestionnaire import GestionnaireCapteurs
from capteur import Capteur
import json


def initialiser_capteurs() -> GestionnaireCapteurs:
    """
    Initialise le gestionnaire avec les capteurs de l'unité de traitement
    
    Returns:
        GestionnaireCapteurs: Gestionnaire avec 5 capteurs configurés
    """
    gestionnaire = GestionnaireCapteurs()
    
    # Configuration des capteurs pour une unité de traitement des eaux
    capteurs_config = [
        ("CAP_POMPE_01", "pompe", "Bassin de réception"),
        ("CAP_POMPE_02", "pompe", "Bassin de traitement"),
        ("CAP_COMPRESSEUR_01", "compresseur", "Station aération"),
        ("CAP_ECLAIRAGE_01", "eclairage", "Salle de contrôle"),
        ("CAP_VENTILATION_01", "ventilation", "Zone de traitement"),
    ]
    
    print("=" * 60)
    print("🏭 INITIALISATION - Unité de traitement des eaux")
    print("=" * 60)
    print("\n📊 Capteurs configurés :\n")
    
    for capteur_id, type_eq, localisation in capteurs_config:
        capteur = Capteur(capteur_id, type_eq, localisation)
        gestionnaire.ajouter_capteur(capteur)
        print(f"  ✓ {capteur_id:<20} | {type_eq:<15} | {localisation}")
    
    print(f"\n✅ Total : {gestionnaire.obtenir_nombre_capteurs()} capteurs actifs\n")
    
    return gestionnaire


def afficher_lectures(lectures, titre="Lecture des capteurs"):
    """
    Affiche les lectures de manière formatée
    
    Args:
        lectures: Liste des lectures
        titre: Titre de l'affichage
    """
    print(f"\n{'=' * 60}")
    print(f"📈 {titre}")
    print(f"{'=' * 60}\n")
    
    for lecture in lectures:
        print(f"  {lecture.capteur_id:<20} | "
              f"{lecture.valeur:>7.2f} {lecture.unite:<5} | "
              f"{lecture.timestamp}")
    
    print()


def simuler_session_simple():
    """Simule une session simple de lecture des capteurs"""
    gestionnaire = initialiser_capteurs()
    
    # Première lecture
    print("\n🔄 PREMIÈRE LECTURE")
    lectures1 = gestionnaire.lire_tous_les_capteurs()
    afficher_lectures(lectures1, "Lecture #1")
    
    # Deuxième lecture
    print("🔄 DEUXIÈME LECTURE")
    lectures2 = gestionnaire.lire_tous_les_capteurs()
    afficher_lectures(lectures2, "Lecture #2")
    
    # Afficher statistiques
    print("=" * 60)
    print("📊 STATISTIQUES")
    print("=" * 60)
    print(f"  • Nombre total de capteurs : {gestionnaire.obtenir_nombre_capteurs()}")
    print(f"  • Nombre total de lectures : {gestionnaire.obtenir_nombre_lectures()}")
    print()


def simuler_session_detaillee():
    """Simule une session détaillée avec plusieurs lectures"""
    gestionnaire = initialiser_capteurs()
    
    nombre_lectures = 3
    
    print(f"\n🔄 SIMULATION : {nombre_lectures} cycles de lecture\n")
    
    for cycle in range(1, nombre_lectures + 1):
        print(f"\n{'─' * 60}")
        print(f"📍 Cycle {cycle}/{nombre_lectures}")
        print(f"{'─' * 60}\n")
        
        lectures = gestionnaire.lire_tous_les_capteurs()
        
        # Afficher chaque lecture
        for lecture in lectures:
            type_eq = lecture.capteur_id.split('_')[1].upper()
            print(f"  📡 {lecture.capteur_id:<20} | "
                  f"Consommation: {lecture.valeur:>7.2f} {lecture.unite}")
        
        # Calculer la consommation totale du cycle
        consommation_totale = sum(l.valeur for l in lectures)
        print(f"\n  💡 Consommation totale du cycle : {consommation_totale:.2f} kW")
    
    # Afficher l'historique complet
    print(f"\n\n{'=' * 60}")
    print("📚 HISTORIQUE COMPLET")
    print(f"{'=' * 60}\n")
    
    historique = gestionnaire.obtenir_historique()
    for i, lecture in enumerate(historique, 1):
        print(f"  {i:2d}. {lecture['capteur_id']:<20} | "
              f"{lecture['valeur']:>7.2f} {lecture['unite']:<5} | "
              f"{lecture['timestamp']}")
    
    # Statistiques finales
    print(f"\n\n{'=' * 60}")
    print("📊 RÉSUMÉ FINAL")
    print(f"{'=' * 60}")
    print(f"  ✓ Capteurs actifs : {gestionnaire.obtenir_nombre_capteurs()}")
    print(f"  ✓ Lectures effectuées : {gestionnaire.obtenir_nombre_lectures()}")
    print(f"  ✓ Cycles complétés : {nombre_lectures}")
    print()


def exporter_donnees(gestionnaire, nom_fichier="donnees_capteurs.json"):
    """
    Exporte les données de l'historique en JSON (prêt pour MongoDB)
    
    Args:
        gestionnaire: Instance du GestionnaireCapteurs
        nom_fichier: Nom du fichier de sortie
    """
    historique = gestionnaire.obtenir_historique()
    
    with open(nom_fichier, 'w', encoding='utf-8') as f:
        json.dump(historique, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Données exportées vers {nom_fichier}")
    print(f"   ({len(historique)} lectures enregistrées)")


if __name__ == "__main__":
    # Choisir le mode de simulation
    print("\n🎯 MODES DE SIMULATION DISPONIBLES\n")
    print("  1 - Simulation simple (2 lectures)")
    print("  2 - Simulation détaillée (3 cycles)")
    print()
    
    choix = input("Choisissez un mode (1 ou 2) : ").strip()
    
    if choix == "1":
        simuler_session_simple()
    elif choix == "2":
        simuler_session_detaillee()
        
        # Optionnel : exporter les données
        export = input("\nExporter les données en JSON ? (o/n) : ").strip().lower()
        if export == 'o':
            gestionnaire = initialiser_capteurs()
            for _ in range(3):
                gestionnaire.lire_tous_les_capteurs()
            exporter_donnees(gestionnaire)
    else:
        print("❌ Choix invalide. Veuillez relancer le programme.")