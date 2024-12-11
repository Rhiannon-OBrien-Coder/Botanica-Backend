from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras

seed_blueprint = Blueprint('seed_blueprint', __name__)

@seed_blueprint.route('/seeds', methods=['GET'])
def store_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM seeds"
        cursor.execute(query)
        seeds = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify({"seeds": seeds}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@seed_blueprint.route('/seeds/<seed_id>', methods=['GET'])
def seeds_by_id(seed_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM seeds WHERE id =" + str(seed_id) + ";"
        cursor.execute(query)
        seeds = cursor.fetchall()
        if seeds:
            connection.commit()
            connection.close()
            return jsonify({"seeds": seeds}), 200
        else:
            connection.close()
            return jsonify({"error": "Seed not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@seed_blueprint.route('/seeds', methods=['POST'])
def create_seed():
    try:
        new_seed = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO seeds (name, description, season, price, growth_period, store)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (new_seed['name'], new_seed['description'], new_seed['season'], new_seed['price'], new_seed['growth_period'], new_seed['store'])
        )
        created_seed = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"seed": created_seed}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
