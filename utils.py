import json

def load_discount_codes(filename):
    with open(filename, 'r') as file:
        discount_codes = json.load(file)
    return discount_codes