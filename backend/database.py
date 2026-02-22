"""
Database connection helper for Urban Mobility Data Explorer
Member 3: Backend API Engineer
"""

import mysql.connector
from typing import Any


def get_db_connection() -> Any:
    """
    Create and return a MySQL database connection.
    Uses connection config from environment or default values.
    """
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="admin",
        password="12345",  
        database="urban_mobility",
        port=3306
    )
    
    return connection