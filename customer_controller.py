from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem,QStyledItemDelegate
from PyQt6.QtCore import Qt
from customer_model import CustomerModel
from main_view import Ui_MainWindow


class CenterDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter
        super().paint(painter, option, index)

class CustomerController:
    def __init__(self, ui:Ui_MainWindow,parent = None):
        self.ui = ui
        self.modelCusomer = CustomerModel("sales_management.db")
        self.parent = parent  # Thêm dòng này

#load khách Hàng
    def load_customers(self):
        customers = self.modelCusomer.get_all_customers()
        self.ui.table_customers.clear()
        self.ui.table_customers.setRowCount(len(customers))  # Thiết lập số hàng
        
        # Đặt đúng số cột và sử dụng đúng table widget
        self.ui.table_customers.setColumnCount(6)  # Đặt số cột phù hợp với số tiêu đề cột
        self.ui.table_customers.setHorizontalHeaderLabels(["Mã KH", "Tên Khách Hàng", "Địa Chỉ", "Điện Thoại", "Ghi chú", "Email"])
        
        for row, customer in enumerate(customers):
            for column, item in enumerate(customer):
                # Đảm bảo rằng item không phải là None trước khi chuyển đổi thành chuỗi
                if item is None:
                    item = ''
                self.ui.table_customers.setItem(row, column, QTableWidgetItem(str(item)))

        self.ui.label__idCustomer.setVisible(False)
        self.ui.id_customers.setVisible(False)
        self.configure_table()
        self.ui.saveCustomers.setEnabled(False)
        self.hide_iput()
# Search 
    def search_customers(self):
        # Lấy từ khóa tìm kiếm từ UI
        search_query = self.ui.lineEdit_searchCustomers.text()  # Giả sử bạn có QLineEdit tên là searchLineEdit

        # Thực hiện tìm kiếm
        customers = self.modelCusomer.search_customers(search_query)
        
        # Cập nhật QTableWidget với kết quả tìm kiếm
        self.ui.table_customers.clearContents()  # Xóa nội dung hiện có
        self.ui.table_customers.setRowCount(len(customers))  # Thiết lập số hàng mới dựa trên kết quả

        for row, customer in enumerate(customers):
            for column, item in enumerate(customer):
                self.ui.table_customers.setItem(row, column, QTableWidgetItem(str(item)))

        # Điều chỉnh lại độ rộng cột và hàng dựa vào nội dung mới
        self.ui.table_customers.resizeColumnsToContents()
        self.ui.table_customers.resizeRowsToContents()
    #Hiện thi số dạng tiền
#config table 
    def configure_table(self):
        self.ui.table_customers.verticalHeader().setVisible(False)
        self.ui.table_customers.resizeColumnsToContents()
        
        # Đặt độ rộng tối thiểu cho các cột sau khi đã điều chỉnh kích thước tự động
        min_column_width = 100  # Đặt độ rộng tối thiểu mà bạn muốn
        for i in range(self.ui.table_customers.columnCount()):
            current_width = self.ui.table_customers.columnWidth(i)
            if current_width < min_column_width:
                self.ui.table_Product.setColumnWidth(i, min_column_width)
            # Hoặc đảm bảo độ rộng tối thiểu không dưới một giá trị nhất định
            self.ui.table_Product.horizontalHeader().setMinimumSectionSize(min_column_width) 

        ##canh lê giữa cho cột  
        centerDelegate = CenterDelegate(self.ui.table_customers)
        for i in range(self.ui.table_customers.columnCount()):
            self.ui.table_customers.setItemDelegateForColumn(i, centerDelegate)
# thêm khách hàng
    def add_customer(self):
        # Lấy thông tin từ UI
        name = self.ui.name_customers.text()
        address = self.ui.address_customers.text()
        phone = self.ui.phone_customers.text()
        note = self.ui.note_customers.text()
        email = self.ui.Email_customers.text()
        self.ui.deleteCustomers.setEnabled(True)
        # Kiểm tra dữ liệu nhập
        if not name or not address or not phone:
            QMessageBox.warning(self.parent, "Thông báo", "Vui lòng nhập đủ thông tin khách hàng!")
            return

        # Thêm khách hàng vào database
        try:
            self.modelCusomer.add_customer((name, address, phone, note,email))
            QMessageBox.information(self.parent, "Thành công", "Khách hàng đã được thêm thành công.")
            self.clear_input_fields()
            self.load_customers()
        except Exception as e:
            QMessageBox.warning(self.ui, "Lỗi", str(e))
#delete customers 
    def delete_customer(self):
        # Lấy hàng hiện tại đang được chọn
        current_row = self.ui.table_customers.currentRow()
        
        if current_row != -1:  # Kiểm tra xem có hàng nào được chọn không
            # Lấy giá trị ID sản phẩm từ cột đầu tiên của hàng được chọn
            id_customer = self.ui.table_customers.item(current_row, 0).text()  # Giả sử ID sản phẩm nằm ở cột đầu tiên
            
            # Hỏi người dùng có chắc chắn muốn xóa không
            reply = QMessageBox.question(self.parent, 'Xác nhận', 'Bạn có chắc chắn muốn xóa sản phẩm này không?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Gọi phương thức xóa sản phẩm từ product_model
                self.modelCusomer.delete_customer(id_customer)
                
                # Hiển thị thông báo thành công
                QMessageBox.information(self.parent, "Thành công", "Khách Hàng đã được xóa.")
                
                # Làm mới danh sách sản phẩm
                self.load_customers()
        else:
            # Nếu không có hàng nào được chọn, hiển thị thông báo
            QMessageBox.warning(self.parent, "Thông báo", "Vui lòng chọn sản phẩm cần xóa.")
    def clear_input_fields(self):
        # Xoá trắng các trường nhập liệu sau khi thêm hoặc cập nhật thành công
        self.ui.name_customers.clear()
        self.ui.address_customers.clear()
        self.ui.phone_customers.clear()
        self.ui.note_customers.clear()
        self.ui.Email_customers.clear()
        self.ui.saveCustomers.setEnabled(True)
        self.show_iput()
    def update_customers(self):
        # Lấy thông tin từ giao diện
        id_customer = self.ui.id_customers.text()
        nameCustomer=self.ui.name_customers.text()
        addressCustomer = self.ui.address_customers.text()
        phoneCustomer=self.ui.phone_customers.text()
        noteCustomer=self.ui.note_customers.text()
        emailCustomer=self.ui.Email_customers.text()

        if not id_customer:
            QMessageBox.warning(self.parent, "Lỗi", "Vui lòng nhập ID Khách Hàng.")
            return
        
        try:
             # Tạo tuple sản phẩm từ thông tin nhập
            customer = (nameCustomer, addressCustomer, phoneCustomer, noteCustomer, emailCustomer)
            reply = QMessageBox.question(self.parent, 'Xác nhận', f"Bạn có chắc chắn muốn sữa Khách Hàng {nameCustomer} này không?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply==QMessageBox.StandardButton.Yes:
                self.modelCusomer.update_customer(id_customer, customer)
                self.load_customers()
                QMessageBox.information(self.parent, "Thành công", f"Khách hàng {nameCustomer} đã được cập nhật thành công.")

        except ValueError:
            QMessageBox.warning(self.parent, "Lỗi", "Giá hoặc số lượng không hợp lệ.")
            return

    def handleCellClicked(self, row, column):
        id_customer = self.ui.table_customers.item(row, 0).text()  # Giả sử cột 0 là ID sản phẩm
        name_customer = self.ui.table_customers.item(row, 1).text()  # Giả sử cột 1 là tên sản phẩm
        address_customer = self.ui.table_customers.item(row, 2).text()  # Giả sử cột 2 là đơn vị
        phone_customer = self.ui.table_customers.item(row, 3).text()  # Giả sử cột 3 là giá
        note_customer = self.ui.table_customers.item(row, 4).text() # Giả sử cột 4 là số lượng
        email_customer = self.ui.table_customers.item(row, 5).text()  # Giả sử cột 5 là ghi chú

        # Gán dữ liệu vào các QLineEdit tương ứng
        self.ui.id_customers.setText(id_customer)
        self.ui.name_customers.setText(name_customer)
        self.ui.address_customers.setText(address_customer)
        self.ui.phone_customers.setText(phone_customer)
        self.ui.note_customers.setText(note_customer)
        self.ui.Email_customers.setText(email_customer)
        self.ui.saveCustomers.setEnabled(False)
        self.show_iput()
    def show_iput(self):
        self.ui.name_customers.setEnabled(True)
        self.ui.name_customers.setStyleSheet("background-color:rgb(255, 255, 255);")
        self.ui.address_customers.setEnabled(True)
        self.ui.address_customers.setStyleSheet("background-color:rgb(255, 255, 255);")

        self.ui.phone_customers.setEnabled(True)
        self.ui.phone_customers.setStyleSheet("background-color:rgb(255, 255, 255);")

        self.ui.note_customers.setEnabled(True)
        self.ui.note_customers.setStyleSheet("background-color:rgb(255, 255, 255);")

        self.ui.Email_customers.setEnabled(True)
        self.ui.Email_customers.setStyleSheet("background-color:rgb(255, 255, 255);")
##hide Inpur 
    def hide_iput(self):
        self.ui.name_customers.setStyleSheet("background-color:rgb(238, 249, 250);")
        self.ui.address_customers.setEnabled(False)
        self.ui.address_customers.setStyleSheet("background-color:rgb(238, 249, 250);")

        self.ui.phone_customers.setEnabled(False)
        self.ui.phone_customers.setStyleSheet("background-color:rgb(238, 249, 250);")

        self.ui.note_customers.setEnabled(False)
        self.ui.note_customers.setStyleSheet("background-color:rgb(238, 249, 250);")

        self.ui.Email_customers.setEnabled(False)
        self.ui.Email_customers.setStyleSheet("background-color:rgb(238, 249, 250);")