import os
import jwt
import bcrypt
import psycopg2, psycopg2.extras
from flask import Blueprint, jsonify, request, g
from flask_cors import cross_origin
from db_helpers import get_db_connection
from auth_middleware import token_required

authentication_blueprint = Blueprint('authentication_blueprint', __name__)

@authentication_blueprint.route('/auth/signup', methods=['POST'])
@cross_origin()
def signup():
    try:
        new_user_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s;", (new_user_data["email"],))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            return jsonify({"error": "Email already in use"}), 400
        hashed_password = bcrypt.hashpw(bytes(new_user_data["password"], 'utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s) RETURNING id, email", (new_user_data["email"], hashed_password.decode('utf-8')))
        created_user = cursor.fetchone()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO shed (gardener, type)
                        VALUES (%s, %s)
                        RETURNING *
                        """,
                        (created_user['id'], 'beginner' )
        )
        created_shed = cursor.fetchone()
        connection.commit()
        token = jwt.encode(created_user, os.getenv('JWT_SECRET'))
        return jsonify({"token": token, "user": created_user, "shed": created_shed}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 401
    finally:
        connection.close()

@authentication_blueprint.route('/auth/signin', methods=["POST"])
@cross_origin()
def signin():
    try:
        sign_in_form_data = request.get_json()
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s;", (sign_in_form_data["email"],))
        existing_user = cursor.fetchone()
        if existing_user is None:
            return jsonify({"error": "Invalid credentials."}), 401
        password_is_valid = bcrypt.checkpw(bytes(sign_in_form_data["password"], 'utf-8'), bytes(existing_user["password"], 'utf-8'))
        if not password_is_valid:
            return jsonify({"error": "Invalid credentials."}), 401
        token = jwt.encode({"email": existing_user["email"], "id": existing_user["id"]}, os.getenv('JWT_SECRET'))
        return jsonify({"token": token}), 201
    except Exception as error:
        return jsonify({"error": "Invalid credentials."}), 401
    finally:
        connection.close()

@authentication_blueprint.route('/auth/<users_id>', methods=['GET'])
@cross_origin()
@token_required
def user_by_id(users_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM users WHERE id = " + str(users_id) + ";"
        cursor.execute(query)
        users = cursor.fetchall()
        if users:
            connection.commit()
            connection.close()
            return jsonify({"users": users}), 200
        else:
            connection.close()
            return jsonify({"error": "User not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@authentication_blueprint.route('/auth/<users_id>', methods=['PUT'])
@cross_origin()
@token_required
def update_user(users_id):
    try:
        updated_user_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (users_id,))
        user_to_update = cursor.fetchone()
        if user_to_update is None:
            return jsonify({"error": "Plot not found"}), 404
        connection.commit()
        if user_to_update["gardener"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("UPDATE users SET money = %s, day = %s WHERE id = %s RETURNING *",
                        (updated_user_data["money"], updated_user_data["day"], users_id))
        updated_user = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"updated_user": updated_user}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@authentication_blueprint.route('/auth/<user_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_user(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE users.id = %s", (user_id,))
        user_to_update = cursor.fetchone()
        if user_to_update is None:
            return jsonify({"error": "user not found"}), 404
        connection.commit()
        if user_to_update["author"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("DELETE FROM users WHERE users.id = %s", (user_id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "user deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500