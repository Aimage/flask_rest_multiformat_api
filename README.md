# flask_rest_multiformat_api

A lot of rest libs for flask focus on single format like jsonapi. When you need to have multiple format in each endpoint the it's not really easy.
Flask_rest_multiformat_api is designed to be provide multiple way to format the response of your api.
![architecture](/docs/img/archi.png)

## Install
Download the zip of this repository and run pip after extracting

`pip install flask_rest_multiformat_api`

## Basic usage
Create you model
```python
# -*- coding: utf-8 -*-

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from flask_rest_multiformat_api.view import ModelDetailView, ModelListView
from flask_rest_multiformat_api.api import RestApi

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# Create api model
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    engine_id = db.Column(db.String)

# Create the database.
db.create_all()

# Create api schema
class CarSchema(Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    engine_id = fields.String(required=True)


# Create views
class CarListView(ModelListView):
    model = Car
    schema = CarSchema
    session = db.session
    type = "car"
    data_format = "jsonapi"
    allowed_methods = ['GET', 'POST']

class CarDetailView(ModelDetailView):
    model = Car
    schema = CarSchema
    session = db.session
    type = "car"
    data_format = "jsonapi"

car_blueprint = Blueprint('car', __name__)

# Create the API + register view with blueprint
rest_api = RestApi(app)
rest_api.register_api(car_blueprint, CarListView, 'car_list', '/cars')
rest_api.register_api(car_blueprint, CarDetailView, 'car_detail', '/cars/<int:id>')
rest_api.register_blueprint(car_blueprint)

# run flask app
if __name__ == '__main__':
    app.run()

```

## Result routes

Endpoint       | Methods                 | Rule
-------------- | ----------------------- | -----------------------
car.car_detail | DELETE, GET, PATCH, PUT | /cars/<int:id>
car.car_list   | GET, POST               | /cars

