from functools import wraps
from flask import request, jsonify
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        authorization_header = request.headers.get('Authorization')
        if authorization_header is None:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            token = authorization_header.split(' ')[1]
            jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
        except Exception as error:
            return jsonify({"error": str(error)}), 500
        return f(*args, **kwargs)
    return decorated_function
