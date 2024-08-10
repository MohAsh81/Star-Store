from database import cursor

class Product:
    @staticmethod
    def get_all_products():
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        return products
