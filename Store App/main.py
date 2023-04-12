from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, session, redirect, url_for, request
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
#from form_helper import FormHelper
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
UPLOAD_FOLDER = 'static/product_pics'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class checkoutForm(Form):
    cardNumber = StringField(label=('Card Number:'),
        validators=[DataRequired(), 
        Length(min=16, max=16, message='Card Number must be 16 digits long') ])
    pay = SubmitField(label=('Submit'))

def get_basket():
    basket = []
    if 'Basket' in session:
        basket = {Product.get_product_from_id(product_id): int(quantity) for product_id, quantity in session['Basket'].items()}
    return basket

def get_basket_total(basket):
    total = 0
    for product, quantity in basket.items():
        total += (product.price * quantity)
    return total

@app.route('/', methods=["GET", "POST"])
def index():
    apply_sort = False
    apply_search = False
    sort_type = None
    search_query = None
    if 'Basket' not in session:
        session['Basket'] = {}
    if request.method == "POST":
        print(request.form)
        if 'SortBar' in request.form:
            apply_sort = True
            sort_type = request.form['SortBar']
        elif 'SearchBar' in request.form:
            apply_search = True
            search_query = request.form['SearchBar']
        else:
            quantity, product_id = None, None
            if 'quantity' in request.form:
                quantity = request.form['quantity']
            if 'product_id' in request.form:
                product_id = request.form['product_id']
            if quantity is not None and product_id is not None:
                if product_id in session['Basket']:
                    session['Basket'][product_id] = int(session['Basket'][product_id]) + int(quantity)
                else:
                    session['Basket'][product_id] = quantity
    if apply_sort:
        if sort_type == "Price":
            products = Product.query.order_by(Product.price).all()
        elif sort_type == "Standard":
            products = Product.query.all()
        elif sort_type == "Name":
            products = Product.query.order_by(Product.name).all()
    elif apply_search:
        products = Product.query.filter(Product.name.contains(search_query))
    else:
        products = Product.query.all()
    return render_template("index.html", products=products)

@app.route('/productPage/<product_id>/<product_name>', methods=["GET", "POST"])
def productPage(product_id, product_name):
    product = Product.get_product_from_id(int(product_id))
    return render_template("productPage.html", product=product)

@app.route('/basket', methods=["GET", "POST"])
def basket():
    if request.method == "POST":
        if 'ClearBasket' in request.form:
            # Clear basket
            session['Basket'] = {}
        else:
            # Update basket
            quantity, product_id = None, None
            if 'quantity' in request.form:
                quantity = request.form['quantity']
            if 'product_id' in request.form:
                product_id = request.form['product_id']
            if quantity is not None and product_id is not None:
                if product_id in session['Basket']:
                    if int(quantity) <= 0:
                        session['Basket'].pop(product_id)
                    else:
                        session['Basket'][product_id] = quantity

    basket = get_basket()
    total = get_basket_total(basket)
    
    return render_template("basket.html", basket=basket, total=total)

@app.route('/checkout', methods=["GET", "POST"])
def checkout():
    form = checkoutForm()
    if form.validate_on_submit():
        form.cardNumber.data = ''
    basket = get_basket()
    total = get_basket_total(basket)
    
    return render_template("checkout.html", basket=basket, total=total, form=form)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    price = db.Column(db.Float) 
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
        return (self.name+"\nPrice: "+str(self.price)+" ID: "+str(self.id))
    
if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    Product.add_item("Brown Leather strap", 59, "/static/product_pics/Brown_Leather_Strap.jpg")
    Product.add_item("Blue Watch Strap", 79, "/static/product_pics/Blue_Strap.jpg")
    Product.add_item("Black Watch Strap", 49, "/static/product_pics/Black_Strap.jpg")
    Product.add_item("Silver Link Watch Strap", 69, "/static/product_pics/Silver_Link_Strap.jpeg")
    
    app.run(debug=True)
