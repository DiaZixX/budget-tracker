from datetime import datetime

from database_manager import BudgetDatabase
from visualizer import BudgetVisualizer


def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "=" * 50)
    print("GESTIONNAIRE DE BUDGET")
    print("=" * 50)
    print("1. Ajouter une transaction")
    print("2. Modifier une transaction")
    print("3. Supprimer une transaction")
    print("4. Voir transactions du mois")
    print("5. Lister revenus du mois")
    print("6. Lister dépenses du mois")
    print("7. Voir totaux par personne")
    print("8. Analyse dépenses (Commun/Perso)")
    print("9. Analyse revenus par auteur")
    print("10. Graphiques d'évolution mensuelle")
    print("11. Graphique comparatif auteurs")
    print("12. Quitter")
    print("=" * 50)


def ajouter_transaction(db: BudgetDatabase):
    """Interface pour ajouter une transaction"""
    print("\n--- AJOUTER UNE TRANSACTION ---")

    date = input("Date (YYYY-MM-DD) [Entrée pour aujourd'hui]: ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    montant = float(input("Montant: "))

    print("Type: 1=Revenu, 2=Dépense")
    type_choice = input("Choix: ")
    type_trans = "Revenu" if type_choice == "1" else "Depense"

    print("Utilité: 1=Commun, 2=Perso")
    util_choice = input("Choix: ")
    utilite = "Commun" if util_choice == "1" else "Perso"

    description = input("Description: ")
    auteur = input("Auteur: ")

    transaction_id = db.ajouter_entree(date, montant, type_trans, utilite, description, auteur)
    print(f"✓ Transaction ajoutée avec l'ID {transaction_id}")


def modifier_transaction(db: BudgetDatabase):
    """Interface pour modifier une transaction"""
    print("\n--- MODIFIER UNE TRANSACTION ---")
    transaction_id = int(input("ID de la transaction à modifier: "))

    # Récupérer la transaction actuelle
    transaction = db.obtenir_transaction_par_id(transaction_id)

    if not transaction:
        print("✗ Transaction non trouvée")
        return

    # Afficher la transaction actuelle
    print("\nTransaction actuelle:")
    print(f"Date: {transaction['Date']}")
    print(f"Montant: {transaction['Montant']}")
    print(f"Type: {transaction['Type']}")
    print(f"Utilité: {transaction['Utilite']}")
    print(f"Description: {transaction['Description']}")
    print(f"Auteur: {transaction['Auteur']}")

    print("\n(Appuyez sur Entrée pour conserver la valeur actuelle)")

    # Demander les nouvelles valeurs
    date = input(f"Nouvelle date [{transaction['Date']}]: ").strip() or None

    montant_str = input(f"Nouveau montant [{transaction['Montant']}]: ").strip()
    montant = float(montant_str) if montant_str else None

    print(f"Type actuel: {transaction['Type']}")
    print("Nouveau type: 1=Revenu, 2=Dépense, Entrée=Conserver")
    type_choice = input("Choix: ").strip()
    type_trans = None
    if type_choice == "1":
        type_trans = "Revenu"
    elif type_choice == "2":
        type_trans = "Depense"

    print(f"Utilité actuelle: {transaction['Utilite']}")
    print("Nouvelle utilité: 1=Commun, 2=Perso, Entrée=Conserver")
    util_choice = input("Choix: ").strip()
    utilite = None
    if util_choice == "1":
        utilite = "Commun"
    elif util_choice == "2":
        utilite = "Perso"

    description = input(f"Nouvelle description [{transaction['Description']}]: ").strip() or None
    auteur = input(f"Nouvel auteur [{transaction['Auteur']}]: ").strip() or None

    if db.modifier_entree(transaction_id, date, montant, type_trans, utilite, description, auteur):
        print("✓ Transaction modifiée")
    else:
        print("✗ Erreur lors de la modification")


def supprimer_transaction(db: BudgetDatabase):
    """Interface pour supprimer une transaction"""
    print("\n--- SUPPRIMER UNE TRANSACTION ---")
    transaction_id = int(input("ID de la transaction à supprimer: "))

    if db.supprimer_entree(transaction_id):
        print("✓ Transaction supprimée")
    else:
        print("✗ Transaction non trouvée")


def voir_transactions_mois(db: BudgetDatabase):
    """Affiche les transactions d'un mois"""
    print("\n--- TRANSACTIONS DU MOIS ---")
    annee = int(input("Année: "))
    mois = int(input("Mois (1-12): "))

    print("\nFiltre par type? 1=Tous, 2=Revenus, 3=Dépenses")
    type_choice = input("Choix: ")
    type_filter = None
    if type_choice == "2":
        type_filter = "Revenu"
    elif type_choice == "3":
        type_filter = "Depense"

    auteur = input("Filtrer par auteur (Entrée pour tous): ").strip() or None

    transactions = db.obtenir_transactions_mois(annee, mois, type_filter, auteur)

    if not transactions:
        print("\nAucune transaction trouvée")
        return

    print(f"\n{len(transactions)} transaction(s) trouvée(s):")
    print("-" * 100)
    print(f"{'ID':<5} {'Date':<12} {'Type':<10} {'Utilité':<10} {'Montant':<10} {'Auteur':<15} {'Description':<30}")
    print("-" * 100)

    for t in transactions:
        print(
            f"{t['ID']:<5} {t['Date']:<12} {t['Type']:<10} {t['Utilite']:<10} {t['Montant']:<10.2f} {t['Auteur']:<15} {t['Description']:<30}"
        )


def lister_revenus_mois(db: BudgetDatabase):
    """Liste tous les revenus d'un mois donné avec option de filtrage par auteur"""
    print("\n--- LISTE DES REVENUS DU MOIS ---")
    annee = int(input("Année: "))
    mois = int(input("Mois (1-12): "))

    # Nouveau: Option de filtrage par auteur
    auteur = input("Filtrer par auteur (Entrée pour tous): ").strip() or None

    revenus = db.obtenir_transactions_mois(annee, mois, type_transaction="Revenu", auteur=auteur)

    if not revenus:
        print("\nAucun revenu pour ce mois")
        if auteur:
            print(f"(avec le filtre auteur: {auteur})")
        return

    total = sum(r["Montant"] for r in revenus)

    # Affichage du titre avec mention du filtre si applicable
    titre = f"\n{len(revenus)} revenu(s) pour {mois:02d}/{annee}"
    if auteur:
        titre += f" - Auteur: {auteur}"
    print(titre + ":")

    print("-" * 100)
    print(f"{'ID':<5} {'Date':<12} {'Utilité':<10} {'Montant':<10} {'Auteur':<15} {'Description':<30}")
    print("-" * 100)

    for r in revenus:
        print(
            f"{r['ID']:<5} {r['Date']:<12} {r['Utilite']:<10} {r['Montant']:<10.2f} {r['Auteur']:<15} {r['Description']:<30}"
        )

    print("-" * 100)
    print(f"{'TOTAL':<37} {total:<10.2f}")


def lister_depenses_mois(db: BudgetDatabase):
    """Liste toutes les dépenses d'un mois donné avec option de filtrage par auteur"""
    print("\n--- LISTE DES DÉPENSES DU MOIS ---")
    annee = int(input("Année: "))
    mois = int(input("Mois (1-12): "))

    # Nouveau: Option de filtrage par auteur
    auteur = input("Filtrer par auteur (Entrée pour tous): ").strip() or None

    depenses = db.obtenir_transactions_mois(annee, mois, type_transaction="Depense", auteur=auteur)

    if not depenses:
        print("\nAucune dépense pour ce mois")
        if auteur:
            print(f"(avec le filtre auteur: {auteur})")
        return

    total = sum(d["Montant"] for d in depenses)

    # Affichage du titre avec mention du filtre si applicable
    titre = f"\n{len(depenses)} dépense(s) pour {mois:02d}/{annee}"
    if auteur:
        titre += f" - Auteur: {auteur}"
    print(titre + ":")

    print("-" * 100)
    print(f"{'ID':<5} {'Date':<12} {'Utilité':<10} {'Montant':<10} {'Auteur':<15} {'Description':<30}")
    print("-" * 100)

    for d in depenses:
        print(
            f"{d['ID']:<5} {d['Date']:<12} {d['Utilite']:<10} {d['Montant']:<10.2f} {d['Auteur']:<15} {d['Description']:<30}"
        )

    print("-" * 100)
    print(f"{'TOTAL':<37} {total:<10.2f}")


def voir_totaux_par_personne(db: BudgetDatabase):
    """Affiche les totaux par personne (mois spécifique ou global)"""
    print("\n--- TOTAUX PAR PERSONNE ---")

    annee_str = input("Année (Entrée pour global): ").strip()

    if not annee_str:
        # Mode global
        totaux = db.obtenir_totaux_globaux()

        if not totaux:
            print("\nAucune transaction dans la base")
            return

        print("\nTotaux sur toute la période:")
        print("-" * 60)
        print(f"{'Auteur':<20} {'Revenus':<15} {'Dépenses':<15} {'Solde':<15}")
        print("-" * 60)

        revenus_total = 0
        depenses_total = 0

        for auteur, montants in totaux.items():
            solde = montants["revenus"] - montants["depenses"]
            revenus_total += montants["revenus"]
            depenses_total += montants["depenses"]
            print(f"{auteur:<20} {montants['revenus']:<15.2f} {montants['depenses']:<15.2f} {solde:<15.2f}")

        print("-" * 60)
        print(f"{'TOTAL':<20} {revenus_total:<15.2f} {depenses_total:<15.2f} {revenus_total - depenses_total:<15.2f}")

    else:
        # Mode mois spécifique
        annee = int(annee_str)
        mois = int(input("Mois (1-12): "))

        totaux = db.obtenir_totaux_mois(annee, mois)

        if not totaux:
            print(f"\nAucune transaction pour {mois:02d}/{annee}")
            return

        print(f"\nTotaux pour {mois:02d}/{annee}:")
        print("-" * 60)
        print(f"{'Auteur':<20} {'Revenus':<15} {'Dépenses':<15} {'Solde':<15}")
        print("-" * 60)

        for auteur, montants in totaux.items():
            solde = montants["revenus"] - montants["depenses"]
            print(f"{auteur:<20} {montants['revenus']:<15.2f} {montants['depenses']:<15.2f} {solde:<15.2f}")


def analyse_depenses_utilite(db: BudgetDatabase, visualizer: BudgetVisualizer):
    """Analyse des dépenses par utilité (Commun/Perso)"""
    print("\n--- ANALYSE DES DÉPENSES PAR UTILITÉ ---")

    choix_periode = input("Période: 1=Mois spécifique, 2=Toute période: ")

    annee = None
    mois = None

    if choix_periode == "1":
        annee = int(input("Année: "))
        mois = int(input("Mois (1-12): "))

    # Récupérer les données
    depenses = db.obtenir_depenses_par_utilite(annee, mois)
    revenus_total = db.obtenir_revenus_totaux(annee, mois)
    total_depenses = sum(depenses.values())

    if total_depenses == 0:
        print("\nAucune dépense pour cette période")
        return

    # Affichage dans le terminal
    periode = f"{mois:02d}/{annee}" if annee and mois else "Toute période"
    print(f"\n=== Dépenses par utilité - {periode} ===")
    print(f"Revenus totaux: {revenus_total:.2f}€")
    print(f"Dépenses totales: {total_depenses:.2f}€")
    print("-" * 80)
    print(f"{'Utilité':<15} {'Montant (€)':<15} {'% du total':<15} {'% des revenus':<20}")
    print("-" * 80)

    for utilite, montant in depenses.items():
        pct_total = (montant / total_depenses) * 100 if total_depenses > 0 else 0
        pct_revenus = (montant / revenus_total) * 100 if revenus_total > 0 else 0
        print(f"{utilite:<15} {montant:<15.2f} {pct_total:<15.1f} {pct_revenus:<20.1f}")

    print("-" * 80)

    # Afficher les graphiques
    print("\nGénération des graphiques...")
    visualizer.graphique_depenses_utilite(annee, mois)


def analyse_revenus_auteur(db: BudgetDatabase, visualizer: BudgetVisualizer):
    """Analyse des revenus par auteur"""
    print("\n--- ANALYSE DES REVENUS PAR AUTEUR ---")

    choix_periode = input("Période: 1=Mois spécifique, 2=Toute période: ")

    annee = None
    mois = None

    if choix_periode == "1":
        annee = int(input("Année: "))
        mois = int(input("Mois (1-12): "))

    # Récupérer les données
    revenus_auteurs = db.obtenir_revenus_par_auteur(annee, mois)
    total_revenus = sum(revenus_auteurs.values())

    if total_revenus == 0:
        print("\nAucun revenu pour cette période")
        return

    # Affichage dans le terminal
    periode = f"{mois:02d}/{annee}" if annee and mois else "Toute période"
    print(f"\n=== Revenus par auteur - {periode} ===")
    print(f"Revenus totaux: {total_revenus:.2f}€")
    print("-" * 60)
    print(f"{'Auteur':<20} {'Montant (€)':<20} {'% du total':<20}")
    print("-" * 60)

    for auteur, montant in sorted(revenus_auteurs.items(), key=lambda x: x[1], reverse=True):
        pct = (montant / total_revenus) * 100
        print(f"{auteur:<20} {montant:<20.2f} {pct:<20.1f}")

    print("-" * 60)

    # Afficher les graphiques
    print("\nGénération des graphiques...")
    visualizer.graphique_revenus_auteur(annee, mois)


def graphique_evolution(visualizer: BudgetVisualizer):
    """Affiche l'évolution mensuelle"""
    print("\n--- ÉVOLUTION MENSUELLE ---")
    annee = int(input("Année: "))

    print("\nGénération des graphiques...")
    visualizer.graphique_evolution_mensuelle(annee)


def graphique_comparatif(visualizer: BudgetVisualizer):
    """Affiche le comparatif par auteur"""
    print("\n--- COMPARATIF PAR AUTEUR ---")

    choix_periode = input("Période: 1=Mois spécifique, 2=Toute période: ")

    annee = None
    mois = None

    if choix_periode == "1":
        annee = int(input("Année: "))
        mois = int(input("Mois (1-12): "))

    print("\nGénération des graphiques...")
    visualizer.graphique_comparatif_auteurs(annee, mois)


def main():
    """Fonction principale"""
    print("Initialisation de la base de données...")

    with BudgetDatabase("budget.db") as db:
        visualizer = BudgetVisualizer(db)

        while True:
            afficher_menu()
            choix = input("\nVotre choix: ").strip()

            try:
                if choix == "1":
                    ajouter_transaction(db)
                elif choix == "2":
                    modifier_transaction(db)
                elif choix == "3":
                    supprimer_transaction(db)
                elif choix == "4":
                    voir_transactions_mois(db)
                elif choix == "5":
                    lister_revenus_mois(db)
                elif choix == "6":
                    lister_depenses_mois(db)
                elif choix == "7":
                    voir_totaux_par_personne(db)
                elif choix == "8":
                    analyse_depenses_utilite(db, visualizer)
                elif choix == "9":
                    analyse_revenus_auteur(db, visualizer)
                elif choix == "10":
                    graphique_evolution(visualizer)
                elif choix == "11":
                    graphique_comparatif(visualizer)
                elif choix == "12":
                    print("\nAu revoir!")
                    break
                else:
                    print("\n✗ Choix invalide")
            except Exception as e:
                print(f"\n✗ Erreur: {e}")


if __name__ == "__main__":
    main()
