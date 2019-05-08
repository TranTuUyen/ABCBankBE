"""This is init module."""
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager

# Place where app is defined
app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

from app import accountsData
