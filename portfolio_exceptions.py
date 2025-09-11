import json
import csv
from dataclasses import dataclass
from datetime import datetime
from collections import namedtuple



Position = namedtuple('Position', ['symbol', 'quantity', 'purchase_price', 'purchase_date'])
Transaction = namedtuple('Transaction', ['date', 'symbol', 'quantity', 'price', 'type'])

@dataclass
class Portfolio:
    positions: list[Position]
    transactions: list[Transaction]



class ErreurDonneesPortfolio(Exception):
    pass



valeur_position = lambda pos: max(pos.quantity * pos.purchase_price, 0)

gain_absolu = lambda pos, prix_actuel: (
    (prix_actuel - pos.purchase_price) * pos.quantity
    if pos.purchase_price > 0 and pos.quantity > 0 else 0
)

rendement_pourcent = lambda pos, prix_actuel: (
    ((prix_actuel - pos.purchase_price) / pos.purchase_price) * 100
    if pos.purchase_price > 0 and pos.quantity > 0 else 0
)

valeur_actuelle = lambda pos, prix_actuel: max(pos.quantity * prix_actuel, 0)

poids_portfolio = lambda pos, prix_actuel, total: (
    (valeur_actuelle(pos, prix_actuel) / total) * 100 if total > 0 else 0
)



def convertir_vers_positions(portfolio_dict):
    try:
        quantity = float(portfolio_dict['quantity'])
        purchase_price = float(portfolio_dict['purchase_price'])
        if quantity <= 0 or purchase_price < 0:
            raise ErreurDonneesPortfolio(f"Données invalides pour {portfolio_dict.get('symbol', 'UNKNOWN')}")
        return Position(
            portfolio_dict['symbol'],
            quantity,
            purchase_price,
            datetime.strptime(portfolio_dict['purchase_date'], "%Y-%m-%d")
        )
    except KeyError as e:
        raise ErreurDonneesPortfolio(f"Clé manquante: {e}")
    except ValueError as e:
        raise ErreurDonneesPortfolio(f"Erreur de conversion pour {portfolio_dict.get('symbol', 'UNKNOWN')}: {e}")

def parcourir(obj, positions):
    if isinstance(obj, dict):
        if {"symbol", "quantity", "purchase_price", "purchase_date"} <= obj.keys():
            try:
                positions.append(convertir_vers_positions(obj))
            except ErreurDonneesPortfolio as e:
                print(e)
        else:
            for _, v in obj.items():
                parcourir(v, positions)
    elif isinstance(obj, list):
        for item in obj:
            parcourir(item, positions)

def lire_portfolio_json(nom_fichier: str):
    positions = []
    try:
        with open(nom_fichier, newline='') as f:
            reader = json.load(f)
            parcourir(reader, positions)
    except FileNotFoundError:
        print(f" Fichier {nom_fichier} introuvable")
    except json.JSONDecodeError as e:
        print(f" Erreur JSON: {e}")
    return positions

def charger_portfolio_securise(fichier):
    return lire_portfolio_json(fichier)



def lire_prix_actuels(fichier_csv):
    prix_actuels = {}
    try:
        with open(fichier_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                symbole = row["symbol"].strip()
                prix = float(row["purchase_price"])
                prix_actuels[symbole] = prix
    except FileNotFoundError:
        print(f" Fichier {fichier_csv} introuvable")
    except Exception as e:
        print(f" Erreur lecture CSV: {e}")
    return prix_actuels



def calculer_gains_securise(positions, prix_actuels_dict):
    gains = []
    for p in positions:
        prix_actuel = prix_actuels_dict.get(p.symbol)
        if prix_actuel is None:
            print(f" Prix actuel manquant pour {p.symbol}, utilisation du prix d'achat")
            prix_actuel = p.purchase_price
        gains.append(gain_absolu(p, prix_actuel))
    return gains



def calculer_valeurs_positions(positions):
    return list(map(valeur_position, positions))

def calculer_gains_portfolio(positions, prix_actuels_dict):
    return list(map(lambda p: gain_absolu(p, prix_actuels_dict.get(p.symbol, p.purchase_price)), positions))

def calculer_rendements_portfolio(positions, prix_actuels_dict):
    return list(map(lambda p: rendement_pourcent(p, prix_actuels_dict.get(p.symbol, p.purchase_price)), positions))

def generer_rapport_complet(positions, prix_actuels_dict):
    valeurs = calculer_valeurs_positions(positions)
    gains = calculer_gains_securise(positions, prix_actuels_dict)
    rendements = calculer_rendements_portfolio(positions, prix_actuels_dict)
    return {"valeurs": valeurs, "gains": gains, "rendements": rendements}



def afficher_positions(positions, prix_actuels_csv="portfolio_actual_prices_sample.csv"):
    prix_actuels = lire_prix_actuels(prix_actuels_csv)
    total_valeur_actuelle = sum(valeur_actuelle(p, prix_actuels.get(p.symbol, p.purchase_price)) for p in positions)

    for p in positions:
        prix_actuel = prix_actuels.get(p.symbol, p.purchase_price)
        print(f"{p.symbol}")
        print(f"Quantité : {p.quantity}")
        print(f"Prix d'achat : {p.purchase_price}")
        print(f"Valeur d'achat : {valeur_position(p)}")
        print(f"Valeur actuelle : {valeur_actuelle(p, prix_actuel)}")
        print(f"Gain absolu : {gain_absolu(p, prix_actuel)}")
        print(f"Rendement % : {rendement_pourcent(p, prix_actuel):.2f}%")
        print(f"Poids dans portfolio : {poids_portfolio(p, prix_actuel, total_valeur_actuelle):.2f}%")
        print()

def afficher_portfolio():
    positions = charger_portfolio_securise("portfolio_sample.json")
    portfolio = Portfolio(positions=positions, transactions=[])
    afficher_positions(portfolio.positions)

def afficher_rapport_global():
    positions = charger_portfolio_securise("portfolio_sample.json")
    prix_actuels = lire_prix_actuels("portfolio_actual_prices_sample.csv")
    rapport = generer_rapport_complet(positions, prix_actuels)
    print("Valeurs d'achat :", rapport["valeurs"])
    print("Gains actuels :", rapport["gains"])
    print("Rendements :", [round(r, 2) for r in rapport["rendements"]])


if __name__ == "__main__":
    print("=== Test avec données corrompues ===")
    positions_problematiques = [
        Position('AAPL', 10, 0.0, '2023-01-15'),      # Prix d'achat = 0 !
        Position('INVALID', 5, 100.0, '2023-02-01'),  # Symbole inexistant
        Position('GOOGL', -10, 2500.0, '2023-03-01')  # Quantité négative !
    ]
    prix_actuels_fictifs = {'AAPL': 150, 'GOOGL': 2600}

    print("Gains sécurisés : ", calculer_gains_securise(positions_problematiques, prix_actuels_fictifs))