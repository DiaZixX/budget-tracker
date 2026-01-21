import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class BudgetDatabase:
    """Gestionnaire de base de données pour le suivi budgétaire"""

    def __init__(self, db_name: str = "budget.db"):
        """
        Initialise la connexion à la base de données

        Args:
            db_name: Nom du fichier de base de données
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Établit la connexion à la base de données"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def _create_table(self):
        """Crée la table des transactions si elle n'existe pas"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                Montant REAL NOT NULL,
                Type TEXT NOT NULL CHECK(Type IN ('Revenu', 'Depense')),
                Utilite TEXT NOT NULL CHECK(Utilite IN ('Commun', 'Perso')),
                Description TEXT,
                Auteur TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def ajouter_entree(
        self, date: str, montant: float, type_transaction: str, utilite: str, description: str, auteur: str
    ) -> int:
        """
        Ajoute une nouvelle transaction

        Args:
            date: Date au format YYYY-MM-DD
            montant: Montant de la transaction
            type_transaction: 'Revenu' ou 'Depense'
            utilite: 'Commun' ou 'Perso'
            description: Description de la transaction
            auteur: Nom de l'auteur

        Returns:
            ID de la transaction créée
        """
        self.cursor.execute(
            """
            INSERT INTO transactions (Date, Montant, Type, Utilite, Description, Auteur)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (date, montant, type_transaction, utilite, description, auteur),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def supprimer_entree(self, transaction_id: int) -> bool:
        """
        Supprime une transaction par son ID

        Args:
            transaction_id: ID de la transaction à supprimer

        Returns:
            True si la suppression a réussi, False sinon
        """
        self.cursor.execute("DELETE FROM transactions WHERE ID = ?", (transaction_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def modifier_entree(
        self,
        transaction_id: int,
        date: str = None,
        montant: float = None,
        type_transaction: str = None,
        utilite: str = None,
        description: str = None,
        auteur: str = None,
    ) -> bool:
        """
        Modifie une transaction existante

        Args:
            transaction_id: ID de la transaction à modifier
            date: Nouvelle date (optionnel)
            montant: Nouveau montant (optionnel)
            type_transaction: Nouveau type (optionnel)
            utilite: Nouvelle utilité (optionnel)
            description: Nouvelle description (optionnel)
            auteur: Nouvel auteur (optionnel)

        Returns:
            True si la modification a réussi, False sinon
        """
        # Récupérer la transaction actuelle
        self.cursor.execute("SELECT * FROM transactions WHERE ID = ?", (transaction_id,))
        transaction = self.cursor.fetchone()

        if not transaction:
            return False

        # Utiliser les valeurs actuelles si aucune nouvelle valeur n'est fournie
        colonnes = [desc[0] for desc in self.cursor.description]
        trans_dict = dict(zip(colonnes, transaction))

        new_date = date if date is not None else trans_dict["Date"]
        new_montant = montant if montant is not None else trans_dict["Montant"]
        new_type = type_transaction if type_transaction is not None else trans_dict["Type"]
        new_utilite = utilite if utilite is not None else trans_dict["Utilite"]
        new_description = description if description is not None else trans_dict["Description"]
        new_auteur = auteur if auteur is not None else trans_dict["Auteur"]

        self.cursor.execute(
            """
            UPDATE transactions 
            SET Date = ?, Montant = ?, Type = ?, Utilite = ?, Description = ?, Auteur = ?
            WHERE ID = ?
        """,
            (new_date, new_montant, new_type, new_utilite, new_description, new_auteur, transaction_id),
        )

        self.conn.commit()
        return self.cursor.rowcount > 0

    def obtenir_transaction_par_id(self, transaction_id: int) -> Optional[Dict]:
        """
        Récupère une transaction par son ID

        Args:
            transaction_id: ID de la transaction

        Returns:
            Dictionnaire contenant la transaction ou None
        """
        self.cursor.execute("SELECT * FROM transactions WHERE ID = ?", (transaction_id,))
        row = self.cursor.fetchone()

        if row:
            colonnes = [desc[0] for desc in self.cursor.description]
            return dict(zip(colonnes, row))
        return None

    def obtenir_transactions_mois(
        self, annee: int, mois: int, type_transaction: Optional[str] = None, auteur: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère les transactions d'un mois spécifique

        Args:
            annee: Année (ex: 2024)
            mois: Mois (1-12)
            type_transaction: Filtre optionnel 'Revenu' ou 'Depense'
            auteur: Filtre optionnel par auteur

        Returns:
            Liste de dictionnaires contenant les transactions
        """
        date_debut = f"{annee}-{mois:02d}-01"
        if mois == 12:
            date_fin = f"{annee + 1}-01-01"
        else:
            date_fin = f"{annee}-{mois + 1:02d}-01"

        query = "SELECT * FROM transactions WHERE Date >= ? AND Date < ?"
        params = [date_debut, date_fin]

        if type_transaction:
            query += " AND Type = ?"
            params.append(type_transaction)

        if auteur:
            query += " AND Auteur = ?"
            params.append(auteur)

        self.cursor.execute(query, params)
        colonnes = [desc[0] for desc in self.cursor.description]

        return [dict(zip(colonnes, row)) for row in self.cursor.fetchall()]

    def obtenir_totaux_mois(self, annee: int, mois: int) -> Dict[str, Dict[str, float]]:
        """
        Calcule les totaux revenus/dépenses par personne pour un mois

        Args:
            annee: Année
            mois: Mois (1-12)

        Returns:
            Dict avec structure {auteur: {'revenus': montant, 'depenses': montant}}
        """
        transactions = self.obtenir_transactions_mois(annee, mois)
        totaux = {}

        for trans in transactions:
            auteur = trans["Auteur"]
            if auteur not in totaux:
                totaux[auteur] = {"revenus": 0.0, "depenses": 0.0}

            if trans["Type"] == "Revenu":
                totaux[auteur]["revenus"] += trans["Montant"]
            else:
                totaux[auteur]["depenses"] += trans["Montant"]

        return totaux

    def obtenir_totaux_globaux(self) -> Dict[str, Dict[str, float]]:
        """
        Calcule les totaux revenus/dépenses par personne sur toute la base

        Returns:
            Dict avec structure {auteur: {'revenus': montant, 'depenses': montant}}
        """
        self.cursor.execute(
            """
            SELECT Auteur, Type, SUM(Montant) as Total
            FROM transactions
            GROUP BY Auteur, Type
        """
        )

        totaux = {}
        for row in self.cursor.fetchall():
            auteur, type_trans, total = row
            if auteur not in totaux:
                totaux[auteur] = {"revenus": 0.0, "depenses": 0.0}

            if type_trans == "Revenu":
                totaux[auteur]["revenus"] = total
            else:
                totaux[auteur]["depenses"] = total

        return totaux

    def obtenir_depenses_par_utilite(self, annee: int = None, mois: int = None) -> Dict[str, float]:
        """
        Calcule les dépenses par utilité (Commun/Perso)

        Args:
            annee: Filtre optionnel par année
            mois: Filtre optionnel par mois

        Returns:
            Dict avec structure {'Commun': montant, 'Perso': montant}
        """
        query = "SELECT Utilite, SUM(Montant) as Total FROM transactions WHERE Type = 'Depense'"
        params = []

        if annee and mois:
            date_debut = f"{annee}-{mois:02d}-01"
            if mois == 12:
                date_fin = f"{annee + 1}-01-01"
            else:
                date_fin = f"{annee}-{mois + 1:02d}-01"
            query += " AND Date >= ? AND Date < ?"
            params = [date_debut, date_fin]

        query += " GROUP BY Utilite"

        self.cursor.execute(query, params)

        result = {"Commun": 0.0, "Perso": 0.0}
        for row in self.cursor.fetchall():
            utilite, total = row
            result[utilite] = total

        return result

    def obtenir_revenus_totaux(self, annee: int = None, mois: int = None) -> float:
        """
        Calcule le total des revenus

        Args:
            annee: Filtre optionnel par année
            mois: Filtre optionnel par mois

        Returns:
            Montant total des revenus
        """
        query = "SELECT SUM(Montant) FROM transactions WHERE Type = 'Revenu'"
        params = []

        if annee and mois:
            date_debut = f"{annee}-{mois:02d}-01"
            if mois == 12:
                date_fin = f"{annee + 1}-01-01"
            else:
                date_fin = f"{annee}-{mois + 1:02d}-01"
            query += " AND Date >= ? AND Date < ?"
            params = [date_debut, date_fin]

        self.cursor.execute(query, params)
        result = self.cursor.fetchone()[0]
        return result if result else 0.0

    def obtenir_revenus_par_auteur(self, annee: int = None, mois: int = None) -> Dict[str, float]:
        """
        Calcule les revenus par auteur

        Args:
            annee: Filtre optionnel par année
            mois: Filtre optionnel par mois

        Returns:
            Dict avec structure {auteur: montant}
        """
        query = "SELECT Auteur, SUM(Montant) as Total FROM transactions WHERE Type = 'Revenu'"
        params = []

        if annee and mois:
            date_debut = f"{annee}-{mois:02d}-01"
            if mois == 12:
                date_fin = f"{annee + 1}-01-01"
            else:
                date_fin = f"{annee}-{mois + 1:02d}-01"
            query += " AND Date >= ? AND Date < ?"
            params = [date_debut, date_fin]

        query += " GROUP BY Auteur"

        self.cursor.execute(query, params)

        result = {}
        for row in self.cursor.fetchall():
            auteur, total = row
            result[auteur] = total

        return result

    def fermer(self):
        """Ferme la connexion à la base de données"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Support du context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fermeture automatique avec context manager"""
        self.fermer()
