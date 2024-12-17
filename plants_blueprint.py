from flask import Blueprint, jsonify, request, g
from flask_cors import cross_origin
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required
import logging

logging.basicConfig(level=logging.INFO)

plants_blueprint = Blueprint('plants_blueprint', __name__)

@plants_blueprint.route('/plants', methods=['GET'])
@cross_origin()
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

@plants_blueprint.route('/plants/<plants_id>', methods=['GET'])
@cross_origin()
@token_required
def plant_by_id(plants_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT * FROM plants WHERE id = " + str(plants_id) + " AND gardener = " + str(g.user["id"]) + ";"
        cursor.execute(query)
        plants = cursor.fetchall()
        if plants:
            connection.commit()
            connection.close()
            return jsonify({"plants": plants}), 200
        else:
            connection.close()
            return jsonify({"error": "Plant not found"}), 404
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@plants_blueprint.route('/plants', methods=['POST'])
@cross_origin()
@token_required
def create_plants():
    try:
        logging.info(new_plants)
        new_plants = request.json
        new_plants["gardener"] = g.user["id"]
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT id FROM shed WHERE gardener = " + str(g.user["id"]) + ";"
        cursor.execute(query)
        new_plants["shed"] = cursor.fetchone()
        logging.info(new_plants)
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
    
@plants_blueprint.route('/plants/<plants_id>', methods=['PUT'])
@cross_origin()
@token_required
def update_plant(plants_id):
    try:
        updated_plant_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM plants WHERE id = %s", (plants_id,))
        plant_to_update = cursor.fetchone()
        if plant_to_update is None:
            return jsonify({"error": "Plot not found"}), 404
        connection.commit()
        if plant_to_update["gardener"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("UPDATE plants SET name = %s, type = %s, shed = %s, plot = %s, planted = %s, position = %s, status = %s, age = %s, sow_day = %s, watered = %s WHERE id = %s RETURNING *",
                        (updated_plant_data["name"], updated_plant_data["type"], updated_plant_data["shed"], updated_plant_data["plot"], updated_plant_data["planted"], updated_plant_data["position"], updated_plant_data["status"], updated_plant_data["age"], updated_plant_data["sow_day"], updated_plant_data["watered"], plants_id))
        updated_plant = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"updated_plant": updated_plant}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
    
@plants_blueprint.route('/plants/<plant_id>', methods=['DELETE'])
@cross_origin()
@token_required
def delete_plant(plant_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM plants WHERE plants.id = %s", (plant_id,))
        plant_to_update = cursor.fetchone()
        if plant_to_update is None:
            return jsonify({"error": "plant not found"}), 404
        connection.commit()
        if plant_to_update["author"] is not g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401
        cursor.execute("DELETE FROM plants WHERE plants.id = %s", (plant_id,))
        connection.commit()
        connection.close()
        return jsonify({"message": "plant deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
