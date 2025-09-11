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

valeur_position = lambda pos: pos.quantity * pos.purchase_price
gain_absolu = lambda pos, prix_actuel: (prix_actuel - pos.purchase_price) * pos.quantity if pos.purchase_price > 0 else 0
rendement_pourcent = lambda pos, prix_actuel: ((prix_actuel - pos.purchase_price) / pos.purchase_price) * 100 if pos.purchase_price > 0 else 0
valeur_actuelle = lambda pos, prix_actuel: pos.quantity * prix_actuel
poids_portfolio = lambda pos, prix_actuel, total: (valeur_actuelle(pos, prix_actuel) / total) * 100 if total > 0 else 0

def convertir_vers_positions(portfolio_dict):
    return Position(
        portfolio_dict['symbol'],
        portfolio_dict['quantity'],
        portfolio_dict['purchase_price'],
        datetime.strptime(portfolio_dict['purchase_date'], "%Y-%m-%d")
    )

def parcourir(obj, positions):
    if isinstance(obj, dict):
        if {"symbol", "quantity", "purchase_price", "purchase_date"} <= obj.keys():
            positions.append(convertir_vers_positions(obj))
        else:
            for _, v in obj.items():
                parcourir(v, positions)
    elif isinstance(obj, list):
        for item in obj:
            parcourir(item, positions)

def lire_portfolio_json(nom_fichier: str):
    positions = []
    with open(nom_fichier, newline='') as f:
        reader = json.load(f)
        parcourir(reader, positions)
    return positions


def lire_prix_actuels(fichier_csv):
    prix_actuels = {}
    with open(fichier_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbole = row["symbol"].strip()
            prix = float(row["purchase_price"])
            prix_actuels[symbole] = prix
    return prix_actuels


def calculer_valeurs_positions(positions):
    return list(map(valeur_position, positions))

def calculer_gains_portfolio(positions, prix_actuels_dict):
    return list(map(lambda p: gain_absolu(p, prix_actuels_dict.get(p.symbol, p.purchase_price)), positions))

def calculer_rendements_portfolio(positions, prix_actuels_dict):
    return list(map(lambda p: rendement_pourcent(p, prix_actuels_dict.get(p.symbol, p.purchase_price)), positions))

def generer_rapport_complet(positions, prix_actuels_dict):
    valeurs = calculer_valeurs_positions(positions)
    gains = calculer_gains_portfolio(positions, prix_actuels_dict)
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
    positions = lire_portfolio_json("portfolio_sample.json")
    portfolio = Portfolio(positions=positions, transactions=[])
    afficher_positions(portfolio.positions)


def afficher_rapport_global():
    positions = lire_portfolio_json("portfolio_sample.json")
    prix_actuels = lire_prix_actuels("portfolio_actual_prices_sample.csv")
    rapport = generer_rapport_complet(positions, prix_actuels)
    print("Valeurs d'achat :", rapport["valeurs"])
    print("Gains actuels :", rapport["gains"])
    print("Rendements :", [round(r, 2) for r in rapport["rendements"]])


if __name__ == "__main__":
    afficher_portfolio()
    afficher_rapport_global()
