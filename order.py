import json
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict
import requests

load_dotenv()

app = FastAPI()
CARTS_FILE = "carts.json"
ORDER_FILE = "order.json"
SHOP_MICROSERVICE_URL = os.getenv("SHOP_MICROSERVICE_URL") # URL of the Shop microservice
ACCOUNT_MICROSERVICE_URL = os.getenv("ACCOUNT_MICROSERVICE_URL")
ORDER_MICROSERVICE_URL = os.getenv("ORDER_MICROSERVICE_URL")


class Payment(BaseModel):
    amount: int
    token:str
     

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




def get_cart(token: str):
    response = requests.post(f"{SHOP_MICROSERVICE_URL}/cart", params={"token": token})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error retrieving cart from Shop microservice")
    return response.json()


@app.post("/order")
def move_cart_to_order(token:str):
    carts = load_carts_from_file()
    orders = load_orders_from_file()

    if token not in carts:
        raise HTTPException(status_code=403, detail="Invalid token")
        
    user_cart = carts[token]
    carts_to_order = user_cart
    carts_to_order["isPay"] = False
    if token not in orders:
        orders[token] = [carts_to_order]
    else:
        orders[token].append(carts_to_order)

    del carts[token]
    
    save_carts_to_file(carts)
    save_orders_to_file(orders)


    return{"message": "move cart to order"}
    

@app.post("/pay")
def pay_order(payment:Payment):
    return{"message" :str(payment.amount)+payment.token+"successfully order paid"}




@app.post("/add_order")
def add_order(token: str):
    cart = get_cart(token)
    return {"cart": cart}

@app.post("/pay_order")
def pay_order(token: str):
    cart = get_cart(token)
    # Simulate payment process and mark the order as paid

    # Save the order to the order.json file
    with open(ORDER_FILE, "a") as file:
        order = {"token": token, "cart": cart}
        json.dump(order, file)
        file.write("\n")

    return {"message": "Order has been paid successfully"}

@app.get("/get_orders")
def get_orders():
    orders = []
    with open(ORDER_FILE, "r") as file:
        for line in file:
            order = json.loads(line)
            orders.append(order)
    return {"orders": orders}

