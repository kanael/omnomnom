from peewee import *
from models import *

db.connect()

def create_restaurant(name, dishes):
    restaurant = Restaurant.create(name=name, address=u"איפושהו")
    restaurant.save()
    for dish_name in dishes:
        dish = Dish.create(name=dish_name, price=12.34, restaurant=restaurant)
        dish.save()

db.create_tables([Restaurant, Dish])
create_restaurant(u"פורטר ובניו", [u"המבורגר שפצלה", u"נקניקיות"])
create_restaurant(u"בראסרי", [u"המבורגר", u"עוף צרפתי"])
create_restaurant(u"פולקלה", [u"עוף בגריל", u"שניצל"])
