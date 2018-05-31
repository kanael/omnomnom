from peewee import *


db = SqliteDatabase('omnomnom.db')

class BaseModel(Model):
    class Meta:
        database = db

class Restaurant(BaseModel):
    name = CharField()
    address = CharField()

class Dish(BaseModel):
    name = CharField()
    price = DecimalField()
    restaurant = ForeignKeyField(Restaurant, backref='dishes')
