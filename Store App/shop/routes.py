from shop import app, db
from .models import Product, User, CustomerOrder
from flask import render_template, flash, session, redirect, url_for, request, json
from .form_helper import FormHelper
from .forms import CheckoutForm, LoginForm, CreateAccountForm, EditProfileForm
import os

#PRODUCT_UPLOAD_FOLDER = 'static/product_pics'
# Needs actual location when saving file
PROFILE_UPLOAD_FOLDER = 'shop/static/profile_pics'
default_pic = 'blank-user.png'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
form_helper = FormHelper(PROFILE_UPLOAD_FOLDER, ALLOWED_EXTENSIONS)

def get_orders_into_display_format(user_id):
    customer_orders = db.session.query(CustomerOrder).join(User).filter(User.id == user_id).all()
    orders = {}
    for customer_order in customer_orders:
        order_num = customer_order.id
        orders[order_num] = {}
        order_info = json.loads(customer_order.order)["order_items"]
        for item in order_info:
            product_id = item['product_id']
            quantity = item['quantity']
            product = Product.get_product_from_id(product_id)
            orders[order_num][product] = quantity
            
    return orders

    # ["order_id": {product: quantity for each item)]
    '''
    for order_id in order.keys():
    <h4> Order num: {{order_id}} </h4>
    for product, quantity in order[order_id].items():
    <p> product x quantity
    '''

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

def get_order_as_json():
    if 'Basket' in session:
        return {"order_items": [{"product_id": product_id, "quantity": quantity} for product_id, quantity in session['Basket'].items()]}
    else:
        return None
    
def checkIfQueryMet(query, text):
    if text[:len(query)].lower() == query.lower():
        return True
    else:
        return False

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
        elif 'SearchInput' in request.form:
            apply_search = True
            search_query = request.form['SearchInput']
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
        print("here")
        products = Product.query.filter(Product.name.ilike("%"+search_query+"%"))
        print("products: ",products)
    else:
        products = Product.query.all()
    return render_template("index.html", products=products)

@app.route('/search/<query>')
def search(query):
    #points = {"products": [{"name": product} for product in products if query.lower() in product.lower()]}
    products = Product.query.filter(Product.name.ilike(query+"%"))
    points = {"products": [{"name": product.name, "id":product.id} for product in products]}

    return json.dumps(points)

@app.route('/productPage/<product_id>/<product_name>', methods=["GET", "POST"])
def productPage(product_id, product_name):
    if request.method == "POST":
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
    form = CheckoutForm(request.form)
    if request.method == 'POST' and form.validate():
        if 'logged' in session:
            basket_as_json = get_order_as_json()
            user = User.get_user_from_username(session['username'])
            if user is not None:
                if basket_as_json is not None:
                    CustomerOrder.add_order(basket_as_json, user.id)
                    flash('Order successfull')
                                        
    basket = get_basket()
    total = get_basket_total(basket)
    
    return render_template("checkout.html", basket=basket, total=total, form=form)

# ACCOUNT RELATED ROUTES

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        # Check for valid login here
        user = User.get_user_from_username(username)
        if user is not None:
            if user.verify_password(password):
                session['logged'] = True
                session['username'] = username
                return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    form = CreateAccountForm(request.form)
    if request.method == 'POST' and form.validate():
        # TODO - ADD OTHER ACCOUNT DETAILS TO DATABASE
        username = form.username.data
        password = form.password.data
        file = request.files[form.profile_pic.name]
        filename = file.filename
        # Check if an account with this username is already created
        user = User.get_user_from_username(username)
        if user is None:
            if filename == "" or filename is None:  
                User.register(username, password, default_pic)
            else:
                profile_pic = form_helper.upload_file(file)
                User.register(username, password, profile_pic)

            flash('Account created successfully')
            return redirect(url_for('login'))
        else:
            flash('Account with this username already exists')

    return render_template('create_account.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    form = EditProfileForm(request.form)
    current_pic = None
    orders = None
    if 'logged' in session:
        user = User.get_user_from_username(session['username'])

        orders = get_orders_into_display_format(user.id)
            
        current_pic = user.profile_pic
        if request.method == 'POST' and form.validate:
            file = request.files[form.profile_pic.name]
            profile_pic = form_helper.upload_file(file)
            
            if profile_pic is not None:
                # Store old profile pic
                old_profile_pic = user.profile_pic

                # Add new profile pic
                User.update_profile_pic(user, profile_pic)

                # Remove old profile pic
                old_pic_location = PROFILE_UPLOAD_FOLDER+"/"+old_profile_pic
                if os.path.exists(old_pic_location):
                    if old_profile_pic != default_pic:
                        os.remove(old_pic_location)
                else:
                    print("The file does not exist")

                # Redirect to refresh page so current pic no shows up on profile
                return redirect(url_for('profile'))
            
        return render_template('profile.html', form=form, orders=orders, current_pic=current_pic, logged=("logged" in session))
        
    return redirect(url_for('login'))
