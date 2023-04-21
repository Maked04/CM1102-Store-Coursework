from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, session, redirect, url_for, request
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from form_helper import FormHelper
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'

PRODUCT_UPLOAD_FOLDER = 'static/product_pics'
PROFILE_UPLOAD_FOLDER = 'static/profile_pics'
default_pic = 'static/profile_pics/blank-user.png'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
form_helper = FormHelper(PROFILE_UPLOAD_FOLDER, ALLOWED_EXTENSIONS)

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
        products = Product.query.filter(Product.name.ilike("%"+search_query+"%"))
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

# ACCOUNT RELATED ROUTES

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check for valid login here
        user = User.get_user_from_username(username)
        if user is not None:
            if user.verify_password(password):
                session['logged'] = True
                session['username'] = username
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if an account with this username is already created
        user = User.get_user_from_username(username)
        if user is None:
            User.register(username, password, default_pic)
            return redirect(url_for('login'))
    return render_template('create_account.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    current_pic = None
    if 'logged' in session:
        user = User.get_user_from_username(session['username'])
        current_pic = user.profile_pic
        
        profile_pic = form_helper.upload_file(request)
        if profile_pic is not None:
            # Store old profile pic
            old_profile_pic = user.profile_pic

            # Add new profile pic
            User.update_profile_pic(user, profile_pic)

            # Remove old profile pic
            if os.path.exists(old_profile_pic):
                os.remove(old_profile_pic)
            else:
                print("The file does not exist")

            # Redirect to refresh page so current pic no shows up on profile
            return redirect(url_for('profile'))

        print(current_pic)
        return render_template('profile.html', current_pic=current_pic, logged=("logged" in session))
        
    return redirect(url_for('login'))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    password_hash = db.Column(db.String(64)) 
    profile_pic = db.Column(db.String(512))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def register(username, password, profile_pic):
        user = User(username=username, profile_pic=profile_pic)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    def update_profile_pic(user, profile_pic):
        user.profile_pic = profile_pic
        db.session.commit()

    def get_user_from_username(username):
        user = User.query.filter_by(username=username).first()
        return user
        
    def __repr__(self):
        return '<User {0}>'.format(self.username)

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
    #db.drop_all()
    db.create_all()
    #Product.add_item("Brown Leather strap", 59, "/static/product_pics/Brown_Leather_Strap.jpg")
    #Product.add_item("Blue Watch Strap", 79, "/static/product_pics/Blue_Strap.jpg")
    #Product.add_item("Black Watch Strap", 49, "/static/product_pics/Black_Strap.jpg")
    #Product.add_item("Silver Link Watch Strap", 69, "/static/product_pics/Silver_Link_Strap.jpeg")
    
    app.run(debug=True)
