from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem,QAbstractButton,QTableWidget,QStyledItemDelegate,QMessageBox
from PyQt6.QtCore import Qt,QLocale,QRegularExpression,QDate
from main_view import Ui_MainWindow  # Đảm bảo tên file này khớp với file UI của bạn
from product_model import ProductModel
import sys
from customer_controller import CustomerController
from oderManage_controller import OrderManagementController
from debts_controller import DebtsController
from PyQt6.QtGui import QRegularExpressionValidator

class CenterDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter
        super().paint(painter, option, index)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Khởi tạo CustomerController với truy cập đến UI
        self.customer_controller = CustomerController(self.ui)
        # Lưu trữ product_model như một thuộc tính để có thể truy cập từ các phương thức khác
        self.product_model = ProductModel("sales_management.db")

        # Khởi tạo và hiển thị sản phẩm
        self.load_product()

        # Thiết lập các kết nối sự kiện mỏ các trang
        self.ui.home.clicked.connect(self.show_home_page)
        self.ui.product.clicked.connect(self.show_product_page)
        self.ui.other.clicked.connect(self.show_oder_page)
        self.ui.customers.clicked.connect(self.show_customers_page)
        self.ui.listoder.clicked.connect(self.show_list_oder_page)
        self.ui.debts.clicked.connect(self.show_debts_oder_page)
        

        # Thiết lập thêm các kết nối sự kiện cho việc thêm, xóa, và cập nhật sản phẩm
        self.ui.price_Product.textEdited.connect(self.format_price)
        #____Show input ____________________________
        self.ui.btn_add_Produuct.clicked.connect(self.clear_content)
        #____Save___________________________
        self.ui.btn_save_Produuct.clicked.connect(self.add_product_slot)
        #____Delete___________________________________
        self.ui.btn_del_Produuct.clicked.connect(self.delete_product_slot)
        #_____Update___________________________________
        self.ui.btn_edit_Produuct.clicked.connect(self.update_product_slot)
        #____Cell click ____________________________________
        self.ui.table_Product.cellClicked.connect(self.handleCellClicked)

        self.ui.line_find_Produuct.textChanged.connect(self.search_product_slot)

#___________________________________________________START CUSTOMERS______________________________________________________________
        
        self.customer_controller = CustomerController(self.ui)
        self.ui.addCustomers.clicked.connect(self.customer_controller.clear_input_fields)
        self.ui.saveCustomers.clicked.connect(self.customer_controller.add_customer)
        self.ui.deleteCustomers.clicked.connect(self.customer_controller.delete_customer)
        self.ui.editCustomers.clicked.connect(self.customer_controller.update_customers)
        


        self.customer_controller.load_customers()
        self.ui.table_customers.cellClicked.connect(self.customer_controller.handleCellClicked)

#___________________________________________________END CUSTOMERS_______________________________________________________________  

#___________________________________________________START MANAGES OEDER_________________________________________________________
        self.odermanage_controller = OrderManagementController(self.ui)

        self.odermanage_controller.load_oderDetail()
        self.ui.btn_addOderDetailProduct.clicked.connect(self.odermanage_controller.add_order_detail_slot)
        self.ui.btn_addOder.clicked.connect(self.odermanage_controller.add_oder)
        self.ui.btn_saveOder.clicked.connect(self.odermanage_controller.save_oder_sales)
        self.ui.btn_delOder.clicked.connect(self.odermanage_controller.reset_order_detail_form)




#___________________________________________________END MANAGES ODDER______________________________________________________



#___________________________________________________START Debts______________________________________________________        
        self.debts_controller = DebtsController(self.ui)
        self.debts_controller.load_all_debts()


#___________________________________________________END START Debts______________________________________________________  





#___________________________________________________START REPORT__________________________________________________________

#___________________________________________________END REPORT___________________________________________________________




#___________________________________________________START PRODUCT_______________________________________________________________

    def load_product(self):
        """Lấy tất cả sản phẩm từ cơ sở dữ liệu và hiển thị trên QTableWidget."""
        products = self.product_model.get_all_products()
        self.ui.table_Product.clear()  # Xóa dữ liệu hiện có trước khi tải
        self.ui.table_Product.setRowCount(len(products))  # Thiết lập số hàng
        self.ui.table_Product.setColumnCount(6)  # Ví dụ: ID, Tên, Đơn vị, Giá, Số lượng
        self.ui.table_Product.setHorizontalHeaderLabels(["MÃ SP", "Tên Sản Phẩm", "Đơn vị", "Giá", "Số lượng","Ghi chú"])

        for row, product in enumerate(products):
            for column, item in enumerate(product):
                if column == 3 :
                    formatted_value = self.format_price_for_display(item)
                    self.ui.table_Product.setItem(row, column, QTableWidgetItem(formatted_value))
                else:
                    self.ui.table_Product.setItem(row, column, QTableWidgetItem(str(item)))
        self.ui.label_id.setVisible(False)
        self.ui.id_Product.setVisible(False)
        self.hide_iput()
        self.configure_table()
    #chỉnh thuộc tính bản 
    def configure_table(self):
        self.ui.table_Product.verticalHeader().setVisible(False)
        self.ui.table_Product.resizeColumnsToContents()
        
        # Đặt độ rộng tối thiểu cho các cột sau khi đã điều chỉnh kích thước tự động
        min_column_width = 100  # Đặt độ rộng tối thiểu mà bạn muốn
        for i in range(self.ui.table_Product.columnCount()):
            current_width = self.ui.table_Product.columnWidth(i)
            if current_width < min_column_width:
                self.ui.table_Product.setColumnWidth(i, min_column_width)
            # Hoặc đảm bảo độ rộng tối thiểu không dưới một giá trị nhất định
            self.ui.table_Product.horizontalHeader().setMinimumSectionSize(min_column_width) 

        ##canh lê giữa cho cột  
        centerDelegate = CenterDelegate(self.ui.table_Product)
        for i in range(self.ui.table_Product.columnCount()):
            self.ui.table_Product.setItemDelegateForColumn(i, centerDelegate)

    #Thêm sản phẩm vào bảng
    def add_product_slot(self):
        # Lấy dữ liệu từ UI
        name = self.ui.name_Product.text()
        unit = self.ui.unit_Product.text()
        price = self.ui.price_Product.text().replace('.','')
        quantity = self.ui.quantity_Product.text()
        note = self.ui.note_Product.text()
        
        try:
            # Nếu bạn cần giá trị là số nguyên
            price = int(price)
            quantity = int(quantity)
        except ValueError as e:
            # Xử lý lỗi ở đây, ví dụ: hiển thị thông báo lỗi
            print("Lỗi khi chuyển đổi:", e)
            return
        # Kiểm tra dữ liệu nhập
        if not (name and unit and price and quantity):
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đủ thông tin sản phẩm!")
            return

        # Thêm sản phẩm
        product = (name, unit, float(price), int(quantity), note)
        self.product_model.add_product(product)
        
        # Hiển thị thông báo và làm mới danh sách sản phẩm hoặc làm sạch các trường nhập
        QMessageBox.information(self, "Thông báo", "Sản phẩm đã được thêm thành công!")
        # Ví dụ làm mới danh sách sản phẩm
        self.load_product()

        self.clear_content()

    def clear_content(self):
        self.ui.name_Product.clear()
        self.ui.unit_Product.clear()
        self.ui.price_Product.clear()
        self.ui.quantity_Product.clear()
        self.ui.note_Product.clear()
        self.ui.btn_save_Produuct.setEnabled(True)
        self.show_iput()
#khoá nhập liệu 
    def hide_iput(self):
        self.ui.name_Product.setEnabled(False)
        self.ui.name_Product.setStyleSheet("background-color:rgb(238, 249, 250);")
        self.ui.unit_Product.setEnabled(False)
        self.ui.unit_Product.setStyleSheet("background-color:rgb(238, 249, 250);")

        self.ui.price_Product.setEnabled(False)
        self.ui.price_Product.setStyleSheet("background-color:rgb(238, 249, 250);")

        self.ui.quantity_Product.setEnabled(False)
        self.ui.quantity_Product.setStyleSheet("background-color:rgb(238, 249, 250);")

        self.ui.note_Product.setEnabled(False)
        self.ui.note_Product.setStyleSheet("background-color:rgb(238, 249, 250);")

#Mờ Nhập Liệu
    def show_iput(self):
        self.ui.name_Product.setEnabled(True)
        self.ui.name_Product.setStyleSheet("background-color:rgb(255, 255, 255);")
        self.ui.unit_Product.setEnabled(True)
        self.ui.unit_Product.setStyleSheet("background-color:rgb(255, 255, 255);")

        self.ui.price_Product.setEnabled(True)
        self.ui.price_Product.setStyleSheet("background-color:rgb(255, 255, 255);")

        self.ui.quantity_Product.setEnabled(True)
        self.ui.quantity_Product.setStyleSheet("background-color:rgb(255, 255, 255);")

        self.ui.note_Product.setEnabled(True)
        self.ui.note_Product.setStyleSheet("background-color:rgb(255, 255, 255);")

#search product 
    def search_product_slot(self):
        # Lấy từ khóa tìm kiếm từ UI
        search_query = self.ui.line_find_Produuct.text()  # Giả sử bạn có QLineEdit tên là searchLineEdit

        # Thực hiện tìm kiếm
        products = self.product_model.search_products(search_query)
        
        # Cập nhật QTableWidget với kết quả tìm kiếm
        self.ui.table_Product.clearContents()  # Xóa nội dung hiện có
        self.ui.table_Product.setRowCount(len(products))  # Thiết lập số hàng mới dựa trên kết quả

        for row, product in enumerate(products):
            for column, item in enumerate(product):
                self.ui.table_Product.setItem(row, column, QTableWidgetItem(str(item)))

        # Điều chỉnh lại độ rộng cột và hàng dựa vào nội dung mới
        self.ui.table_Product.resizeColumnsToContents()
        self.ui.table_Product.resizeRowsToContents()
    #Hiện thi số dạng tiền
    def format_price_for_display(self, price):
        # Giả sử 'price' là một số nguyên
        formatted_text = "{:,.2f}".format(price).replace(',', 'x').replace('.', ',').replace('x', '.')
        return formatted_text
    def format_price(self, text):
        # Loại bỏ dấu phân cách cũ nếu có để tránh lỗi khi chuyển đổi
        plain_text = text.replace('.', '').replace(',', '')
        if not plain_text.isdigit():
            # Nếu không phải là số, đơn giản là trở về không làm gì cả
            return

        # Chuyển đổi chuỗi sang số
        number = int(plain_text)

        # Định dạng lại số theo chuẩn Việt Nam: dấu chấm cho phần thập phân, dấu phẩy cho hàng nghìn
        formatted_text = "{:,.0f}".format(number).replace(',', 'x').replace('.', ',').replace('x', '.')

        # Cập nhật lại giá trị của QLineEdit mà không kích hoạt sự kiện textEdited
        self.ui.price_Product.blockSignals(True)
        self.ui.price_Product.setText(formatted_text)
        self.ui.price_Product.blockSignals(False)
    #______________Xoá sản phầm_______________________________________
    def delete_product_slot(self):
        # Lấy hàng hiện tại đang được chọn
        current_row = self.ui.table_Product.currentRow()
        
        if current_row != -1:  # Kiểm tra xem có hàng nào được chọn không
            # Lấy giá trị ID sản phẩm từ cột đầu tiên của hàng được chọn
            product_id = self.ui.table_Product.item(current_row, 0).text()  # Giả sử ID sản phẩm nằm ở cột đầu tiên
            
            # Hỏi người dùng có chắc chắn muốn xóa không
            reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn xóa sản phẩm này không?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Gọi phương thức xóa sản phẩm từ product_model
                self.product_model.delete_product(product_id)
                
                # Hiển thị thông báo thành công
                QMessageBox.information(self, "Thành công", "Sản phẩm đã được xóa.")
                
                # Làm mới danh sách sản phẩm
                self.load_product()
        else:
            # Nếu không có hàng nào được chọn, hiển thị thông báo
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn sản phẩm cần xóa.")
    #update Sản phần 
    def update_product_slot(self):
        # Lấy thông tin từ giao diện

        product_id = self.ui.id_Product.text()
        name = self.ui.name_Product.text()
        unit = self.ui.unit_Product.text()
        price = self.ui.price_Product.text()
        quantity = self.ui.quantity_Product.text()
        note = self.ui.note_Product.text()

        if not product_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập ID sản phẩm.")
            return
        
        try:
            # Chuyển đổi giá và số lượng sang định dạng phù hợp
            price = float(price)
            quantity = int(quantity)
             # Tạo tuple sản phẩm từ thông tin nhập
            product = (name, unit, price, quantity, note)
            reply = QMessageBox.question(self, 'Xác nhận', 'Bạn có chắc chắn muốn sữa sản phẩm này không?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply==QMessageBox.StandardButton.Yes:
                self.product_model.update_product(product_id, product)
                self.load_product()
                QMessageBox.information(self, "Thành công", "Sản phẩm đã được cập nhật.")
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Giá hoặc số lượng không hợp lệ.")
            return

    def handleCellClicked(self, row, column):
    # Lấy dữ liệu từ hàng được chọn
        id_Product = self.ui.table_Product.item(row, 0).text()  # Giả sử cột 0 là ID sản phẩm
        name_Product = self.ui.table_Product.item(row, 1).text()  # Giả sử cột 1 là tên sản phẩm
        unit_Product = self.ui.table_Product.item(row, 2).text()  # Giả sử cột 2 là đơn vị
        price_Product = self.ui.table_Product.item(row, 3).text()  # Giả sử cột 3 là giá
        quantity_Product = self.ui.table_Product.item(row, 4).text()  # Giả sử cột 4 là số lượng
        note_Product = self.ui.table_Product.item(row, 5).text()  # Giả sử cột 5 là ghi chú

        # Gán dữ liệu vào các QLineEdit tương ứng
        self.ui.id_Product.setText(id_Product)
        self.ui.name_Product.setText(name_Product)
        self.ui.unit_Product.setText(unit_Product)
        self.ui.price_Product.setText(price_Product)
        self.ui.quantity_Product.setText(quantity_Product)
        self.ui.note_Product.setText(note_Product)
        self.ui.btn_save_Produuct.setEnabled(False)
        self.show_iput()

#___________________________________________END PRODUCT_______________________________________________________________________
    #show Home
    def show_home_page(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    #show Sản Phẩm
    def show_product_page(self):
        self.load_product()  # Tải lại danh sách sản phẩm mỗi khi người dùng chuyển đến tab sản phẩm
        self.ui.stackedWidget.setCurrentIndex(1)

    #show Hoá Đơn
    def show_oder_page(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    #Show Khách Hàng
    def show_customers_page(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    #Show Report 
    def show_report_page(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    #Show listoder_page 
    def show_list_oder_page(self):
        self.ui.stackedWidget.setCurrentIndex(6)
    #Show debts_page 
    def show_debts_oder_page(self):
        self.ui.stackedWidget.setCurrentIndex(5)
        self.debts_controller.load_all_debts()




if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
