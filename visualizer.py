from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

from database_manager import BudgetDatabase


class BudgetVisualizer:
    """Classe pour créer des visualisations graphiques du budget"""

    def __init__(self, db: BudgetDatabase):
        """
        Initialise le visualiseur

        Args:
            db: Instance de BudgetDatabase
        """
        self.db = db
        plt.style.use("seaborn-v0_8-darkgrid")

    def graphique_depenses_utilite(self, annee: int = None, mois: int = None):
        """
        Crée un camembert des dépenses par utilité (Commun/Perso)

        Args:
            annee: Année optionnelle pour filtrer
            mois: Mois optionnel pour filtrer
        """
        depenses = self.db.obtenir_depenses_par_utilite(annee, mois)
        revenus_total = self.db.obtenir_revenus_totaux(annee, mois)

        if sum(depenses.values()) == 0:
            print("Aucune dépense à afficher")
            return

        # Préparer les données
        labels = []
        values = []
        percentages_revenus = []

        for utilite, montant in depenses.items():
            if montant > 0:
                labels.append(utilite)
                values.append(montant)
                if revenus_total > 0:
                    pct = (montant / revenus_total) * 100
                    percentages_revenus.append(pct)
                else:
                    percentages_revenus.append(0)

        # Créer la figure avec 2 sous-graphiques
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Camembert des montants
        # colors = ["#ff9999", "#66b3ff"]
        colors = ["#a9cbd7", "#ffc5d3"]
        explode = (0.05, 0.05)

        wedges, texts, autotexts = ax1.pie(
            values, labels=labels, autopct="%1.1f%%", colors=colors, explode=explode, startangle=90
        )
        ax1.set_title("Répartition des dépenses par utilité\n(Montants)", fontsize=14, fontweight="bold")

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(12)
            autotext.set_fontweight("bold")

        # Graphique en barres : pourcentage par rapport aux revenus
        x_pos = np.arange(len(labels))
        bars = ax2.bar(x_pos, percentages_revenus, color=colors, alpha=0.7, edgecolor="black")
        ax2.set_xlabel("Utilité", fontsize=12, fontweight="bold")
        ax2.set_ylabel("% des revenus", fontsize=12, fontweight="bold")
        ax2.set_title("Dépenses en % des revenus totaux", fontsize=14, fontweight="bold")
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(labels)
        ax2.axhline(y=100, color="r", linestyle="--", linewidth=2, label="100% des revenus")
        ax2.legend()

        # Ajouter les valeurs sur les barres
        for i, (bar, val, pct) in enumerate(zip(bars, values, percentages_revenus)):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{val:.2f}€\n({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        periode = f" - {mois:02d}/{annee}" if annee and mois else " - Toute période"
        fig.suptitle(f"Analyse des dépenses{periode}", fontsize=16, fontweight="bold")

        plt.tight_layout()
        plt.show()

    def graphique_revenus_auteur(self, annee: int = None, mois: int = None):
        """
        Crée des graphiques montrant la contribution de chaque auteur aux revenus

        Args:
            annee: Année optionnelle pour filtrer
            mois: Mois optionnel pour filtrer
        """
        revenus_auteurs = self.db.obtenir_revenus_par_auteur(annee, mois)
        total_revenus = sum(revenus_auteurs.values())

        if total_revenus == 0:
            print("Aucun revenu à afficher")
            return

        # Préparer les données
        auteurs = list(revenus_auteurs.keys())
        montants = list(revenus_auteurs.values())
        percentages = [(m / total_revenus) * 100 for m in montants]

        # Créer la figure avec 2 sous-graphiques
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Camembert des pourcentages
        colors = ["#a9cbd7", "#ffc5d3"]
        explode = tuple([0.05] * len(auteurs))

        wedges, texts, autotexts = ax1.pie(
            percentages, labels=auteurs, autopct="%1.1f%%", colors=colors, explode=explode, startangle=90
        )
        ax1.set_title("Contribution aux revenus totaux\n(Pourcentage)", fontsize=14, fontweight="bold")

        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(12)
            autotext.set_fontweight("bold")

        # Graphique en barres des montants
        x_pos = np.arange(len(auteurs))
        bars = ax2.bar(x_pos, montants, color=colors, alpha=0.7, edgecolor="black")
        ax2.set_xlabel("Auteur", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Montant (€)", fontsize=12, fontweight="bold")
        ax2.set_title("Revenus par auteur\n(Montants)", fontsize=14, fontweight="bold")
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(auteurs, rotation=45, ha="right")

        # Ajouter les valeurs sur les barres
        for bar, montant, pct in zip(bars, montants, percentages):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{montant:.2f}€\n({pct:.1f}%)",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        periode = f" - {mois:02d}/{annee}" if annee and mois else " - Toute période"
        fig.suptitle(
            f"Analyse des revenus par auteur{periode}\nTotal: {total_revenus:.2f}€", fontsize=16, fontweight="bold"
        )

        plt.tight_layout()
        plt.show()

    def graphique_evolution_mensuelle(self, annee: int):
        """
        Crée un graphique montrant l'évolution des revenus/dépenses sur l'année

        Args:
            annee: Année à analyser
        """
        mois_labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]

        revenus_mensuels = []
        depenses_mensuelles = []
        soldes_mensuels = []

        for mois in range(1, 13):
            revenus = self.db.obtenir_revenus_totaux(annee, mois)
            depenses_utilite = self.db.obtenir_depenses_par_utilite(annee, mois)
            depenses = sum(depenses_utilite.values())

            revenus_mensuels.append(revenus)
            depenses_mensuelles.append(depenses)
            soldes_mensuels.append(revenus - depenses)

        # Créer la figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # Graphique 1: Revenus vs Dépenses
        x = np.arange(len(mois_labels))
        width = 0.35

        bars1 = ax1.bar(
            x - width / 2, revenus_mensuels, width, label="Revenus", color="#2ecc71", alpha=0.8, edgecolor="black"
        )
        bars2 = ax1.bar(
            x + width / 2, depenses_mensuelles, width, label="Dépenses", color="#e74c3c", alpha=0.8, edgecolor="black"
        )

        ax1.set_xlabel("Mois", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Montant (€)", fontsize=12, fontweight="bold")
        ax1.set_title(f"Revenus et Dépenses mensuels - {annee}", fontsize=14, fontweight="bold")
        ax1.set_xticks(x)
        ax1.set_xticklabels(mois_labels)
        ax1.legend(fontsize=11)
        ax1.grid(axis="y", alpha=0.3)

        # Graphique 2: Solde mensuel
        colors_solde = ["#2ecc71" if s >= 0 else "#e74c3c" for s in soldes_mensuels]
        bars3 = ax2.bar(x, soldes_mensuels, color=colors_solde, alpha=0.8, edgecolor="black")

        ax2.axhline(y=0, color="black", linestyle="-", linewidth=1)
        ax2.set_xlabel("Mois", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Solde (€)", fontsize=12, fontweight="bold")
        ax2.set_title(f"Solde mensuel - {annee}", fontsize=14, fontweight="bold")
        ax2.set_xticks(x)
        ax2.set_xticklabels(mois_labels)
        ax2.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.show()

    def graphique_comparatif_auteurs(self, annee: int = None, mois: int = None):
        """
        Crée un graphique comparatif revenus/dépenses par auteur

        Args:
            annee: Année optionnelle pour filtrer
            mois: Mois optionnel pour filtrer
        """
        if annee and mois:
            totaux = self.db.obtenir_totaux_mois(annee, mois)
        else:
            totaux = self.db.obtenir_totaux_globaux()

        if not totaux:
            print("Aucune donnée à afficher")
            return

        auteurs = list(totaux.keys())
        revenus = [totaux[a]["revenus"] for a in auteurs]
        depenses = [totaux[a]["depenses"] for a in auteurs]
        soldes = [r - d for r, d in zip(revenus, depenses)]

        # Créer la figure
        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(auteurs))
        width = 0.25

        bars1 = ax.bar(x - width, revenus, width, label="Revenus", color="#2ecc71", alpha=0.8, edgecolor="black")
        bars2 = ax.bar(x, depenses, width, label="Dépenses", color="#e74c3c", alpha=0.8, edgecolor="black")
        bars3 = ax.bar(x + width, soldes, width, label="Solde", color="#3498db", alpha=0.8, edgecolor="black")

        ax.set_xlabel("Auteur", fontsize=12, fontweight="bold")
        ax.set_ylabel("Montant (€)", fontsize=12, fontweight="bold")

        periode = f" - {mois:02d}/{annee}" if annee and mois else " - Toute période"
        ax.set_title(f"Comparatif par auteur{periode}", fontsize=14, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(auteurs)
        ax.legend(fontsize=11)
        ax.axhline(y=0, color="black", linestyle="-", linewidth=1)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.show()
