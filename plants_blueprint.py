from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

plants_blueprint = Blueprint('plants_blueprint', __name__)

@plants_blueprint.route('/plants', methods=['GET'])
@token_required
def plant_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM plants WHERE gardener =" + str(g.user["id"]) + ";"
        cursor.execute(query)
        plants = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify({"plants": plants}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@plants_blueprint.route('/plants', methods=['POST'])
@token_required
def create_plants():
    try:
        new_plants = request.json
        new_plants["gardener"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO plants (gardener, name, type, shed)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """,
                        (new_plants['gardener'], new_plants['name'], new_plants['type'], new_plants['shed'])
        )
        created_plants = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"plants": created_plants}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500