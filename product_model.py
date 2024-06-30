# product_model.py
import sqlite3
from database import create_connection, close_connection

class ProductModel:
    def __init__(self, db_path):
        self.db_path = db_path

    def add_product(self, product):
        """Thêm sản phẩm mới vào cơ sở dữ liệu."""
        conn = create_connection(self.db_path)
        sql = ''' INSERT INTO products(name, unit, price, quantity, note)
                  VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, product)
        conn.commit()
        close_connection(conn)

    def get_all_products(self):
        """Lấy tất cả sản phẩm từ cơ sở dữ liệu."""
        conn = create_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        close_connection(conn)
        return products

    def update_product(self, product_id, product):
        """Cập nhật thông tin sản phẩm."""
        conn = create_connection(self.db_path)
        sql = ''' UPDATE products
                  SET name = ?, unit = ?, price = ?, quantity = ?, note = ?
                  WHERE id = ? '''
        cur = conn.cursor()
        cur.execute(sql, product + (product_id,))
        conn.commit()
        close_connection(conn)

    def delete_product(self, product_id):
        """Xoá sản phẩm từ cơ sở dữ liệu."""
        conn = create_connection(self.db_path)
        sql = 'DELETE FROM products WHERE id = ?'
        cur = conn.cursor()
        cur.execute(sql, (product_id,))
        conn.commit()
        close_connection(conn)

    def search_products(self, search_query):
        """Tìm kiếm sản phẩm dựa trên tên hoặc ghi chú."""
        conn = create_connection(self.db_path)
        sql = ''' SELECT * FROM products WHERE name LIKE ? OR note LIKE ? '''
        cur = conn.cursor()
        cur.execute(sql, ('%' + search_query + '%', '%' + search_query + '%'))
        products = cur.fetchall()
        close_connection(conn)
        return products
