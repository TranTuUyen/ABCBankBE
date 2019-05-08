"""This module will serve the api request."""
import os
import datetime

import flask_bcrypt

from config import client
from app import app
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import request, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)
import unidecode
import json
import ast
import imp
import logging
from account import validate_user

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')



# Select the database
db = client.ABCBankDatabase
# Select the collection
collection = db.account


@app.route("/")
def get_initial_response():
    """Welcome message for the API."""
    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Welcome to the Flask API'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp

@app.route('/api/v1/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    data = request.get_json()
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    user = collection.find_one({'email': email})
    v = 3
    b = user[password]
    a = user
    if user and flask_bcrypt.check_password_hash(user['password'], password):
        del user['password']
        access_token = create_access_token(identity=data)
        refresh_token = create_refresh_token(identity=data)
        user['token'] = access_token
        user['refresh'] = refresh_token
        return jsonify({'ok': True, 'data': user}), 200

    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200


# Protect a view with jwt_required, which requires a valid access token
# in the request to access.
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route("/api/v1/accounts", methods=['POST'])
def create_account():
    """
       Function to create new accounts.
       """
    try:
        # Create new accounts
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as request body is not available
            # Add message for debugging purpose
            return "", 400

        record_created = collection.insert(body)

        # Prepare the response
        if isinstance(record_created, list):
            # Return list of Id of the newly created item
            return jsonify([str(v) for v in record_created]), 201
        else:
            # Return Id of the newly created item
            return jsonify(str(record_created)), 201
    except:
        # Error while trying to create the resource
        # Add message for debugging purpose
        return "", 500


@app.route("/api/v1/accounts", methods=['GET'])
def fetch_accounts():
    """
       Function to fetch the accounts.
       """
    try:
        # Call the function to get the query params
        query_params = helper_module.parse_query_params(request.query_string)
        # Check if dictionary is not empty
        if query_params:

            # Try to convert the value to int
            query = {k: int(v) if isinstance(v, str) and v.isdigit() else v for k, v in query_params.items()}

            # Fetch all the record(s)
            records_fetched = collection.find(query)

            # Check if the records are found
            if records_fetched.count() > 0:
                # Prepare the response
                return dumps(records_fetched)
            else:
                # No records are found
                return "", 404

        # If dictionary is empty
        else:
            # Return all the records as query string parameters are not available
            if collection.find().count > 0:
                # Prepare response if the accounts are found
                return dumps(collection.find())
            else:
                # Return empty array if no accounts are found
                return jsonify([])
    except:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return "", 500

@app.route("/api/v1/accounts/<account_id>", methods=['GET'])
def fetch_account(account_id):
    """
       Function to fetch the account.
       """
    try:
        # Decode account_id
        account_id = unidecode.unidecode(account_id)
        found_account = collection.find_one({'_id': ObjectId(account_id)})
        if found_account:
            # Prepare response if the accounts are found
            return dumps(found_account)
        else:
            return "", 400

    except Exception, e:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return "", 500

@app.route("/api/v1/accounts/<account_id>", methods=['POST'])
def update_account(account_id):
    """
       Function to update the account.
       """
    try:
        # Get the value which needs to be updated
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            return "", 400

        # Decode account_id
        account_id = unidecode.unidecode(account_id)

        # Updating the account
        records_updated = collection.update_one({'_id': ObjectId(account_id)}, {"$set": body})

        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return "", 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return "", 404
    except:
        # Error while trying to update the resource
        # Add message for debugging purpose
        return "", 500


@app.route("/api/v1/accounts/<account_id>", methods=['DELETE'])
def remove_account(account_id):
    """
       Function to remove the account.
       """
    try:
        # Decode account_id
        account_id = unidecode.unidecode(account_id)

        # Delete the account
        delete_account = collection.delete_one({'_id': ObjectId(account_id)})

        if delete_account.deleted_count > 0 :
            # Prepare the response
            return "", 204
        else:
            # Resource Not found
            return "", 404
    except:
        # Error while trying to delete the resource
        # Add message for debugging purpose
        return "", 500

@app.route('/api/v1/accounts/search')
def search():
    query = request.form['q']
    text_results = db.command('text', 'firstname', search=query, limit=20)
    doc_matches = (res['obj'] for res in text_results['results'])
    # return render_template("search.html", results=results)
    return text_results

@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported. Please refer API documentation."
            }
    }
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp
