from flask import Flask, render_template, session, redirect, url_for, request, json
from flask.ext.bootstrap import Bootstrap


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'

PRODUCT_UPLOAD_FOLDER = 'static/product_pics'
PROFILE_UPLOAD_FOLDER = 'static/profile_pics'
default_pic = 'static/profile_pics/blank-user.jpeg'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

bootstrap = Bootstrap(app)

def checkIfQueryMet(query, text):
    if text[:len(query)].lower() == query.lower():
        return True
    else:
        return False

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pass
    return render_template("index.html", products=products)

@app.route('/search/<query>')
def search(query):
    #points = {"products": [{"name": product} for product in products if query.lower() in product.lower()]}
    points = {"products": [{"name": product} for product in products if checkIfQueryMet(query, product)]}

    return json.dumps(points)
    
if __name__ == "__main__":
    products = ['Blue strap', 'Black strap', 'Purple strap', '3 in 1 Charger', 'Grey Milan strap', 'Brown Leather strap']
    app.run(debug=True)

    
