from peewee import *
from models import *

db.connect()
db.create_tables([Restaurant, Dish])

import json
restaurants = json.load(open("/Users/kanael/projects/omnomnom/all.json"))

for r in restaurants:
    print(r["id"])
    restaurant = Restaurant.create(name=r["name"], address=r["address"], phone=r.get("phone", ""),
                                   hours=", ".join(r["hours"]), url=r["url"])
    restaurant.save()
    for i, d in enumerate(r["dishes"]):
        print("#%s" % (i, ))
        dish = Dish.create(name=d["name"], price=d["price"], restaurant=restaurant)
        dish.save()
