from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

plot_options_blueprint = Blueprint('plot_options_blueprint', __name__)

@plot_options_blueprint.route('/plot-options', methods=['GET'])
def plot_options_index():
    return jsonify({"message": "plot options index lives here"})