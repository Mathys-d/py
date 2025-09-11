import csv
import json

def lire_portfolio_csv(nom_fichier: str):
    with open(nom_fichier, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)

def lire_portfolio_json(nom_fichier: str):
    with open(nom_fichier, newline='') as f:
        reader = json.load(f)
        parcourir(reader)


def parcourir(obj, indent=0):
    prefix = "  " * indent

    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{prefix}Clé: {k}")
            parcourir(v, indent + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            print(f"{prefix}Élément [{i}]")
            parcourir(item, indent + 1)
    else:
        print(f"{prefix}Valeur: {obj}")




def afficher_portfolio():
    lire_portfolio_json("portfolio_sample.json")
    print("\n")
    lire_portfolio_csv("portfolio_sample.csv")

afficher_portfolio()