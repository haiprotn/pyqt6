import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('invoice_management.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(create_table_sql):
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error! cannot create the database connection.")

def init_app():
    create_table_products()
    create_table_invoices()
    create_table_suppliers()

def create_table_products():
    sql_create_products_table = """ CREATE TABLE IF NOT EXISTS products (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL,
                                        unit TEXT NOT NULL,
                                        price REAL NOT NULL,
                                        quantity INTEGER NOT NULL,
                                        note TEXT
                                    ); """
    create_table(sql_create_products_table)

def create_table_invoices():
    sql_create_invoices_table = """ CREATE TABLE IF NOT EXISTS invoices (
                                        id INTEGER PRIMARY KEY,
                                        date TEXT NOT NULL,
                                        supplier_id INTEGER NOT NULL,
                                        note TEXT,
                                        FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                                    ); """
    create_table(sql_create_invoices_table)

def create_table_suppliers():
    sql_create_suppliers_table = """ CREATE TABLE IF NOT EXISTS suppliers (
                                        id INTEGER PRIMARY KEY,
                                        name TEXT NOT NULL,
                                        address TEXT,
                                        phone TEXT
                                    ); """
    create_table(sql_create_suppliers_table)
