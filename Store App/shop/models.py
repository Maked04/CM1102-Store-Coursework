from shop import db
from flask import json
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    password_hash = db.Column(db.String(64)) 
    profile_pic = db.Column(db.String(512))
    order = db.relationship('Customer', backref='user', lazy=True)

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

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    surname = db.Column(db.String(32))
    email_address = db.Column(db.String(128))
    phone_number = db.Column(db.Integer())
    address_line_1 = db.Column(db.String(128))
    address_line_2 = db.Column(db.String(64))
    country = db.Column(db.String(64))
    city = db.Column(db.String(32))
    postcode = db.Column(db.String(7))

    card_number = db.Column(db.String(16))
    name_on_card = db.Column(db.String(32))
    expiry_date = db.Column(db.String(8))
    csv = db.Column(db.String(3))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    order = db.relationship('Order', backref='customer', lazy=True)

    def add_customer(user_id, first_name, surname, email_address, phone_number, \
                     address_line_1, address_line_2, country, city, postcode, \
                     card_number, name_on_card, expiry_date, csv):
        if user_id is not None:
            customer = Customer(user_id=user_id, first_name=first_name, surname=surname,\
                                email_address=email_address, phone_number=phone_number, address_line_1=address_line_1,\
                                address_line_2=address_line_2, country=country, city=city, postcode=postcode, \
                                card_number=card_number, name_on_card=name_on_card, expiry_date=expiry_date, csv=csv)
        else:
            customer = Customer(card_number=card_number)

        db.session.add(customer)
        db.session.commit()

        return customer.id
        

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    discount = db.Column(db.Float, nullable=True)

    def add_order_item(order_id, product_id, price, quantity, discount):
        if discount is not None:
            order_item = OrderItem(order_id=order_id, product_id=product_id, price=price, quantity=quantity, discount=discount)
        else:
            order_item = OrderItem(order_id=order_id, product_id=product_id, price=price, quantity=quantity)

        db.session.add(order_item)
        db.session.commit()


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_item = db.relationship('OrderItem', backref='order', lazy=True)
    shipping_type = db.Column(db.String(32))


    def add_order(customer_id, items, shipping_type):
        order = Order(customer_id=customer_id, shipping_type=shipping_type)
        db.session.add(order)
        db.session.commit()
        Order.add_order_items(order.id, items)
        return order.id

    def add_order_items(order_id, items):
        # Function is within Order so can only be called within Order context
        # form is [{"product_id": , "price": , "quantity": , "discount": }, {}]
        for item in items: 
            OrderItem.add_order_item(order_id, item["product_id"], item["price"], item["quantity"], item["discount"])

    def __repr__(self):
        return '<Order %r>' % self.customer_id
        
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    price = db.Column(db.Float) 
    picture = db.Column(db.String(512))
    description = db.Column(db.String(512))
    ecological_footprint = db.Column(db.String(512))
    order_item = db.relationship('OrderItem', backref='product', lazy=True)

    @staticmethod
    def add_item(name, price, picture, description, ecological_footprint):
        product = Product(name=name, price=price, picture=picture, description=description, ecological_footprint=ecological_footprint)
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

restart = False
#restart = True
if restart:
    #Product.__table__.drop(db.engine)
    db.drop_all()

db.create_all()

if restart:
    Product.add_item("Brown Leather strap", 59, "/static/product_pics/Brown_Leather_Strap.png", "Crafted from the finest quality Italian Leather and lined with soft Nubuck, this Paraphonalia strap takes the Apple Watch to a whole new level of luxury and sophistication", "50% recyclable")
    Product.add_item("Blue Watch Strap", 79, "/static/product_pics/Blue_Milan_Strap.png", "Modern and ultra-sleek. A unique spin on a 19th-century design that first originated in Milan, the Milanese Loop is infinitely adjustable to fit your wrist perfectly. Made from intricately woven stainless steel and fastened using a strong magnetic clasp, this strap takes seconds to put on or take off.", "100% Recyclable")
    Product.add_item("Black Watch Strap", 49, "/static/product_pics/Black_Milan_Strap.png", "Modern and ultra-sleek. A unique spin on a 19th-century design that first originated in Milan, the Milanese Loop is infinitely adjustable to fit your wrist perfectly. Made from intricately woven stainless steel and fastened using a strong magnetic clasp, this strap takes seconds to put on or take off.", "100% Recyclable")
    Product.add_item("Silver Link Watch Strap", 69, "/static/product_pics/Silver_Link_Strap.png", "Crafted from 316L stainless steel and fastened using a hidden clasp, the link strap is designed to impress and built to last.", "Made from recycled metal")
    Product.add_item("Green Air Conditoning Unit", 100, "/static/product_pics/Green_Air_Conditioning_Unit.png", "This compact air conditional unit will run directly from your power supply, the sleek design will cool your room in style!", "Produces clean air")

    
