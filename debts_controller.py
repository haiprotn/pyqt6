from PyQt6.QtWidgets import QMessageBox,QTableWidget,QTableWidgetItem,QStyledItemDelegate
from main_view import Ui_MainWindow
from debts_model import DebtsModel
from PyQt6.QtCore import Qt




class CenterDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter
        super().paint(painter, option, index)

class DebtsController:
    def __init__(self, ui:Ui_MainWindow, parent=None):
        self.ui = ui
        self.parent = parent
        self.debtsModel = DebtsModel("sales_management.db")


    def load_all_debts(self):
        """Tải và hiển thị thông tin công nợ."""
        debts = self.debtsModel.get_debt_all()
        self.ui.tableWidget_debts.clear()
        self.ui.tableWidget_debts.setRowCount(len(debts))#thiết lập số hàng
        # Đặt đúng số cột và sử dụng đúng table widget
        self.ui.tableWidget_debts.setColumnCount(7)  # Đặt số cột phù hợp với số tiêu đề cột
        self.ui.tableWidget_debts.setHorizontalHeaderLabels(["Mã CN", "MÃ HĐ", "Tên Khách Hàng", "Tổng Công Nợ", "Ngày Hết Hạn", "Số Tiền Đã TT", "Ghi chú"])
        
        for row, debt in enumerate(debts):
            for column, item in enumerate(debt):
                if item is None:
                    item = ''
                self.ui.tableWidget_debts.setItem(row, column, QTableWidgetItem(str(item)))
        self.configure_table()

    def configure_table(self):
        self.ui.tableWidget_debts.verticalHeader().setVisible(False)
        self.ui.tableWidget_debts.resizeColumnsToContents()
        
        # Đặt độ rộng tối thiểu cho các cột sau khi đã điều chỉnh kích thước tự động
        min_column_width = 100  # Đặt độ rộng tối thiểu mà bạn muốn
        for i in range(self.ui.tableWidget_debts.columnCount()):
            current_width = self.ui.tableWidget_debts.columnWidth(i)
            if current_width < min_column_width:
                self.ui.tableWidget_debts.setColumnWidth(i, min_column_width)
            # Hoặc đảm bảo độ rộng tối thiểu không dưới một giá trị nhất định
            self.ui.tableWidget_debts.horizontalHeader().setMinimumSectionSize(min_column_width) 

         ##canh lê giữa cho cột  
        centerDelegate = CenterDelegate(self.ui.tableWidget_debts)
        for i in range(self.ui.tableWidget_debts.columnCount()):
            self.ui.tableWidget_debts.setItemDelegateForColumn(i, centerDelegate)

    def show_debt_details(self, customer_id):
        """Hiển thị chi tiết nợ của khách hàng khi người dùng yêu cầu."""
        details = self.debtsModel.get_debt_details(customer_id)
        if details:
            # Xử lý hiển thị chi tiết nợ
            pass
        else:
            QMessageBox.information(self.parent, "Thông báo", "Không có chi tiết nợ cho khách hàng này.")
