from flask import Blueprint, jsonify, request, g
from flask_cors import cross_origin
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

shed_blueprint = Blueprint('shed_blueprint', __name__)

@shed_blueprint.route('/shed', methods=['GET'])
@cross_origin()
@token_required
def shed_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM shed WHERE gardener =" + str(g.user["id"]) + ";"
        cursor.execute(query)
        shed = cursor.fetchall()
        connection.commit()
        connection.close()
        return jsonify({"shed": shed}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@shed_blueprint.route('/shed', methods=['POST'])
@cross_origin()
@token_required
def create_shed():
    try:
        new_shed = request.json
        new_shed["gardener"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
                        INSERT INTO shed (gardener, type)
                        VALUES (%s, %s)
                        RETURNING *
                        """,
                        (new_shed['gardener'], new_shed['type'])
        )
        created_shed = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"shed": created_shed}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@shed_blueprint.route('/shed/<shed_id>', methods=['PUT'])
@cross_origin()
@token_required
def update_shed(shed_id):
    try:
        updated_shed_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM shed WHERE id = %s", (shed_id,))
        shed_to_update = cursor.fetchone()
        if shed_to_update is None:
            return jsonify({"error": "Plot not found"}), 404
        connection.commit()
        if shed_to_update["gardener"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("UPDATE shed SET type = %s WHERE id = %s RETURNING *",
                        (updated_shed_data["type"], shed_id))
        updated_shed = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"user_plot": updated_shed}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@shed_blueprint.route('/shed/<shed_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_shed(shed_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM shed WHERE shed.id = %s", (shed_id,))
        shed_to_update = cursor.fetchone()
        if shed_to_update is None:
            return jsonify({"error": "shed not found"}), 404
        connection.commit()
        if shed_to_update["author"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("DELETE FROM shed WHERE shed.id = %s", (shed_id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "shed deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500