from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

user_schema = {
    "type": "object",
    "properties": {
        "balance": {
            "type": "int"
        },
        "firstname": {
            "type": "string",
        },
        "lastname": {
            "type": "string",
        },
        "age": {
            "type": "int"
        },
        "gender": {
            "type": "string",
        },
        "address": {
            "type": "string",
        },
        "employer": {
            "type": "string",
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "city": {
            "type": "string",
        },
        "state": {
            "type": "string",
        },
        "password": {
            "type": "string",
            "minLength": 5
        },
        "role": {
            "type": "string"
        }
    },
    "required": ["email", "password"],
    "additionalProperties": False
}


def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}