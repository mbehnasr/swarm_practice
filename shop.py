import json
import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv
import requests

load_dotenv()
app = FastAPI()

CARTS_FILE = "carts.json"
ORDER_FILE = "order.json"
ACCOUNT_MICROSERVICE_URL = os.getenv("ACCOUNT_MICROSERVICE_URL")

PRODUCTS = "products.json"

class CartItem(BaseModel):
    item_id: str
    quantity: int

def load_products_from_file():
    try:
        with open(PRODUCTS, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return{}

def write_products_to_file(data, file_path):
    try:
        with open(file_path, "w") as file:
            json.dump(data, file)
    except IOError as e:
        print("Error writing to file:", str(e))

def load_carts_from_file() -> Dict[str, Dict[str, int]]:
    try:
        with open(CARTS_FILE, "r") as file:
            carts = json.load(file)
            return carts
    except FileNotFoundError:
        return {}


def save_carts_to_file(carts: Dict[str, Dict[str, int]]):
    with open(CARTS_FILE, "w") as file:
        json.dump(carts, file)

def load_orders_from_file() -> Dict[str, Dict[str, int]]:
    try:
        with open(ORDER_FILE, "r") as file:
            carts = json.load(file)
            return orders
    except FileNotFoundError:
        return {}


def save_orders_to_file(orders: Dict[str, Dict[str, int]]):
    with open(ORDER_FILE, "w") as file:
        json.dump(orders, file)



def check_token(token: str):
    response = requests.get(f"{ACCOUNT_MICROSERVICE_URL}/check_token", json={"token": token})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Invalid token")
    return response.json()


def get_user_cart(token: str, carts: Dict[str, Dict[str, int]] = Depends(load_carts_from_file)) -> Dict[str, int]:
    if token not in carts:
        carts[token] = {}
    return carts[token]


def is_valid_item(product_id: str) -> bool:
    products = load_products_from_file()

    for product in products:
        if product.get("id") == product_id:
            return True

    return False


@app.post("/cart")
def add_to_cart(cart_item: CartItem, token: str, carts: Dict[str, Dict[str, int]] = Depends(load_carts_from_file)):
    # Check if the token is valid
    response = requests.get(f"{ACCOUNT_MICROSERVICE_URL}/check_token", json={"token": token})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Invalid token")

    # Token is valid, proceed with adding item to cart
    item_id = cart_item.item_id
    quantity = cart_item.quantity

    if token not in carts:
        carts[token] = {}

    user_cart = carts[token]

    if not is_valid_item(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    # Add logic to check other validation rules if needed

    if item_id in user_cart:
        user_cart[item_id] += quantity
    else:
        user_cart[item_id] = quantity

    save_carts_to_file(carts)  # Save the carts to file

    return {"message": "Item added to cart"}

@app.get("/items")
def items():
    return load_products_from_file()


@app.get("/item/{item_ID}")
def details(item_ID: str):
    item = next((item for item in load_products_from_file() if item["id"] == item_ID), None)
    if item:
        return item
    else:
        return {"Item Not Found"}


@app.delete("/cart")
def remove_from_cart(product_id: str, token: str):
    carts = load_carts_from_file()

    if token not in carts:
        raise HTTPException(status_code=404, detail="Invalid token")

    user_cart = carts[token]

    if product_id not in user_cart:
        raise HTTPException(status_code=404, detail="Product not found in cart")

    del user_cart[product_id]

    save_carts_to_file(carts)

    return {"message": "Product removed from cart"}




