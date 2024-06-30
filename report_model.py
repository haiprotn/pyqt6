import sqlite3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image,Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from database import create_connection, close_connection

# Cấu hình font
font_paths = {
    'Segoe UI Light': r'./Font/segoeuil.ttf',
    'Segoe UI Bold': r'./Font/segoeuib.ttf'
}

for font_name, font_path in font_paths.items():
    pdfmetrics.registerFont(TTFont(font_name, font_path))

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'TitleStyle',
    parent=styles['Title'],
    fontName='Segoe UI Bold',
    fontSize=24,
    leading=28,
    alignment=TA_CENTER,
    spaceAfter=20,
    textColor=colors.darkblue
)

class DocumentComponents:
    def __init__(self, styles):
        self.styles = styles

    def add_logo(self, path, width=100, height=50):
        """Thêm logo vào tài liệu."""
        logo = Image(path, width=width, height=height)
        return logo

    def add_company_info(self, name, address, phone):
        """Thêm thông tin công ty vào tài liệu."""
        info_content = f"{name}<br/>{address}<br/>Điện thoại: {phone}"
        company_style = ParagraphStyle(
            'CompanyInfo',
            parent=self.styles['Normal'],
            fontName='Segoe UI Bold',
            fontSize=12,
            leading=14,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        company_info = Paragraph(info_content, company_style)
        return company_info

class ReportModel:
    def __init__(self, db_path, components:DocumentComponents):
        self.db_path = db_path
        self.components = components

    def fetch_data(self, sql):
        conn = create_connection(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            close_connection(conn)

    def get_report_all_orders(self):
        sql = ''' SELECT id, order_date, customer_name, payment_method, subtotal, tax, discount, total_payment FROM orders '''
        return self.fetch_data(sql)

    def generate_orders_report(self):
        left_margin = 50  # lề trái 50 points
        right_margin = 50 # lề phải 50 points
        top_margin = 50   # lề trên 50 points
        bottom_margin = 50 # lề dưới 50 points
        document = SimpleDocTemplate(
                "orders_report.pdf",
                pagesize=A4,
                leftMargin=left_margin,
                rightMargin=right_margin,
                topMargin=top_margin,
                bottomMargin=bottom_margin
            )

        elements = []

        # Tạo logo và thông tin công ty
        logo = self.components.add_logo('.\\img\\logo.png', width=80, height=50)
        company_info = self.components.add_company_info('Cữa hàng Vi Tính Nghĩa Thành', 'Phường 4, TP. TÂY NINH','0976780204')

        # Tạo một bảng để chứa logo và thông tin công ty
        header_data = [[logo, company_info]]
        header_table = Table(header_data, colWidths=[120, 370])  # Thay đổi colWidths theo kích thước mong muốn
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))  # Thêm khoảng cách giữa header và tiêu đề báo cáo

        # Thêm tiêu đề báo cáo
        report_title = Paragraph("BÁO CÁO HOÁ ĐƠN BÁN HÀNG", title_style)
        elements.append(report_title)

        # Xử lý dữ liệu bảng hóa đơn như trước
        orders = self.get_report_all_orders()
        if orders:
            table_data = [["ID", "Ngày HĐ", "Khách Hàng", "PT-Thanh Toán", "Tổng Tiền", "Thuế", "Giảm Giá", "Tổng Thanh Toán"]]
            table_data.extend(orders)
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Segoe UI Light'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("Không có dữ liệu để hiển thị", styles['BodyText']))

        document.build(elements)
        print("PDF report has been created.")

# Khởi tạo và sử dụng
