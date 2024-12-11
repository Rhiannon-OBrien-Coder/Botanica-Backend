from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

plot_options_blueprint = Blueprint('plot_options_blueprint', __name__)

@plot_options_blueprint.route('/plot-options', methods=['GET'])
def plot_options_index():
    return jsonify({"message": "plot options index lives here"})

@plot_options_blueprint.route('/plot-options', methods=['POST'])
def create_plot_option():
    try:
        new_plot_option = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO plot_options (name, description, season, price, store)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (new_plot_option['name'], new_plot_option['description'], new_plot_option['season'], new_plot_option['price'], new_plot_option['store'])
        )
        created_plot_option = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"plot_option": created_plot_option}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500