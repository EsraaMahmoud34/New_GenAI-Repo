import os
from langchain.tools import tool
import json
from pathlib import Path
from data.routin_rules import ROUTINE_RULES


#i will build a many agent for skin care cosmetics and routin
with open(Path(__file__).resolve().parent / "data" / "products.json", 'r', encoding='utf-8') as f:
    products=json.load(f)

@tool
def get_product(skin_type:str, category:str, max_price:float,concerns:list):
    """get a skin care product recommendations based on the skin type, category, concerns and max price
    Args:
        skin_type (str): The skin type of the user (e.g., oily, dry, combination, sensitive).
        category (str): The category of the product (e.g., cleanser, moisturizer, serum).
        max_price (float): The maximum price the user is willing to pay.
        concerns (list): A list of skin concerns (e.g., acne, wrinkles, dark spots)."""
    recommendations=[]
    for product in products:
        if skin_type in product['skin_types'] and product['category']==category and product['price']<=max_price:
            if all(concern in product['concerns'] for concern in concerns):
                recommendations.append(product)
    if not recommendations:
        return "No products found matching the given requirements."

    return str(recommendations)
@tool
def build_routine(skin_type:str, concerns:list):
    """Build a skincare routine based on the skin type and concerns.
    Args:
        skin_type (str): The skin type of the user (e.g., oily, dry, combination, sensitive).
        concerns (list): A list of skin concerns (e.g., acne, wrinkles, dark spots)."""
    morning=ROUTINE_RULES["base_morning"]
    night=ROUTINE_RULES["base_night"]
    for concern in concerns:
        if concern in ROUTINE_RULES:
            rules=ROUTINE_RULES[concern]
            if "morning" in rules:
                morning.extend(rules["morning"])
            if "night" in rules:
                night.extend(rules["night"])
    #i want to return str

    return str({
        "morning": morning,
        "night": night
    })

@tool
def compare_products(products:list[dict], skin_type:str, concerns:list, max_price:float)->list[dict]:
    """if the get product tool returns more than one product so this tool will compare them based on the skin type, concerns, and max price.
    Args:
        products (list): A list of skincare products to compare.
        skin_type (str): The skin type of the user (e.g., oily, dry, combination, sensitive).
        concerns (list): A list of skin concerns (e.g., acne, wrinkles, dark spots).
        max_price (float): The maximum price the user is willing to pay."""
    results=[]
    for product in products:
        score=0
        reasons=[]
        if skin_type in product['skin_types']:
            score+=1
            reasons.append("matches skin type")
        matched_concers=[concern for concern in concerns if concern in product['concerns']]
        if matched_concers:
            score+=len(matched_concers)*2
            reasons.append(f"matches concerns: {', '.join(matched_concers)}")
        if matched_concers:
            reasons.append(f"matches concerns: {', '.join(matched_concers)}")
        if product['price']<=max_price:
            score+=1
            reasons.append("within budget")
        results.append({
        "name": product["name"],
        "price": product["price"],
        "score": score,
        "reasons": reasons
       })

    # Highest score first
    results.sort(
        key=lambda product: product["score"],
        reverse=True
    )

    if not results:
        return "No products found matching the given requirements."

    return str(results)
