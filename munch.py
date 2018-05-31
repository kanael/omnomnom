import json, glob, os

def parse_price(s):
    return float(str(s).replace('₪','').strip())

def munch_restaurants():
    restaurants = []
    all_dishes = []
    for restaurant_file in glob.glob("scraps/restaurants/*"):
        menu_file = restaurant_file.replace("restaurants", "menus")
        restaurant_id = restaurant_file.replace("restaurants", "")
        restaurant_info = json.load(open(restaurant_file))
        print (restaurant_id)
        if not os.path.isfile(menu_file):
            print ("no menu")
            continue
        restaurant_info["id"] = restaurant_id
        restaurants.append(restaurant_info)

        menu_info = json.load(open(menu_file))
        dishes = menu_info["dishes"]
        if (len(set([d["name"] for d in dishes])) != len(dishes)):
            print ("duplicate dishes")
            continue
        for i, dish in enumerate(dishes):
            print("#%s" % (i, ))
            dish["price"] = parse_price(dish["price"])
            dish["restaurant_id"] = restaurant_id
            all_dishes.append(dish)
    return dict(restaurants=restaurants, dishes=dishes)

json.dump(munch_restaurants(), open("all.json", "w"))
