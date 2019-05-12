"""This is init module."""
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Place where app is defined
app = Flask(__name__)
CORS(app)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'abcbank-portal'
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)

from app import accountsData
