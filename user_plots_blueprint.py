from flask import Blueprint, jsonify, request, g
from flask_cors import cross_origin
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

user_plots_blueprint = Blueprint('user_plots_blueprint', __name__)

@user_plots_blueprint.route('/user-plots', methods=['GET'])
@cross_origin()
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
    
@user_plots_blueprint.route('/user-plots/<user_plots_id>', methods=['GET'])
@cross_origin()
@token_required
def plot_by_id(user_plots_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM user_plots WHERE id = " + str(user_plots_id) + " AND gardener = " + str(g.user["id"]) + ";"
        cursor.execute(query)
        user_plots = cursor.fetchall()
        if user_plots:
            connection.commit()
            connection.close()
            return jsonify({"user_plots": user_plots}), 200
        else:
            connection.close()
            return jsonify({"error": "Plot not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@user_plots_blueprint.route('/user-plots', methods=['POST'])
@cross_origin()
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

@user_plots_blueprint.route('/user-plots/<user_plots_id>', methods=['PUT'])
@cross_origin()
@token_required
def update_plot(user_plots_id):
    try:
        updated_user_plot_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM user_plots WHERE id = %s", (user_plots_id,))
        user_plot_to_update = cursor.fetchone()
        if user_plot_to_update is None:
            return jsonify({"error": "Plot not found"}), 404
        connection.commit()
        if user_plot_to_update["gardener"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("UPDATE user_plots SET name = %s, type = %s WHERE id = %s RETURNING *",
                        (updated_user_plot_data["name"], updated_user_plot_data["type"], user_plots_id))
        updated_user_plot = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"user_plot": updated_user_plot}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@user_plots_blueprint.route('/user-plots/<user_plot_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_user_plot(user_plot_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM user_plots WHERE id = %s", (user_plot_id,))
        user_plot_to_update = cursor.fetchone()
        if user_plot_to_update is None:
            return jsonify({"error": "user_plot not found"}), 404
        connection.commit()
        if user_plot_to_update["gardener"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("DELETE FROM user_plots WHERE id = %s", (user_plot_id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "user_plot deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500