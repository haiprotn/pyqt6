import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """Tạo kết nối đến cơ sở dữ liệu SQLite đã chỉ định."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """Tạo một bảng từ câu lệnh create_table_sql đã cung cấp."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
def close_connection(conn):
    """Đóng kết nối với cơ sở dữ liệu."""
    try:
        if conn:
            conn.close()
            print("Kết nối đã được đóng.")
    except Error as e:
        print(e)

def main():
    database = "sales_management.db"

    sql_create_customers_table = """CREATE TABLE IF NOT EXISTS customers (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    address text,
                                    phone text,
                                    note text
                                );"""

    sql_create_debts_table = """CREATE TABLE IF NOT EXISTS debts (
                                id INTEGER PRIMARY KEY,
                                order_id INTEGER NOT NULL,
                                customer_id INTEGER NOT NULL,
                                total_debt REAL NOT NULL,
                                debt_date,
                                due_date DATE,   -- Ngày đáo hạn công nợ
                                is_paid INTEGER DEFAULT 0, -- Trạng thái thanh toán, 0 = chưa thanh toán, 1 = đã thanh toán
                                note TEXT,
                                FOREIGN KEY (order_id) REFERENCES orders (id),
                                FOREIGN KEY (customer_id) REFERENCES customers (id)
                            );"""

    sql_create_products_table = """CREATE TABLE IF NOT EXISTS products (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    unit text NOT NULL,
                                    price real NOT NULL,
                                    quantity integer NOT NULL,
                                    note text
                                );"""

    sql_create_inventory_table = """CREATE TABLE IF NOT EXISTS inventory (
                                    id integer PRIMARY KEY,
                                    product_id integer NOT NULL,
                                    quantity integer NOT NULL,
                                    FOREIGN KEY (product_id) REFERENCES products (id)
                                );"""

    sql_create_orders_table = """CREATE TABLE IF NOT EXISTS orders (
                                    id integer PRIMARY KEY,
                                    order_date text NOT NULL,
                                    id_customer interger NOT NULL
                                );"""

    sql_create_order_details_table = """CREATE TABLE IF NOT EXISTS order_details (
                                        order_id integer NOT NULL,
                                        product_id integer NOT NULL,
                                        quantity integer NOT NULL,
                                        price real NOT NULL,
                                        note text,
                                        FOREIGN KEY (order_id) REFERENCES orders (id),
                                        FOREIGN KEY (product_id) REFERENCES products (id)
                                    );"""

    sql_create_suppliers_table = """CREATE TABLE IF NOT EXISTS suppliers (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    address text,
                                    phone text
                                );"""

    sql_create_export_invoices_table = """CREATE TABLE IF NOT EXISTS export_invoices (
                                            id integer PRIMARY KEY,
                                            date text NOT NULL,
                                            supplier_id integer NOT NULL,
                                            note text,
                                            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                                        );"""

    sql_create_import_invoices_table = """CREATE TABLE IF NOT EXISTS import_invoices (
                                            id integer PRIMARY KEY,
                                            date text NOT NULL,
                                            supplier_id integer NOT NULL,
                                            note text,
                                            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                                        );"""

    
    # Tạo kết nối đến cơ sở dữ liệu
    conn = create_connection(database)

    # Tạo các bảng
    if conn is not None:
        create_table(conn, sql_create_products_table)
        create_table(conn, sql_create_inventory_table)
        create_table(conn, sql_create_orders_table)
        create_table(conn, sql_create_order_details_table)
        # Tạo bảng customers và debts
        create_table(conn, sql_create_customers_table)
        create_table(conn, sql_create_debts_table)
        # Tạo bảng mới
        create_table(conn, sql_create_suppliers_table)
        create_table(conn, sql_create_export_invoices_table)
        create_table(conn, sql_create_import_invoices_table)
        add_email_column_to_customers(conn)  # Thêm cột mới
        add_payment_column_to_oder(conn)
        add_amount_column_to_oder(conn)
        add_column_order(conn)
        close_connection(conn)
    else:
        print("Lỗi! không thể tạo kết nối đến cơ sở dữ liệu.")
def add_email_column_to_customers(conn):
    sql = '''ALTER TABLE customers ADD COLUMN email TEXT;'''
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
def add_payment_column_to_oder(conn):
    sql = '''ALTER TABLE orders ADD COLUMN payment_method TEXT;'''
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
def add_amount_column_to_oder(conn):
    sql = '''ALTER TABLE order_details ADD COLUMN amount real;'''
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)

def add_column_order(conn):
    columns = [
        "ALTER TABLE orders ADD COLUMN subtotal REAL",
        "ALTER TABLE orders ADD COLUMN tax REAL",
        "ALTER TABLE orders ADD COLUMN discount REAL",
        "ALTER TABLE orders  ADD COLUMN total_payment REAL"
    ]
    
    c = conn.cursor()
    for sql in columns:
        try:
            c.execute(sql)
        except Error as e:
            print(e)
    conn.commit() 
if __name__ == '__main__':
    main()
