from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras

seed_blueprint = Blueprint('seed_blueprint', __name__)

@seed_blueprint.route('/seeds', methods=['GET'])
def plot_options_index():
    return jsonify({"message": "seeds index lives here"})

@seed_blueprint.route('/seeds', methods=['POST'])
def create_seed():
    try:
        new_seed = request.json
        new_seed["author"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO seeds (author, title, text, category)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """,
                        (new_seed['author'], new_seed['title'], new_seed['text'], new_seed['category'])
        )
        created_seed = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"seed": created_seed}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
