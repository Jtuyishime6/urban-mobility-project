"""
Trip service for Urban Mobility Data Explorer
Member 3: Backend API Engineer
Handles filtered trip queries
"""

from typing import Dict, Any, Optional
import mysql.connector
from database import get_db_connection


def get_filtered_trips(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pickup_zone: Optional[str] = None,
    dropoff_zone: Optional[str] = None,
    min_fare: Optional[float] = None,
    max_fare: Optional[float] = None,
    min_distance: Optional[float] = None,
    page: int = 1,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get filtered trips with pagination.
    Returns {data: [...], total: int, page: int, limit: int}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Build WHERE clause dynamically
    where_conditions = []
    params = []
    
    if start_date:
        where_conditions.append("DATE(t.pickup_datetime) >= %s")
        params.append(start_date)
    
    if end_date:
        where_conditions.append("DATE(t.pickup_datetime) <= %s")
        params.append(end_date)
    
    if pickup_zone:
        where_conditions.append("b_pickup.borough_name = %s")
        params.append(pickup_zone)
    
    if dropoff_zone:
        where_conditions.append("b_dropoff.borough_name = %s")
        params.append(dropoff_zone)
    
    if min_fare is not None:
        where_conditions.append("t.fare_amount >= %s")
        params.append(min_fare)
    
    if max_fare is not None:
        where_conditions.append("t.fare_amount <= %s")
        params.append(max_fare)
    
    if min_distance is not None:
        where_conditions.append("t.trip_distance >= %s")
        params.append(min_distance)
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # Count total matching rows
    count_query = f"""
        SELECT COUNT(*) as total
        FROM trips t
        JOIN taxi_zones tz_pickup ON t.pickup_location_id = tz_pickup.location_id
        JOIN boroughs b_pickup ON tz_pickup.borough_id = b_pickup.borough_id
        JOIN taxi_zones tz_dropoff ON t.dropoff_location_id = tz_dropoff.location_id
        JOIN boroughs b_dropoff ON tz_dropoff.borough_id = b_dropoff.borough_id
        WHERE {where_clause}
    """
    
    cursor.execute(count_query, params)
    total = cursor.fetchone()['total']
    
    # Get paginated data
    offset = (page - 1) * limit
    
    data_query = f"""
        SELECT 
            t.trip_id,
            t.pickup_datetime,
            t.dropoff_datetime,
            tz_pickup.zone_name as pickup_zone,
            tz_dropoff.zone_name as dropoff_zone,
            b_pickup.borough_name as pickup_borough,
            b_dropoff.borough_name as dropoff_borough,
            t.trip_distance,
            t.fare_amount,
            t.total_amount,
            t.trip_duration_minutes,
            t.avg_speed_mph,
            t.passenger_count
        FROM trips t
        JOIN taxi_zones tz_pickup ON t.pickup_location_id = tz_pickup.location_id
        JOIN boroughs b_pickup ON tz_pickup.borough_id = b_pickup.borough_id
        JOIN taxi_zones tz_dropoff ON t.dropoff_location_id = tz_dropoff.location_id
        JOIN boroughs b_dropoff ON tz_dropoff.borough_id = b_dropoff.borough_id
        WHERE {where_clause}
        ORDER BY t.pickup_datetime DESC
        LIMIT %s OFFSET %s
    """
    
    cursor.execute(data_query, params + [limit, offset])
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Convert Decimal to float for JSON serialization
    for row in data:
        if 'trip_distance' in row and row['trip_distance']:
            row['trip_distance'] = float(row['trip_distance'])
        if 'fare_amount' in row and row['fare_amount']:
            row['fare_amount'] = float(row['fare_amount'])
        if 'total_amount' in row and row['total_amount']:
            row['total_amount'] = float(row['total_amount'])
        if 'trip_duration_minutes' in row and row['trip_duration_minutes']:
            row['trip_duration_minutes'] = float(row['trip_duration_minutes'])
        if 'avg_speed_mph' in row and row['avg_speed_mph']:
            row['avg_speed_mph'] = float(row['avg_speed_mph'])
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit
    }


def get_summary_stats() -> Dict[str, Any]:
    """
    Get summary statistics for filtered trips.
    Returns {total_trips, avg_fare, avg_distance, avg_speed}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            COUNT(*) as total_trips,
            AVG(fare_amount) as avg_fare,
            AVG(trip_distance) as avg_distance,
            AVG(avg_speed_mph) as avg_speed
        FROM trips
        WHERE fare_amount > 0 AND trip_distance > 0
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    # Convert Decimal to float
    return {
        "total_trips": result['total_trips'],
        "avg_fare": float(result['avg_fare']) if result['avg_fare'] else 0,
        "avg_distance": float(result['avg_distance']) if result['avg_distance'] else 0,
        "avg_speed": float(result['avg_speed']) if result['avg_speed'] else 0
    }


def get_boroughs() -> list:
    """
    Get list of all boroughs for filter dropdown.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT DISTINCT borough_name
        FROM boroughs
        ORDER BY borough_name
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return [row['borough_name'] for row in result]