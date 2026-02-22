"""
Trips API routes
"""

from flask import Blueprint, request, jsonify, current_app
from services.trip_service import get_filtered_trips, get_summary_stats

trips_bp = Blueprint("trips", __name__)


def _parse_float(value: str | None, name: str) -> float | None:
    """Parse float parameter with validation"""
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Parameter '{name}' must be a number. Got: '{value}'")


def _parse_int(value: str | None, name: str, default: int) -> int:
    """Parse int parameter with validation"""
    if value is None:
        return default
    try:
        result = int(value)
        if result < 1:
            raise ValueError()
        return result
    except ValueError:
        raise ValueError(f"Parameter '{name}' must be a positive integer. Got: '{value}'")


@trips_bp.route("/trips", methods=["GET"])
def list_trips():
    """
    Get filtered trips with pagination.
    
    Query parameters:
        - start_date: Filter by pickup date (YYYY-MM-DD)
        - end_date: Filter by pickup date (YYYY-MM-DD)
        - pickup_zone: Filter by pickup borough
        - dropoff_zone: Filter by dropoff borough
        - min_fare: Minimum fare amount
        - max_fare: Maximum fare amount
        - min_distance: Minimum trip distance
        - page: Page number (default: 1)
        - limit: Items per page (default: 50, max: 500)
    """
    try:
        start_date   = request.args.get("start_date")
        end_date     = request.args.get("end_date")
        pickup_zone  = request.args.get("pickup_zone")
        dropoff_zone = request.args.get("dropoff_zone")
        min_fare     = _parse_float(request.args.get("min_fare"),     "min_fare")
        max_fare     = _parse_float(request.args.get("max_fare"),     "max_fare")
        min_distance = _parse_float(request.args.get("min_distance"), "min_distance")

        default_limit = current_app.config["DEFAULT_PAGE_SIZE"]
        max_limit     = current_app.config["MAX_PAGE_SIZE"]
        
        page  = _parse_int(request.args.get("page"),  "page",  default=1)
        limit = _parse_int(request.args.get("limit"), "limit", default=default_limit)
        limit = min(limit, max_limit)

        if min_fare is not None and max_fare is not None and min_fare > max_fare:
            return jsonify({"error": "min_fare cannot be greater than max_fare"}), 400

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        result = get_filtered_trips(
            start_date   = start_date,
            end_date     = end_date,
            pickup_zone  = pickup_zone,
            dropoff_zone = dropoff_zone,
            min_fare     = min_fare,
            max_fare     = max_fare,
            min_distance = min_distance,
            page         = page,
            limit        = limit,
        )
        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"[/api/trips] {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500


@trips_bp.route("/trips/summary", methods=["GET"])
def trips_summary():
    """
    Get summary statistics for all trips.
    Returns: {total_trips, avg_fare, avg_distance, avg_speed}
    """
    try:
        stats = get_summary_stats()
        return jsonify(stats), 200
    except Exception as e:
        current_app.logger.error(f"[/api/trips/summary] {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500