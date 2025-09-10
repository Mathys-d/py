import json
from dataclasses import dataclass
from datetime import datetime
from collections import namedtuple

Position = namedtuple('Position', ['symbol', 'quantity', 'purchase_price', 'purchase_date'])
Transaction = namedtuple('Transaction', ['date', 'symbol', 'quantity', 'price', 'type'])

@dataclass
class Portfolio:
    positions: list[Position]
    transactions: list[Transaction]


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


def afficher_positions(positions):
    for p in positions:
        print(p)


def afficher_portfolio():
    positions = lire_portfolio_json("portfolio_sample.json")
    portfolio = Portfolio(positions=positions, transactions=[]) 
    afficher_positions(portfolio.positions)


afficher_portfolio()