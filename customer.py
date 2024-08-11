from datetime import datetime
import re
from user import User
from product import Product
from database import cursor, mydb
from utils import load_discount_codes

discount_codes = load_discount_codes('discount_codes.json')

class Customer(User):
    def __init__(self, user_id, username, password, wallet):
        super().__init__(user_id, username, password)
        self.wallet = wallet

    @staticmethod
    def register(username, password):
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$', password):
            return "Password must be at least 8 characters long, contain a number, a lowercase and an uppercase letter."

        cursor.execute(
            f"""SELECT * FROM users WHERE username = '{username}'""")
        if cursor.fetchone():
            return "Username already exists."

        cursor.execute(
            f"""INSERT INTO users (username, password) VALUES ('{username}', '{password}')""")
        user_id = cursor.lastrowid
        cursor.execute(
            f"""INSERT INTO customers (user_id, wallet) VALUES ({int(user_id)}, {0})""")
        mydb.commit()
        return None

    @staticmethod
    def get_customer_by_user_id(user_id):
        cursor.execute(f"""SELECT * FROM users WHERE user_id = {user_id}""")
        user = cursor.fetchone()
        cursor.execute(
            f"""select wallet from customers where user_id = {user_id}""")
        customer = cursor.fetchone()
        if user:
            return Customer(user[0], user[1], user[2], customer[0])
        return None

    def place_order(self, product_id, quantity, discount_code=None):
        cursor.execute(
            f"""SELECT price, stock FROM products WHERE product_id = {product_id}""")
        product = cursor.fetchone()

        if not product or product[1] < quantity:
            return "Not enough stock or invalid product ID"

        total_price = product[0] * quantity
        if discount_code:
            discount = discount_codes.get(discount_code, None)
            if discount and datetime.strptime(discount['expiry_date'], '%Y-%m-%d') > datetime.now():
                total_price *= (1 - discount['discount_percentage'] / 100)
                cursor.execute(f"""insert into discounts value('{discount_code}',{1})""")
            else:
                return "Invalid or expired discount code"

        print(f"Total price after discount (if applied): {total_price}")
        use_wallet = input(
            "Do you want to use your wallet balance? (y/n): ").lower()

        if use_wallet == 'y' and self.wallet >= total_price:
            self.wallet -= total_price
            total_price = 0
        elif use_wallet == 'y':
            total_price -= self.wallet
            self.wallet = 0
        elif use_wallet == 'n':
            pass

        cursor.execute(
            f"""UPDATE products SET stock = stock - {quantity} WHERE product_id = {product_id}""")
        cursor.execute(
            f"""INSERT INTO orders (user_id, product_id, quantity, total_price, date) VALUES ({self.user_id}, {product_id}, {quantity}, {total_price}, '{datetime.now()}')""")
        cursor.execute(
            f"""UPDATE customers SET wallet = {self.wallet + total_price * 0.05} WHERE user_id = {self.user_id}""")

        mydb.commit()
        return "Order placed successfully"

    def view_order_history(self):
        cursor.execute(
            f"""SELECT * FROM orders WHERE user_id = {self.user_id}""")
        orders = cursor.fetchall()
        return orders

def customer_menu():
    while True:
        print(" ** Enter <1> to log in **")
        print(" ** Enter <2> to register **")
        print(" ** Enter <0> to return to main menu **")
        choice = input()

        if choice == '0':
            break
        elif choice == '1':
            customer_login()
        elif choice == '2':
            customer_register()
        else:
            print("Invalid input")

def customer_login():
    print("Customer Login")
    username = input("Username: ")
    password = input("Password: ")
    user = User.authenticate(username, password)
    if user:
        customer = Customer.get_customer_by_user_id(user.user_id)
        customer_dashboard(customer)
    else:
        print("Invalid username or password")

def customer_register():
    print("Customer Registration")
    username = input("Choose a username: ")
    password = input("Choose a password: ")
    error = Customer.register(username, password)
    if error:
        print(error)
    else:
        print("Registration successful")

def customer_dashboard(customer):
    while True:
        print(f"Welcome, your wallet balance is {customer.wallet}")
        print(" ** Enter <1> to place a new order **")
        print(" ** Enter <2> to view order history **")
        print(" ** Enter <3> to change password **")
        print(" ** Enter <0> to logout **")
        choice = input()

        if choice == '0':
            break
        elif choice == '1':
            place_order(customer)
        elif choice == '2':
            view_order_history(customer)
        elif choice == '3':
            change_password(customer)
        else:
            print("Invalid input")

def place_order(customer):
    products = Product.get_all_products()
    print("Product List:")
    for product in products:
        print(
            f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Stock: {product[3]}")

    try:
        product_id = int(input("Enter product ID to buy: "))
        quantity = int(input("Enter quantity: "))
    except ValueError:
        print("Invalid input. Please enter numerical values for product ID and quantity.")
        return

    discount_code = input("Enter discount code (if any): ").strip()
    if discount_code == '':
        discount_code = None
    else:
        used_codes = []
        cursor.execute("""Select discount_code from discounts""")
        used = cursor.fetchall()
        for row in used:
            used_codes.append(row[0])
        if discount_code in used_codes:
            print("Code was used")
            discount_code = ''
        else:
            pass

    message = customer.place_order(product_id, quantity, discount_code)
    print(message)

def view_order_history(customer):
    orders = customer.view_order_history()
    print("Order History:")
    for order in orders:
        print(
            f"Order ID: {order[0]}, Product ID: {order[2]}, Quantity: {order[3]}, Total Price: {order[4]}, Date: {order[5]}")

def change_password(user):
    new_password = input("Enter new password: ")
    message = user.change_password(new_password)
    print(message)
