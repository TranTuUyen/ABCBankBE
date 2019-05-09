"""This module is to configure app to connect with database."""

from pymongo import MongoClient

# DATABASE = MongoClient()['ABCBankDatabase'] # DB_NAME
# DEBUG = True
# client = MongoClient('localhost', 27017)

MONGODB_URI = "mongodb://trantuuyen:password1@ds153766.mlab.com:53766/abcbankportal"
client = MongoClient(MONGODB_URI, connectTimeoutMS=30000)

