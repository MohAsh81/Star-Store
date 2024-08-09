from user import User
from database import cursor, mydb


class Admin(User):
    @staticmethod
    def add_product(name, price, stock):
        cursor.execute(
            f"""INSERT INTO products (name, price, stock) VALUES ('{name}', {price}, {stock})""")
        mydb.commit()
        return "Product added successfully"

    @staticmethod
    def change_stock(product_id, stock):
        cursor.execute(
            f"""update products set stock = {stock} WHERE product_id = {int(product_id)}""")
        mydb.commit()
        return "Product removed successfully"

    @staticmethod
    def view_all_products():
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        return products


def admin_menu(admin):
    while True:
        print(" ** Enter <1> to add a new product **")
        print(" ** Enter <2> to change a stock of a product **")
        print(" ** Enter <3> to view all products **")
        print(" ** Enter <4> to change password **")
        print(" ** Enter <0> to logout **")
        choice = input()

        if choice == '0':
            break
        elif choice == '1':
            add_product()
        elif choice == '2':
            change_stock()
        elif choice == '3':
            view_all_products()
        elif choice == '4':
            User.change_password(admin)
        else:
            print("Invalid input")


def add_product():
    name = input("Enter product name: ")
    price = float(input("Enter product price: "))
    stock = int(input("Enter product stock: "))
    message = Admin.add_product(name, price, stock)
    print(message)


def change_stock():
    product_id = (input("Enter product ID to change: "))
    stock = int(input("Enter new stock of product: "))
    message = Admin.change_stock(product_id, stock)
    print(message)


def view_all_products():
    products = Admin.view_all_products()
    print("Product List:")
    for product in products:
        print(
            f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}, Stock: {product[3]}")


def admin_login():
    print("Admin Login")
    username = input("Username: ")
    password = input("Password: ")
    user = User.authenticate(username, password)
    if user:
        admin = Admin(user.user_id, user.username, user.password)
        admin_menu(admin)
    else:
        print("Invalid username or password")
