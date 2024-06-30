#file oderManage_controller.py
from PyQt6.QtWidgets import QMessageBox,QComboBox, QTableWidget, QTableWidgetItem, QComboBox ,QHeaderView,QLineEdit,QTreeWidget,QTreeWidgetItem,QStyledItemDelegate
from PyQt6.QtCore import Qt,QRegularExpressionMatch,QRegularExpression,QDate
from oderManage_model import OrderManagementModel
from report_model import ReportModel,DocumentComponents
from product_model import ProductModel
from customer_model import CustomerModel
from debts_model import DebtsModel
from reportlab.lib.styles import getSampleStyleSheet

from main_view import Ui_MainWindow
from PyQt6.QtGui import QRegularExpressionValidator
import locale

class CenterDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter
        super().paint(painter, option, index)

class OrderManagementController:
    def __init__(self, ui:Ui_MainWindow, parent=None):
        self.ui = ui
        self.parent = parent
        self.orderModel = OrderManagementModel("sales_management.db")
        self.customerModel = CustomerModel("sales_management.db")
        self.productModel = ProductModel("sales_management.db")
        self.debtsModel = DebtsModel("sales_management.db")

        styles = getSampleStyleSheet()
        components = DocumentComponents(styles)
        self.reportModel = ReportModel("sales_management.db", components)

        locale.setlocale(locale.LC_ALL,'vi_VN')

        self.populate_customers_combobox()
        self.Load_orders_QTree_Table()
        self.ui.treeWidget_ListOder.itemClicked.connect(self.on_order_selected)

        self.ui.print_report_oder.clicked.connect(self.reportModel.generate_orders_report)


        self.ui.oder_Cbb_Customer.addItem("")
        self.start_load()
        self.ui.table_oderDetail.cellChanged.connect(self.calculate_totals)
        self.ui.lineE_Tax.textChanged.connect(self.calculate_totals)
        self.ui.lineE_discount.textChanged.connect(self.calculate_totals)

        #sử lý textchange Giá sản phần trong oderdetail  
        #even indexx change combobox 
        self.ui.oder_Cbb_Customer.currentIndexChanged.connect(self.get_address_by_id_customers)
        #cân chỉnh bảng list  hoá  đơN 
        header = self.ui.treeWidget_ListOder.header()
        #header.setMinimumSectionSize(50)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        # Kích hoạt các sự kiện

    def load_oderDetail(self):
        self.ui.table_oderDetail.setColumnCount(5)  # Đặt số lượng cột bạn cần
        self.ui.table_oderDetail.setHorizontalHeaderLabels(["ID Sản Phẩm", "Số Lượng", "Đơn Giá", "Thành Tiền", "Ghi Chú"])
        # Đảm bảo rằng bảng có thể tự động điều chỉnh độ rộng cột
        self.ui.table_oderDetail.horizontalHeader().setStretchLastSection(True)
        self.ui.table_oderDetail.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    #thêm hoá đơn
    def add_oder(self):
        self.ui.dateEdit_date_oder.setEnabled(True)
        self.ui.oder_Cbb_Customer.setEnabled(True)
        self.ui.payment_method_cbb.setEnabled(True)
        self.ui.order_address_customer.setEnabled(True)
        self.ui.btn_addOderDetailProduct.setEnabled(True)
        self.get_address_by_id_customers()
        #set curent date 
        self.ui.dateEdit_date_oder.setDate(QDate.currentDate())


 #thêm chi tiết hoá đơn
    def add_order_detail_slot(self):
        row_position = self.ui.table_oderDetail.rowCount()
        self.ui.table_oderDetail.insertRow(row_position)
        
        # Tạo và thêm QComboBox cho cột sản phẩm
        product_combobox = QComboBox()
        self.populate_products_combobox(product_combobox) 
        self.ui.table_oderDetail.setCellWidget(row_position, 0, product_combobox)
        quantity_edit = QLineEdit()
        price_edit = QLineEdit()
        amuont_edit = QLineEdit()
        amuont_edit.setReadOnly(True)
        
        
        quantity_edit.textChanged.connect(lambda: self.calculate_total_Product(row_position))
        price_edit.textChanged.connect(lambda: self.calculate_total_Product(row_position))
        price_edit.textChanged.connect(lambda text, pe=price_edit: self.on_price_edit_text_changed(pe))
        #price_edit.textChanged.connect(lambda: self.format_price_for_display(int(price_edit)))

        
        amuont_edit.textChanged.connect(lambda: self.calculate_totals(row_position))
        

        self.ui.table_oderDetail.setCellWidget(row_position, 1, quantity_edit)
        self.ui.table_oderDetail.setCellWidget(row_position, 2, price_edit)
      
        # Đặt cell cho thành tiền và ghi chú
        self.ui.table_oderDetail.setItem(row_position, 3, QTableWidgetItem())  # Thành tiền

        self.ui.table_oderDetail.setItem(row_position, 4, QTableWidgetItem())  # Ghi chú


    #Save hoá đơn : 
    def validate_order_details(self):
        # Kiểm tra các trường thông tin cơ bản
        order_date = self.ui.dateEdit_date_oder.date().toString("yyyy-MM-dd")
        customer_name = self.ui.oder_Cbb_Customer.currentText()
        payment_method = self.ui.payment_method_cbb.currentText()

        if not customer_name:
            QMessageBox.warning(self.parent, "Thông tin thiếu", "Vui lòng nhập tên khách hàng.")
            return False
        if not payment_method:
            QMessageBox.warning(self.parent, "Thông tin thiếu", "Vui lòng chọn phương thức thanh toán.")
            return False

        # Kiểm tra thông tin trong bảng chi tiết sản phẩm
        if self.ui.table_oderDetail.rowCount() == 0:
            QMessageBox.warning(self.parent, "Thông tin thiếu", "Không có sản phẩm nào được thêm vào đơn hàng.")
            return False

        for row in range(self.ui.table_oderDetail.rowCount()):
            quantity_edit = self.ui.table_oderDetail.cellWidget(row, 1)
            price_edit = self.ui.table_oderDetail.cellWidget(row, 2)

            try:
                quantity = float(quantity_edit.text())
                price = float(price_edit.text())
                if quantity <= 0 or price <= 0:
                    QMessageBox.warning(self.parent, "Dữ liệu không hợp lệ", f"Giá trị số lượng và giá bán phải lớn hơn 0. Lỗi ở hàng {row+1}.")
                    return False
            except ValueError:
                QMessageBox.warning(self.parent, "Dữ liệu không hợp lệ", f"Vui lòng nhập số hợp lệ cho số lượng và giá ở hàng {row+1}.")
                return False

        return True
    #save Odder 

    def save_oder_sales(self):
        if self.validate_order_details():
            print("Thông tin đầy đủ")
            order_date = self.ui.dateEdit_date_oder.date().toString("dd-MM-yyyy")
            customer_name = self.ui.oder_Cbb_Customer.currentText()
            payment_method = self.ui.payment_method_cbb.currentText()
            subtotal = self.ui.lineE_subtotal.text()
            tax = self.ui.lineE_Tax.text()
            discount = self.ui.lineE_discount.text()
            total_payment = self.ui.lineE_totalPayment.text()
            
            # Bước 1: Thêm hóa đơn và lấy order_id
            order_id = self.orderModel.add_order(order_date, customer_name, payment_method, subtotal, tax, discount, total_payment)
            
            if payment_method == "Công Nợ":
                date_oder = self.ui.dateEdit_date_oder.date()
                due_date = date_oder.addDays(15).toString("dd-MM-yyyy")
                self.debtsModel.add_debt_for_order(order_id, customer_name, total_payment, order_date, due_date)
                QMessageBox.information(self.parent, "Lưu Công Nợ thành công", "Công nợ lưu thành công!")
            
            # Bước 2: Duyệt qua bảng chi tiết sản phẩm và thêm từng sản phẩm vào CSDL
            for row in range(self.ui.table_oderDetail.rowCount()):
                product_combobox = self.ui.table_oderDetail.cellWidget(row, 0)
                if product_combobox is not None:  # Kiểm tra xem product_combobox có tồn tại không
                    product_id = product_combobox.currentData()
                    quantity_edit = self.ui.table_oderDetail.cellWidget(row, 1)
                    quantity = float(quantity_edit.text())
                    price_edit = self.ui.table_oderDetail.cellWidget(row, 2)
                    price = float(price_edit.text())
                    amount = quantity * price
                    note_edit = self.ui.table_oderDetail.cellWidget(row, 4)
                    note = note_edit.text() if note_edit else ""
                    
                    # Thêm chi tiết sản phẩm
                    self.orderModel.add_order_detail(order_id, product_id, quantity, price, amount, note)

            # Code lưu đơn hàng nếu tất cả dữ liệu hợp lệ
            QMessageBox.information(self.parent, "Thông báo", "Hóa đơn đã được lưu thành công!")
            self.reset_order_detail_form()
        else:
            # Không thực hiện lưu nếu dữ liệu không hợp lệ
            QMessageBox.warning(self.parent, "Lưu không thành công", "Không thể lưu hóa đơn do dữ liệu không hợp lệ hoặc thiếu.")


# reset table_oder_detail 
    def reset_order_detail_form(self):
        # Xóa tất cả hàng từ bảng
        self.ui.table_oderDetail.setRowCount(0)

        # Thiết lập lại các trường nhập liệu
        self.ui.dateEdit_date_oder.setDate(QDate.currentDate())
        self.ui.oder_Cbb_Customer.setCurrentIndex(0)
        self.ui.payment_method_cbb.setCurrentIndex(0)
        self.ui.lineE_subtotal.setText("")
        self.ui.lineE_Tax.setText("")
        self.ui.lineE_discount.setText("")
        self.ui.lineE_totalPayment.setText("")
        self.start_load()
#định dang kiểu số
    def on_price_edit_text_changed(self, price_edit):
        try:
            # Chỉ cố gắng chuyển đổi khi có giá trị
            if price_edit.text():
                price = int(price_edit.text())
                print("Giá trị chuyển đổi thành số nguyên là:", price)
                # Có thể thực hiện thêm các thao tác với giá trị 'price' ở đây
        except ValueError:
            print("Giá trị nhập không phải là số.")

    def populate_products_combobox(self, combobox):
        products = self.productModel.get_all_products()
        for product in products:
            combobox.addItem(product[1], product[0])  # product[1] là tên sản phẩm, product[0] là ID

    def calculate_total_Product(self, row):
        
        row = int(row)
        print(row)
        quantity_widget = self.ui.table_oderDetail.cellWidget(row, 1)
        price_widget = self.ui.table_oderDetail.cellWidget(row, 2)

        if quantity_widget is not None and price_widget is not None:
            try:
                quantity = int(quantity_widget.text())
                price = float(price_widget.text())
                total = quantity * price
                format_total = self.format_price_for_display(total)
                # Đảm bảo bạn đang tạo QTableWidgetItem mới để đặt vào cell
                self.ui.table_oderDetail.setItem(row, 3, QTableWidgetItem(str(format_total)))
            except ValueError:
                self.ui.table_oderDetail.setItem(row, 3, QTableWidgetItem(""))
        else:
            print("Không tìm thấy widget tại hàng:", row)

    def calculate_totals(self):
        subtotal = 0.0
        for row in range(self.ui.table_oderDetail.rowCount()):
            # Lấy QLineEdit cho quantity và price
            quantity_widget = self.ui.table_oderDetail.cellWidget(row, 1)
            price_widget = self.ui.table_oderDetail.cellWidget(row, 2)
            
            if quantity_widget and price_widget:
                try:
                    quantity = float(quantity_widget.text())
                    price = float(price_widget.text().replace(',', '.'))
                    subtotal += quantity * price
                except ValueError:
                    continue  # Bỏ qua hàng này nếu không phải là số

        tax_rate = float(self.ui.lineE_Tax.text().replace(',', '.')) / 100 if self.ui.lineE_Tax.text() else 0
        discount = float(self.ui.lineE_discount.text().replace(',', '.')) if self.ui.lineE_discount.text() else 0

        tax_amount = subtotal * tax_rate
        total_payment = subtotal + tax_amount - discount
        
        # Định dạng giá trị sau khi đã thực hiện tính toán
        formatted_subtotal = "{:,.2f}".format(subtotal).replace(",", "x").replace(".", ",").replace("x", ".")
        #formatted_discount = "{:,.2f}".format(discount).replace(",", "x").replace(".", ",").replace("x", ".")
        formatted_total_payment = "{:,.2f}".format(total_payment).replace(",", "x").replace(".", ",").replace("x", ".")
        
        # Cập nhật giá trị lên UI
        self.ui.lineE_subtotal.setText(formatted_subtotal)
        # Chỉ cập nhật lại nếu bạn muốn hiển thị giá trị đã định dạng, nhưng lưu ý làm điều này có thể làm người dùng nhầm lẫn khi nhập
        #self.ui.lineE_discount.setText(formatted_discount)
        self.ui.lineE_totalPayment.setText(formatted_total_payment)
#populate customer 
    def populate_customers_combobox(self):
        customers  = self.customerModel.get_all_customers()
        for customer  in customers:
            self.ui.oder_Cbb_Customer.addItem(customer[1], customer[0]) 
#Get Address by ID customer ()
    def get_address_by_id_customers(self):
        customer_id = self.ui.oder_Cbb_Customer.currentData()
        address_customer = self.customerModel.get_customer_address_by_id(customer_id)
        self.ui.order_address_customer.setText(address_customer)

# start load form 


    def start_load(self):
        self.ui.label_idOder.setVisible(False)
        self.ui.lineEdit_oder.setVisible(False)
        self.ui.dateEdit_date_oder.setEnabled(False)
        self.ui.oder_Cbb_Customer.setEnabled(False)
        self.ui.payment_method_cbb.setEnabled(False)
        self.ui.order_address_customer.setEnabled(False)
        self.ui.btn_addOderDetailProduct.setEnabled(False)

    def format_price_for_display(self, price):
        # Giả sử 'price' là một số nguyên
        formatted_text = "{:,.0f}".format(price).replace(',', 'x').replace('.', ',').replace('x', '.')
        return formatted_text
    #############
    def Load_orders_QTree_Table(self):
        """Điền dữ liệu hóa đơn vào QTreeWidget."""
        tree_widget = self.ui.treeWidget_ListOder
        tree_widget.clear()  # Xóa các mục hiện có
        #canh lê QtreeWidget 
        centerDelegate = CenterDelegate(self.ui.treeWidget_ListOder)
        for i in range(self.ui.treeWidget_ListOder.columnCount()):
            self.ui.treeWidget_ListOder.setItemDelegateForColumn(i, centerDelegate)

        tree_widget.setHeaderLabels(["Mã HĐ", "Ngày HĐ", "Khách Hàng", "Phương Thức Thanh Toán", "Tổng Cộng", "Thuế", "Giảm giá", "Tổng Thanh Toán"])

        orders = self.orderModel.get_all_orders()  # Gọi hàm từ model
        for order in orders:
            # Tạo một QTreeWidgetItem cho mỗi hóa đơn
            item = QTreeWidgetItem(tree_widget)
            item.setText(0, str(order[0]))  # order_id
            item.setText(1, order[1])       # order_date
            item.setText(2, order[2])       # customer_name
            item.setText(3, order[3])       # payment_method
            item.setText(4, str(order[4]))  # subtotal
            item.setText(5, str(order[5]))  # tax
            item.setText(6, str(order[6]))  # discount
            item.setText(7, str(order[7]))  # total_payment
            tree_widget.addTopLevelItem(item)
            last_item = item  # Lưu lại item cuối cùng
        if 'last_item' in locals():  # Kiểm tra xem biến last_item đã được khai báo trong phạm vi hiện tại chưa
            if last_item:
                tree_widget.scrollToItem(last_item)

#hiển thị hoá đơn chi tiết khi click 
    def on_order_selected(self, item, column):
        order_id = item.text(0)  # Giả sử ID hóa đơn được lưu ở cột đầu tiên
        details = self.orderModel.get_order_list_details(order_id)
        self.display_order_details(details)

    def display_order_details(self, details):
        detail_table = self.ui.tableWidget_list_oderdetail
        detail_table.clearContents()
        detail_table.setRowCount(0)
        detail_table.setColumnCount(6)

        detail_table.setHorizontalHeaderLabels(["Tên Sản Phẩm", "Tên Sản Phẩm", "Số Lượng", "Đơn Giá", "Thành Tiền", "Ghi Chú"])

        self.ui.tableWidget_list_oderdetail.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tableWidget_list_oderdetail.verticalHeader().setVisible(False)

        centerDelegate = CenterDelegate(self.ui.tableWidget_list_oderdetail)
        for i in range(self.ui.tableWidget_list_oderdetail.columnCount()):
            self.ui.tableWidget_list_oderdetail.setItemDelegateForColumn(i, centerDelegate)

        for detail in details:
            row_position = detail_table.rowCount()
            detail_table.insertRow(row_position)
            for i, value in enumerate(detail):
                if i == 0:  # Giả sử cột đầu tiên là ID sản phẩm
                    item = QTableWidgetItem(str(value))
                    detail_table.setItem(row_position, i, item)
                else:
                    # Định dạng số cho các cột tiếp theo
                    item = QTableWidgetItem("{:.2f}".format(float(value)) if isinstance(value, (int, float)) else str(value))
                    detail_table.setItem(row_position, i, item)


    '''
    def save_oder_sales(self):
        order_date = self.ui.dateEdit_date_oder.date().toString("yyyy-MM-dd")
        customer_name = self.ui.oder_Cbb_Customer.currentText()
        payment_method = self.ui.payment_method_cbb.currentText()
        subtotal= self.ui.lineE_subtotal.text()
        tax = self.ui.lineE_Tax.text()
        discount= self.ui.lineE_discount.text()
        total_payment= self.ui.lineE_totalPayment.text()
        
        # Bước 1: Thêm hóa đơn và lấy order_id
        order_id = self.orderModel.add_order(order_date, customer_name, payment_method,subtotal, tax,discount,total_payment)
        
        # Bước 2: Duyệt qua bảng chi tiết sản phẩm và thêm từng sản phẩm vào CSDL
        for row in range(self.ui.table_oderDetail.rowCount()):
            product_combobox = self.ui.table_oderDetail.cellWidget(row, 0)
            product_id = product_combobox.currentData()
            quantity_edit = self.ui.table_oderDetail.cellWidget(row, 1)
            quantity = float(quantity_edit.text())
            price_edit = self.ui.table_oderDetail.cellWidget(row, 2)
            price = float(price_edit.text())
            amount = quantity * price
            note_edit = self.ui.table_oderDetail.cellWidget(row, 4)
            note = note_edit.text() if note_edit else ""
            
            # Thêm chi tiết sản phẩm
            self.orderModel.add_order_detail(order_id, product_id, quantity, price, amount, note)
        
        QMessageBox.information(self.parent, "Thông báo", "Hóa đơn đã được lưu thành công!")
        self.reset_order_detail_form()
        '''