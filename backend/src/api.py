import os
from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail():
    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def add_drink():
    drink_title = request.get_json()['title']
    drink_recipe = str(request.get_json()['recipe'])

    new_drink = Drink(title=drink_title, recipe=drink_recipe.replace("'", "\""))

    try:
        new_drink.insert()
    except HTTPException as e:
        abort(e.code)

    return jsonify({
        "success": True,
        "drinks": [new_drink.long()]
    }), 200


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drink(id):
    drink = Drink.query.get(id)

    # Check if drink exists
    if not drink:
        abort(404)

    # Update the recorded drink
    try:
        data = request.get_json()
        if 'title' in data:
            drink.title = data['title']

        if 'recipe' in data:
            drink.recipe = str(data['recipe']).replace("'", "\"")

        drink.update();
    except HTTPException as e:
        abort(e.code)

    # return json response
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def dlt_drink(id):
    drink = Drink.query.get(id)

    # Check if drink exists
    if not drink:
        abort(404)

    try:
        # Delete record from the db
        drink.delete()
    except HTTPException as e:
        abort(e.code)

    # return json response
    return jsonify({
        "success": True,
        "drinks": id
    }), 200


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                "success": False,
                "error": 404,
                "message": "resource not found"
                }), 404


@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
                "success": False,
                "error": 500,
                "message": "internal sever error"
                }), 500

'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error_handler(authError):
    return jsonify({
        'success': False,
        'error': authError.status_code,
        'message': authError.error
    }), authError.status_code
