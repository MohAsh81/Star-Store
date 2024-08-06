import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="------",
    database="shop"
)

cursor = mydb.cursor()