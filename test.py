from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def create_invoice(invoice_data, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Thêm tiêu đề
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "Hóa Đơn Bán Hàng")

    # Thông tin công ty
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 100, "Công Ty ABC")
    c.drawString(100, height - 120, "Địa chỉ: 123 Đường XYZ, Tp.HCM")

    # Thông tin khách hàng
    c.drawString(100, height - 160, f"Khách hàng: {invoice_data['customer_name']}")
    c.drawString(100, height - 180, f"Địa chỉ: {invoice_data['customer_address']}")

    # Chi tiết hóa đơn
    y_position = height - 220
    c.drawString(100, y_position, "Sản phẩm")
    c.drawString(300, y_position, "Số lượng")
    c.drawString(400, y_position, "Đơn giá")
    c.drawString(500, y_position, "Thành tiền")

    for item in invoice_data['items']:
        y_position -= 20
        c.drawString(100, y_position, item['name'])
        c.drawString(300, y_position, str(item['quantity']))
        c.drawString(400, y_position, f"{item['price']:,.0f} VNĐ")
        c.drawString(500, y_position, f"{item['total']:,.0f} VNĐ")

    # Tổng cộng
    c.drawString(400, y_position - 40, "Tổng cộng:")
    c.drawString(500, y_position - 40, f"{invoice_data['total']:,.0f} VNĐ")

    c.save()

# Dữ liệu hóa đơn mẫu
invoice_data = {
    'customer_name': 'Nguyen Van A',
    'customer_address': '456 Đường KLM, Tp.HCM',
    'items': [
        {'name': 'Sản phẩm 1', 'quantity': 2, 'price': 150000, 'total': 300000},
        {'name': 'Sản phẩm 2', 'quantity': 1, 'price': 200000, 'total': 200000}
    ],
    'total': 500000
}

create_invoice(invoice_data, "invoice.pdf")
