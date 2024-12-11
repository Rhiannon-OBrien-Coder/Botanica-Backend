from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras

store_blueprint = Blueprint('store_blueprint', __name__)

@store_blueprint.route('/store', methods=['GET'])
def store_index():
    return jsonify({"message": "store index lives here"})

@store_blueprint.route('/store', methods=['POST'])
def create_store():
    try:
        new_store = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO store (name, difficulty)
                        VALUES (%s, %s)
                        RETURNING *
                        """,
                        (new_store['name'], new_store['difficulty'])
        )
        created_store = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"store": created_store}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500