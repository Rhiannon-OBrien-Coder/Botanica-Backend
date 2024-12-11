from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

user_plots_blueprint = Blueprint('user_plots_blueprint', __name__)

@user_plots_blueprint.route('/user-plots', methods=['GET'])
@token_required
def plot_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM user_plots WHERE gardener =" + str(g.user["id"]) + ";"
        cursor.execute(query)
        user_plots = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify({"user_plots": user_plots}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@user_plots_blueprint.route('/user-plots', methods=['POST'])
@token_required
def create_plot():
    try:
        new_user_plot = request.json
        new_user_plot["gardener"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO user_plots (gardener, name, type)
                        VALUES (%s, %s, %s)
                        RETURNING *
                        """,
                        (new_user_plot['gardener'], new_user_plot['name'], new_user_plot['type'])
        )
        create_user_plot = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"user_plot": create_user_plot}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
