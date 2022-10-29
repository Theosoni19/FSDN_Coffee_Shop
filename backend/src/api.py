import os
from tkinter import E
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():

    try:
        drinks = Drink.query.all()
        formatted_data = [ drink.short() for drink in drinks ]
        return jsonify(
            {
                "success": True,
                "drinks": formatted_data
            }
        ), 200
    except:
        abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():

    try:
        drinks = Drink.query.all()
        formatted_data = [ drink.long() for drink in drinks ]
        return jsonify(
            {
                "success": True,
                "drinks": formatted_data
            }
        ), 200
    except:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def register_new_drink():
    data = request.get_json()
    try:
        if data is not None:
            new_title = data.get('title', None)
            new_recipe = data.get('recipe', None)
            drink = Drink(title=new_title, recipe=new_recipe)
            drink.insert()
            formatted_data= list(drink.long())
                
            return jsonify(
                    {
                        "success":True,
                        "drinks": formatted_data
                    }
                ), 200
    except:
        abort(422)
        


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_detail(id):
    drink = Drink.query.get(id)

    try:
        if drink is None:
            abort(404)
        else:
            data = request.get_json()

            if data is not None:
                new_title = data.get('title', None)
                new_recipe = data.get('recipe', None)
                drink.title = new_title
                drink.recipe = new_recipe

                drink.update()
                formatted_data= list(drink.long())
                    
                return jsonify(
                        {
                            "success":True,
                            "drinks": formatted_data
                        }
                    ), 200
    except:
        abort(422)



@app.route('/drinks/<int:id>')
@requires_auth('delete:drinks')
def delete_drink(id):
    drink = Drink.query.get(id)

    try:
        if drink is None:
            abort(404)

        drink.delete()    
        return jsonify(
                    {
                        "success":True,
                        "delete": id
                    }
                ), 200
    except:
        abort(422)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def authentification_failed(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": AuthError.error.get('description')
    }), AuthError.status_code