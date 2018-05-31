from flask import Flask
from datetime import datetime
app = Flask(__name__)

from models import *
from flask import jsonify
import json
from flask import request

db.connect()

@app.route('/search')
def search():
    dishes = Dish.select().where(Dish.name.contains(request.args.get("q")))
    data = [dict(name=d.name, price=float(d.price), restaurant=d.restaurant.name) for d in dishes]
    return json.dumps(data)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
