from shop import db
from flask import json
from werkzeug.security import generate_password_hash, check_password_hash


class JsonEncodedDict(db.TypeDecorator):
    impl = db.Text
    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)

    def process_result_param(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), index=True, unique=True)
    password_hash = db.Column(db.String(64)) 
    profile_pic = db.Column(db.String(512))
    order = db.relationship('CustomerOrder', backref='user', lazy=True)

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
    

class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(JsonEncodedDict)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=True)
    
    def add_order(order, user_id):
        order = CustomerOrder(order=order, user_id=user_id)
        db.session.add(order)
        db.session.commit()
        
    def __repr__(self):
        return '<CustomerOrder %r>' % self.order


class Product(db.Model):
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

restart = False
#restart = True
if restart:
    db.drop_all()
db.create_all()
if restart:
    Product.add_item("Brown Leather strap", 59, "/static/product_pics/Brown_Leather_Strap.jpg")
    Product.add_item("Blue Watch Strap", 79, "/static/product_pics/Blue_Strap.jpg")
    Product.add_item("Black Watch Strap", 49, "/static/product_pics/Black_Strap.jpg")
    Product.add_item("Silver Link Watch Strap", 69, "/static/product_pics/Silver_Link_Strap.jpeg")
    
