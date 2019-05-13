"""This module will serve the api request."""
import datetime

import pymongo
import flask_bcrypt
from config import client
from app import app
from bson.objectid import ObjectId
from bson.json_util import dumps
from flask import request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity,
    create_access_token, create_refresh_token,
    jwt_refresh_token_required, get_raw_jwt
)
import unidecode
import json
import ast

role = {
    'admin': 'Admin',
    'normal': "Normal"
}

ITEM_PER_PAGE = 20

# Import the helpers module
# helper_module = imp.load_source('*', './app/helpers.py')


# Select the database
db = client.get_database("abcbankportal")
# Select the accountCollection
accountCollection = db.account
userCollection = db.user
blacklist = set()

@app.route('/api/v1/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        if not email:
            return jsonify({"msg": "Missing username parameter"}), 400
        if not password:
            return jsonify({"msg": "Missing password parameter"}), 400
        user = userCollection.find_one({'email': email})
        if not user:
            return jsonify({'ok': False, 'message': "Account does not exist"}), 400
        pw_match = flask_bcrypt.check_password_hash(user['password'], password)
        if not pw_match:
            return jsonify({'ok': False, 'message': "Password is wrong"}), 400
        del user['password']
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=email, expires_delta=expires)
        refresh_token = create_refresh_token(identity=email)
        user['token'] = access_token
        user['refresh'] = refresh_token
        page_sanitized = json.loads(dumps(user))
        return jsonify({'ok': True, 'data': page_sanitized}), 200
    except Exception, e:
        return e, 401


# Standard refresh endpoint. A blacklisted refresh token
# will not be able to access this endpoint
@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


# Endpoint for revoking the current users access token
@app.route('/api/v1/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200


@app.route("/api/v1/accounts/check_account_number", methods=['POST'])
@jwt_required
def check_existed_account_number():
    """
       Function to check existed account_number
       """
    current_user = get_jwt_identity()
    if current_user:
        found_user = userCollection.find_one({'email': current_user})
    if found_user:
        body = ast.literal_eval(json.dumps(request.get_json()))
        account_number = body['account_number']
        try:
            existed_account = accountCollection.find_one({'account_number': int(account_number)})
            if existed_account:
                return "Account number has existed already", 409
            else:
                return jsonify({'ok': True, 'message': "Account number is valid"}), 200
        except Exception, e:
            return e, 500
    return jsonify({'ok': False, 'message': "Can not check account number"}), 500


@app.route("/api/v1/accounts/check_email", methods=['POST'])
@jwt_required
def checkExistedEmail():
    """
       Function to check existed email
       """
    current_user = get_jwt_identity()
    if current_user:
        found_user = userCollection.find_one({'email': current_user})
    if found_user:
        body = ast.literal_eval(json.dumps(request.get_json()))
        email = body['email']
        try:
            existed_account = accountCollection.find_one({'email': email})
            if existed_account:
                return "Email has existed already", 409
            else:
                return jsonify({'ok': True, 'message': "Email is valid"}), 200
        except Exception, e:
            return e, 500
    return jsonify({'ok': False, 'message': "Can not check email"}), 500


@app.route("/api/v1/accounts", methods=['POST'])
@jwt_required
def createAccount():
    """
       Function to create new accounts.
       """
    current_user = get_jwt_identity()
    if current_user:
        found_user = userCollection.find_one({'email': current_user})
    if found_user:
        if found_user["role"] == role['admin']:
            try:
                # Create new accounts
                try:
                    body = ast.literal_eval(json.dumps(request.get_json()))

                    password_encode = flask_bcrypt.generate_password_hash(body['password']).decode('utf-8')
                    body['password'] = password_encode
                except Exception, e:
                    # Bad request as request body is not available
                    # Add message for debugging purpose
                    return e, 400

                record_created = accountCollection.insert(body)

                return jsonify(str(record_created)), 201
            except:
                # Error while trying to create the resource
                # Add message for debugging purpose
                return jsonify({'ok': True, 'message': "Create account failed"}), 500

    return jsonify({'ok': False, 'message': "Create account failed"}), 500

    # else:
    #     return "You don't have permission to access this url", 403


@app.route("/api/v1/accounts", methods=['GET'])
@jwt_required
def getAllAccount():
    """
       Function to fetch the accounts.
       """
    current_user = get_jwt_identity()
    if current_user:
        try:
            # Return all the records as query string parameters are not available
            fetched_accounts = accountCollection.find() \
                .sort([("account_number", pymongo.ASCENDING), ("lastname", pymongo.ASCENDING),
                       ("firstname", pymongo.ASCENDING), ("age", pymongo.ASCENDING)])
            if fetched_accounts.count > 0:
                # Prepare response if the accounts are found
                return dumps(fetched_accounts), 200
            else:
                # Return empty array if no accounts are found
                return jsonify([])
        except Exception, e:
            # Error while trying to fetch the resource
            # Add message for debugging purpose
            return "Get account failed", 500


@app.route("/api/v1/accounts/<account_id>", methods=['GET'])
@jwt_required
def getAccount(account_id):
    """
       Function to fetch the account.
       """
    current_user = get_jwt_identity()
    if current_user:
        try:
            # Decode account_id
            account_id = unidecode.unidecode(account_id)
            found_user = accountCollection.find_one({'_id': ObjectId(account_id)})
            if found_user:
                # Prepare response if the accounts are found
                return dumps(found_user), 200
            else:
                return "Account not found", 404

        except Exception, e:
            # Error while trying to fetch the resource
            # Add message for debugging purpose
            return "Get account failed", 500


@app.route("/api/v1/accounts/<account_id>", methods=['POST'])
@jwt_required
def updateAccount(account_id):
    """
       Function to update the account.
       """
    current_user = get_jwt_identity()
    if current_user:
        found_user = userCollection.find_one({'email': current_user})
    if found_user:
        if found_user["role"] ==  role['admin']:
            try:
                # Get the value which needs to be updated
                try:
                    body = ast.literal_eval(json.dumps(request.get_json()))
                except:
                    # Bad request as the request body is not available
                    # Add message for debugging purpose
                    return "No update data", 400

                # Decode account_id
                account_id = unidecode.unidecode(account_id)

                # Updating the account
                records_updated = accountCollection.update_one({'_id': ObjectId(account_id)}, {"$set": body})

                # Check if resource is updated
                if records_updated.modified_count > 0:
                    # Prepare the response as resource is updated successfully
                    return jsonify({'ok': True, 'message': "Update successfully"}), 200
                else:
                    # Bad request as the resource is not available to update
                    # Add message for debugging purpose
                    return "Account is not available to update", 404
            except Exception, e:
                # Error while trying to update the resource
                # Add message for debugging purpose
                return "Update failed", 500
    return jsonify({'ok': True, 'message': "Update succesfully"}), 200


@app.route("/api/v1/accounts/<account_id>", methods=['DELETE'])
@jwt_required
def deleteAccount(account_id):
    """
       Function to remove the account.
       """
    current_user = get_jwt_identity()
    if current_user:
        found_user = userCollection.find_one({'email': current_user})
    if found_user:
        if found_user["role"] == role['admin']:
            try:
                # Decode account_id
                account_id = unidecode.unidecode(account_id)
                # Delete the account
                delete_account = accountCollection.delete_one({'_id': ObjectId(account_id)})

                if delete_account.deleted_count > 0:
                    # Prepare the response
                    return jsonify({'ok': True, 'message': "Delete successfully"}), 200
                else:
                    # Resource Not found
                    return "Account not found", 404
            except:
                # Error while trying to delete the resource
                # Add message for debugging purpose
                return "Delete failed", 500
    return "Delete failed", 500


@app.route('/api/v1/accounts/search', methods=['GET'])
def search():
    try:
        search_data = request.get_json()
        text = search_data["text"]
        page_num = search_data['page_num'] - 1
        accountCollection.drop_indexes()
        accountCollection.create_index([("$**", pymongo.TEXT)])
        text_results = accountCollection.find({"$text": {"$search": "\"" + text + "\""}}) \
            .sort([("email", pymongo.ASCENDING), ("firstname", pymongo.ASCENDING), ("lastname", pymongo.ASCENDING)]) \
            .limit(ITEM_PER_PAGE).skip(ITEM_PER_PAGE * page_num)
        return dumps(text_results)
    except Exception, e:
        return e, 500


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
