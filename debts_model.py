import sqlite3
from database import create_connection, close_connection

class DebtsModel:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_debts_total(self):
        """Lấy thông tin công nợ của tất cả khách hàng."""
        conn = create_connection(self.db_path)
        try:
            sql = '''SELECT customer_id, sum(total_debt) as total_debt
                     FROM debts
                     GROUP BY customer_id;'''
            cur = conn.cursor()
            cur.execute(sql)
            debts = cur.fetchall()
            return debts
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            close_connection(conn)

    def get_debt_details(self, customer_id):
        """Lấy chi tiết công nợ của một khách hàng cụ thể."""
        conn = create_connection(self.db_path)
        try:
            sql = '''SELECT order_id, due_date, total_debt, is_paid
                     FROM debts
                     WHERE customer_id = ?;'''
            cur = conn.cursor()
            cur.execute(sql, (customer_id,))
            details = cur.fetchall()
            return details
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            close_connection(conn)

    def get_orders_by_payment_method(self, payment_method):
        conn = create_connection(self.db_path)
        try:
            sql = ''' SELECT id, order_date, customer_name, subtotal, tax, discount, total_payment FROM orders WHERE payment_method=? '''
            cur = conn.cursor()
            cur.execute(sql, (payment_method,))
            orders = cur.fetchall()
            return orders
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            close_connection(conn)

    #thêm công nợ nếu khách hàng chọn hình thức thanh toán công nợ
    def add_debt_for_order(self, order_id, customer_id, total_debt,debt_date ,due_date):
        conn = create_connection(self.db_path)
        try:
            sql = '''INSERT INTO debts (order_id, customer_id, total_debt,debt_date, due_date, is_paid)
                    VALUES (?, ?, ?, ?, ?, 0);'''
            cur = conn.cursor()
            cur.execute(sql, (order_id, customer_id, total_debt, debt_date, due_date))
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            close_connection(conn)

    #lấy dữ liệu bảng debts
    def get_debt_all(self):
        """Lấy chi tiết công nợ của một khách hàng cụ thể."""
        conn = create_connection(self.db_path)
        try:
            sql = '''SELECT *FROM debts;'''
            cur = conn.cursor()
            cur.execute(sql)
            details = cur.fetchall()
            return details
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            close_connection(conn)