from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

plants_blueprint = Blueprint('plants_blueprint', __name__)

@plants_blueprint.route('/plants', methods=['GET'])
@token_required
def plot_index():
    return jsonify({"message": "plant index lives here"})

@plants_blueprint.route('/plants', methods=['POST'])
@token_required
def create_plants():
    try:
        new_plants = request.json
        new_plants["gardener"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO plantss (gardener, type, shed)
                        VALUES (%s, %s, %s)
                        RETURNING *
                        """,
                        (new_plants['gardener'], new_plants['type'], new_plants['shed'])
        )
        created_plants = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"plants": created_plants}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500