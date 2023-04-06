from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, session, redirect, url_for, request
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
#from form_helper import FormHelper
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
UPLOAD_FOLDER = 'static/product_pics'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


@app.route('/', methods=["GET", "POST"])
def index():
    if 'Basket' not in session:
        session['Basket'] = {}
    if request.method == "POST":
        # Gets stored as: ImmutableMultiDict([('quantity', '2'), ('3', 'Add To Basket')])
        results = request.form.items()
        quantity, product_id = None, None
        for data in results:
            if data[0] == "quantity":
                quantity = data[1]
                print("Quantity("+quantity+")")
            elif data[1] == "Add To Basket":
                product_id = data[0]
            if quantity is not None and product_id is not None:
                if product_id in session['Basket']:
                    session['Basket'][product_id] = int(session['Basket'][product_id]) + int(quantity)
                else:
                    session['Basket'][product_id] = quantity
        
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route('/basket', methods=["GET", "POST"])
def basket():
    if request.method == "POST":
        # Gets stored as: ImmutableMultiDict([('quantity', '2'), ('3', 'Save')])
        # Update basket
        results = request.form.items()
        quantity, product_id = None, None
        for data in results:
            if data[0] == "quantity":
                quantity = data[1]
            elif data[1] == "Save":
                product_id = data[0]
            if quantity is not None and product_id is not None:
                if product_id in session['Basket']:
                    if int(quantity) <= 0:
                        session['Basket'].pop(product_id)
                    else:
                        session['Basket'][product_id] = quantity
    basket = []
    if 'Basket' in session:
        basket = {Product.get_product_from_id(product_id): int(quantity) for product_id, quantity in session['Basket'].items()}
    return render_template("basket.html", basket=basket)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    price = db.Column(db.String(64)) 
    picture = db.Column(db.String(512))

    @staticmethod
    def add_item(name, price, picture):
        product = Product(name=name, price=price, picture=picture)
        db.session.add(product)
        db.session.commit()

    def update_item_pic(product, picture):
        product.picture = picture
        db.session.commit()


    def get_product_from_id(item_id):
        product = Product.query.get(item_id)
        return product
        
    def __repr__(self):
        return (self.name+"\nPrice: "+self.price+" ID: "+str(self.id))
    
if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    Product.add_item("Black Watch Strap", 49, "static/product_pics/Black_Strap.jpg")
    Product.add_item("Brown Leather strap", 59, "static/product_pics/Brown_Leather_Strap.jpg")
    Product.add_item("Silver Link Watch Strap", 69, "static/product_pics/Silver_Link_Strap.jpeg")
    Product.add_item("Blue Watch Strap", 79, "static/product_pics/Blue_Strap.jpg")
    
    app.run(debug=True)
