"""
Zones API routes
"""

from flask import Blueprint, jsonify, current_app
from services.trip_service import get_boroughs

zones_bp = Blueprint("zones", __name__)


@zones_bp.route("/zones/boroughs", methods=["GET"])
def list_boroughs():
    """
    Get list of all boroughs for filter dropdown.
    Returns: ["Bronx", "Brooklyn", "Manhattan", ...]
    """
    try:
        boroughs = get_boroughs()
        return jsonify({"data": boroughs}), 200
    except Exception as e:
        current_app.logger.error(f"[/zones/boroughs] {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500