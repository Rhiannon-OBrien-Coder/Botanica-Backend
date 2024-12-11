from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

shed_blueprint = Blueprint('shed_blueprint', __name__)

@shed_blueprint.route('/shed', methods=['GET'])
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