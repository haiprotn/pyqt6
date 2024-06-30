
import sqlite3
from database import create_connection, close_connection
class CustomerModel:
    def __init__(self, db_path):
        self.db_path = db_path

    def add_customer(self, customer):
        """Thêm khách hàng mới vào cơ sở dữ liệu."""
        conn = create_connection(self.db_path)
        sql = ''' INSERT INTO customers(name, address, phone, note,email)
                  VALUES(?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, customer)
        conn.commit()
        close_connection(conn)

    def get_all_customers(self):
        """Lấy tất cả khách hàng từ cơ sở dữ liệu."""
        conn = create_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM customers")
        customers = cur.fetchall()
        close_connection(conn)
        return customers

    def update_customer(self, customer_id, customer):
        """Cập nhật thông tin khách hàng."""
        conn = create_connection(self.db_path)
        sql = ''' UPDATE customers
                  SET name = ?, address = ?, phone = ?, note = ?,email=?
                  WHERE id = ? '''
        cur = conn.cursor()
        # Đảm bảo product_id được thêm vào cuối tuple trước khi truyền vào execute
        cur.execute(sql, customer + (customer_id,))
        conn.commit()
        close_connection(conn)

    def delete_customer(self, customer_id):
        """Xoá khách hàng từ cơ sở dữ liệu."""
        conn = create_connection(self.db_path)
        sql = 'DELETE FROM customers WHERE id = ?'
        cur = conn.cursor()
        cur.execute(sql, (customer_id,))
        conn.commit()
        close_connection(conn)

    def search_customers(self, search_query):
        """Tìm kiếm khách hàng dựa trên tên hoặc ghi chú."""
        conn = create_connection(self.db_path)
        sql = ''' SELECT * FROM customers WHERE name LIKE ? OR note LIKE ? '''
        cur = conn.cursor()
        cur.execute(sql, ('%' + search_query + '%', '%' + search_query + '%'))
        customers = cur.fetchall()
        close_connection(conn)
        return customers
    def get_customer_address_by_id(self, customer_id):
        """Lấy địa chỉ của khách hàng dựa trên ID."""
        conn = create_connection(self.db_path)
        sql = ''' SELECT address FROM customers WHERE id = ? '''
        cur = conn.cursor()
        cur.execute(sql, (customer_id,))
        result = cur.fetchone()
        close_connection(conn)
        if result:
            return result[0]  # Trả về địa chỉ của khách hàng
        else:
            return None  # Trả về None nếu không tìm thấy khách hàng
