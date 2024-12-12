from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras

store_blueprint = Blueprint('store_blueprint', __name__)

@store_blueprint.route('/store', methods=['GET'])
def store_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM store"
        cursor.execute(query)
        store = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify({"store": store}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@store_blueprint.route('/store/<store_id>', methods=['GET'])
def store_by_id(store_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM store WHERE id =" + str(store_id) + ";"
        cursor.execute(query)
        store = cursor.fetchall()
        if store:
            connection.commit()
            connection.close()
            return jsonify({"store": store}), 200
        else:
            connection.close()
            return jsonify({"error": "store not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500

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
    
@store_blueprint.route('/store/<store_id>', methods=['PUT'])
def update_seed(store_id):
    try:
        store_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM store WHERE id = %s", (store_id,))
        store_to_update = cursor.fetchone()
        if store_to_update is None:
            return jsonify({"error": "Seed not found"}), 404
        connection.commit()
        cursor.execute("UPDATE store SET name = %s, diifficulty = %s WHERE id = %s RETURNING *",
                        (store_data["name"], store_data["diifficulty"], store_id))
        updated_store = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"updated_store": updated_store}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@store_blueprint.route('/store/<store_id>', methods=['DELETE'])
def delete_store(delete_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM store WHERE store.id = %s", (delete_id,))
        store_to_delete = cursor.fetchone()
        if store_to_delete is None:
            return jsonify({"error": "store not found"}), 404
        connection.commit()
        cursor.execute("DELETE FROM store WHERE store.id = %s", (delete_id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "store deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500