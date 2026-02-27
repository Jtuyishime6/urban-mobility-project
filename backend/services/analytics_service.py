"""
Analytics service for Urban Mobility Data Explorer
Member 3: Backend API Engineer
Connects to MySQL database and provides analytics endpoints
"""

from typing import List, Dict, Any
import mysql.connector
from app.algorithms import (
    rank_zones_by_revenue,
    get_top_pickup_hours,
    group_trips_by_key,
    detect_anomalies
)
from app.database import get_db_connection


def get_hourly_demand() -> List[Dict[str, Any]]:
    """
    Get trip count per hour of day.
    Returns list of {pickup_hour, trip_count}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            pickup_hour,
            COUNT(*) as trip_count
        FROM trips
        WHERE pickup_hour IS NOT NULL
        GROUP BY pickup_hour
        ORDER BY pickup_hour
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return result


def get_revenue_by_zone() -> List[Dict[str, Any]]:
    """
    Get total revenue by borough.
    Returns list of {borough_name, total_revenue}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            b.borough_name,
            SUM(t.total_amount) as total_revenue,
            COUNT(*) as trip_count
        FROM trips t
        JOIN taxi_zones tz ON t.pickup_location_id = tz.location_id
        JOIN boroughs b ON tz.borough_id = b.borough_id
        GROUP BY b.borough_name
        ORDER BY total_revenue DESC
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Convert Decimal to float for JSON serialization
    for row in result:
        if row['total_revenue'] is not None:
            row['total_revenue'] = float(row['total_revenue'])
        else:
            row['total_revenue'] = 0.0
    
    return result


def get_avg_fare_per_distance() -> List[Dict[str, Any]]:
    """
    Get average fare grouped by distance buckets.
    Returns list of {distance_group, avg_fare, trip_count}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            CASE 
                WHEN trip_distance < 1 THEN '0-1 mi'
                WHEN trip_distance < 3 THEN '1-3 mi'
                WHEN trip_distance < 5 THEN '3-5 mi'
                WHEN trip_distance < 10 THEN '5-10 mi'
                ELSE '10+ mi'
            END as distance_group,
            AVG(fare_amount) as avg_fare,
            COUNT(*) as trip_count
        FROM trips
        WHERE trip_distance > 0 AND fare_amount > 0
        GROUP BY distance_group
        ORDER BY 
            CASE distance_group
                WHEN '0-1 mi' THEN 1
                WHEN '1-3 mi' THEN 2
                WHEN '3-5 mi' THEN 3
                WHEN '5-10 mi' THEN 4
                ELSE 5
            END
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Convert Decimal to float
    for row in result:
        if row['avg_fare'] is not None:
            row['avg_fare'] = float(row['avg_fare'])
        else:
            row['avg_fare'] = 0.0
    
    return result


def get_top_revenue_zones(top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Get top revenue zones using custom merge sort algorithm.
    Returns list of {zone_name, borough_name, total_revenue, trip_count}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            tz.zone_name,
            b.borough_name,
            SUM(t.total_amount) as total_revenue,
            COUNT(*) as trip_count
        FROM trips t
        JOIN taxi_zones tz ON t.pickup_location_id = tz.location_id
        JOIN boroughs b ON tz.borough_id = b.borough_id
        GROUP BY tz.zone_name, b.borough_name
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Convert Decimal to float
    for row in result:
        if row['total_revenue'] is not None:
            row['total_revenue'] = float(row['total_revenue'])
        else:
            row['total_revenue'] = 0.0
    
    # Use custom merge sort algorithm
    sorted_zones = rank_zones_by_revenue(result)
    
    return sorted_zones[:top_n]


def get_top_pickup_hours_manual(top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Get top pickup hours using custom top-k selection algorithm.
    Returns list of {pickup_hour, trip_count}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            pickup_hour,
            COUNT(*) as trip_count
        FROM trips
        WHERE pickup_hour IS NOT NULL
        GROUP BY pickup_hour
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Use custom top-k selection algorithm
    top_hours = get_top_pickup_hours(result, top_n)
    
    return top_hours


def get_trips_grouped_by_zone_manual(limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Group trips by zone using custom hash map implementation.
    Returns list of {zone_name, count, sum, avg}
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            tz.zone_name,
            t.total_amount
        FROM trips t
        JOIN taxi_zones tz ON t.pickup_location_id = tz.location_id
        LIMIT %s
    """
    
    cursor.execute(query, (limit,))
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Convert Decimal to float
    for row in result:
        row['total_amount'] = float(row['total_amount'])
    
    # Use custom hash map grouping algorithm
    grouped = group_trips_by_key(result, 'zone_name', 'total_amount', 'sum')
    
    return grouped


def get_anomalous_trips(field: str = 'total_amount', 
                        threshold: float = 3.0, 
                        limit: int = 10000) -> List[Dict[str, Any]]:
    """
    Detect anomalous trips using custom Z-score algorithm.
    Returns list of trips with high Z-scores
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Build query with selected field
    query = f"""
        SELECT 
            trip_id,
            pickup_datetime,
            tz_pickup.zone_name as pickup_zone,
            tz_dropoff.zone_name as dropoff_zone,
            trip_distance,
            fare_amount,
            total_amount,
            trip_duration_minutes,
            fare_per_mile,
            avg_speed_mph
        FROM trips t
        JOIN taxi_zones tz_pickup ON t.pickup_location_id = tz_pickup.location_id
        JOIN taxi_zones tz_dropoff ON t.dropoff_location_id = tz_dropoff.location_id
        WHERE {field} IS NOT NULL
        LIMIT %s
    """
    
    cursor.execute(query, (limit,))
    result = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Convert Decimal to float
    for row in result:
        if 'trip_distance' in row and row['trip_distance']:
            row['trip_distance'] = float(row['trip_distance'])
        if 'fare_amount' in row and row['fare_amount']:
            row['fare_amount'] = float(row['fare_amount'])
        if 'total_amount' in row and row['total_amount']:
            row['total_amount'] = float(row['total_amount'])
        if 'trip_duration_minutes' in row and row['trip_duration_minutes']:
            row['trip_duration_minutes'] = float(row['trip_duration_minutes'])
        if 'fare_per_mile' in row and row['fare_per_mile']:
            row['fare_per_mile'] = float(row['fare_per_mile'])
        if 'avg_speed_mph' in row and row['avg_speed_mph']:
            row['avg_speed_mph'] = float(row['avg_speed_mph'])
    
    # Use custom anomaly detection algorithm
    anomalies = detect_anomalies(result, field, threshold)
    
    return anomalies