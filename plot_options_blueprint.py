from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

plot_options_blueprint = Blueprint('plot_options_blueprint', __name__)

@plot_options_blueprint.route('/plot-options', methods=['GET'])
def plot_options_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM plot_options"
        cursor.execute(query)
        plot_options = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify({"plot_options": plot_options}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@plot_options_blueprint.route('/plot-options/<plot_options_id>', methods=['GET'])
def plot_options_by_id(plot_options_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM plot_options WHERE id =" + str(plot_options_id) + ";"
        cursor.execute(query)
        plot_options = cursor.fetchall()
        if plot_options:
            connection.commit()
            connection.close()
            return jsonify({"plot_options": plot_options}), 200
        else:
            connection.close()
            return jsonify({"error": "Plot option not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500

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