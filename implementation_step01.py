import csv
import json
from typing import Dict, List, Any


def lire_portfolio_csv(nom_fichier: str) -> List[Dict[str, Any]]:
    portfolio = []
    
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            lecteur_csv = csv.DictReader(fichier)
            
            for ligne in lecteur_csv:
                position = {
                    'symbol': ligne['symbol'],
                    'quantity': int(ligne['quantity']),
                    'purchase_price': float(ligne['purchase_price']),
                    'purchase_date': ligne['purchase_date']
                }
                portfolio.append(position)
                
    except FileNotFoundError:
        print(f"Erreur: Le fichier {nom_fichier} n'a pas été trouvé.")
        return []
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV: {e}")
        return []
    
    return portfolio


def lire_portfolio_json(nom_fichier: str) -> Dict[str, Any]:
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as fichier:
            portfolio = json.load(fichier)
        return portfolio
        
    except FileNotFoundError:
        print(f"Erreur: Le fichier {nom_fichier} n'a pas été trouvé.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Erreur: Fichier JSON invalide - {e}")
        return {}
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier JSON: {e}")
        return {}


def afficher_portfolio(portfolio: Any) -> None:
# Gestion des deux formats (CSV = liste, JSON = dict)
    if isinstance(portfolio, dict) and 'positions' in portfolio:
        # Format JSON
        positions = portfolio['positions']
        print("Portfolio chargé depuis JSON")

    else:
        # Format CSV (liste)
        positions = portfolio
        print("Portfolio chargé depuis CSV")
        print("-" * 60)
    
    
    # Affichage des positions
    total_value = 0
    print(f"{'SYMBOLE':<8} {'QTÉ':<5} {'PRIX':<10} {'VALEUR':<12} {'DATE':<12}")
    print("-" * 60)
    
    for position in positions:
        symbol = position['symbol']
        quantity = position['quantity']
        price = position['purchase_price']
        value = quantity * price
        date = position['purchase_date']
        
        print(f"{symbol:<8} {quantity:<5} {price:<10.2f} {value:<12.2f} {date:<12}")
        total_value += value
    
    print("-" * 60)
    print(f"VALEUR TOTALE DU PORTFOLIO: {total_value}€")
    print(f"NOMBRE DE POSITIONS: {len(positions)}")
    print("=" * 60)


def main():
    # Test du chargement CSV
    print("1️⃣  Chargement depuis CSV:")
    portfolio_csv = lire_portfolio_csv('portfolio_sample.csv')
    if portfolio_csv:
        afficher_portfolio(portfolio_csv)
    
    print("\n" + "="*60 + "\n")
    
    # Test du chargement JSON
    print("2️⃣  Chargement depuis JSON:")
    portfolio_json = lire_portfolio_json('portfolio_sample.json')
    if portfolio_json:
        afficher_portfolio(portfolio_json)


if __name__ == "__main__":
    main()
