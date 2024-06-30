from database import create_connection, close_connection

class OrderManagementModel:
    def __init__(self, db_path):
        self.db_path = db_path

    def add_order(self, order_date, id_customer, payment_method,subtotal, tax, discount,total_payment):
        conn = create_connection(self.db_path)
        sql = ''' INSERT INTO orders(order_date, id_customer, payment_method, subtotal, tax, discount,total_payment)
                VALUES(?,?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (order_date, id_customer, payment_method, subtotal, tax, discount,total_payment))
        order_id = cur.lastrowid
        conn.commit()
        close_connection(conn)
        return order_id

    def add_order_detail(self, order_id, product_id, quantity, price, amount, note=""):
        conn = create_connection(self.db_path)
        sql = ''' INSERT INTO order_details(order_id, product_id, quantity, price, amount, note)
                  VALUES(?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (order_id, product_id, quantity, price,amount, note))
        conn.commit()
        close_connection(conn)

    def get_orders(self):
        conn = create_connection(self.db_path)
        sql = ''' SELECT * FROM orders '''
        cur = conn.cursor()
        cur.execute(sql)
        orders = cur.fetchall()
        close_connection(conn)
        return orders

    def get_order_details(self, order_id):
        conn = create_connection(self.db_path)
        sql = ''' SELECT * FROM order_details WHERE order_id=? '''
        cur = conn.cursor()
        cur.execute(sql, (order_id,))
        details = cur.fetchall()
        close_connection(conn)
        return details
    
    #hiển thi danh sách chi tiết  hoá đơn
    def get_order_list_details(self, order_id):
        conn = create_connection(self.db_path)
        try:
            # Truy vấn sửa đổi với JOIN chính xác
            sql = ''' 
            SELECT d.product_id, p.name, d.quantity, d.price, d.amount, d.note
            FROM order_details d
            JOIN products p ON d.product_id = p.id
            WHERE d.order_id=?
            '''
            cur = conn.cursor()
            cur.execute(sql, (order_id,))
            details = cur.fetchall()
            return details
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            close_connection(conn)

    # Phương thức để cập nhật thông tin hoá đơn nếu cần
    def update_order(self, order_id, order_date, customer_name):
        conn = create_connection(self.db_path)
        sql = ''' UPDATE orders SET order_date=?, customer_name=? WHERE id=? '''
        cur = conn.cursor()
        cur.execute(sql, (order_date, customer_name, order_id))
        conn.commit()
        close_connection(conn)

    # Phương thức để cập nhật chi tiết hoá đơn
    def update_order_detail(self, detail_id, order_id, product_id, quantity, price, note=""):
        conn = create_connection(self.db_path)
        sql = ''' UPDATE order_details SET order_id=?, product_id=?, quantity=?, price=?, note=? WHERE id=? '''
        cur = conn.cursor()
        cur.execute(sql, (order_id, product_id, quantity, price, note, detail_id))
        conn.commit()
        close_connection(conn)

    # Thêm các phương thức xóa hoá đơn và chi tiết hoá đơn nếu cần
    def get_all_orders(self):
        """Lấy danh sách tất cả hóa đơn từ cơ sở dữ liệu."""
        conn = create_connection(self.db_path)
        try:
            sql = ''' SELECT id, order_date, customer_name, payment_method, subtotal, tax, discount, total_payment FROM orders '''
            cur = conn.cursor()
            cur.execute(sql)
            orders = cur.fetchall()
            return orders
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
        finally:
            close_connection(conn)
