from flask import Flask
from views.products_views import products_bp

app = Flask(__name__)
app.register_blueprint(products_bp)
