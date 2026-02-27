# Urban Mobility Data Explorer

**NYC Yellow Taxi Trip Analytics Dashboard**

An enterprise-level full-stack application for analyzing NYC taxi trip data from January 2019. Features a normalized MySQL database, RESTful Flask API, and interactive web dashboard with custom data structures and algorithms.

---

## VIDEO LINK

[Watch Here]([Video](https://youtu.be/Fup0RQvUxkk))


## Project Overview

This project analyzes **1.5+ million NYC Yellow Taxi trips** from January 2019 to uncover urban mobility patterns. The system features:

- **Normalized MySQL database** (3NF) with 7 tables
- **Flask REST API** with 10+ endpoints
- **Interactive dashboard** with real-time filtering
- **Custom algorithms** implemented from scratch (merge sort, quickselect, hash map, Z-score anomaly detection)
- **5 derived features** (trip duration, fare per mile, pickup hour, weekend flag, average speed)

---

## Tech Stack

**Database:**
- MySQL 8.0
- 7 tables in Third Normal Form (3NF)
- 9 indexes for query optimization

**Backend:**
- Python 3.8+
- Flask 3.0
- mysql-connector-python 8.2

**Frontend:**
- HTML5 / CSS3 / JavaScript (ES6+)
- Chart.js 4.4
- Responsive design

**Data Processing:**
- Pandas (data cleaning only)
- Custom validation logic

---

## Features

### Database Layer
- Normalized schema (3NF) with proper relationships
- Foreign key constraints for referential integrity
- Strategic indexes for time, location, and fare queries
- Pre-seeded dimension tables (265 taxi zones, boroughs, vendors, rate codes, payment types)
- 5 computed derived features stored as columns

### Backend API
- RESTful endpoints for trips, analytics, and zones
- Dynamic filtering (date range, borough, fare, distance)
- Pagination support
- CORS enabled for frontend integration
- Error handling and logging

### Custom Algorithms (No Built-in Libraries)
- **Merge Sort** - Ranking zones by revenue (O(n log n))
- **Quickselect (Top-K)** - Finding top pickup hours (O(n) average)
- **Custom Hash Map** - Grouping trips without SQL GROUP BY (O(n))
- **Z-Score Anomaly Detection** - Finding outlier trips (O(n))

## System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (HTML/CSS/JS) │
│   Port 8000     │
└────────┬────────┘
         │ HTTP Requests
         ↓
┌─────────────────┐
│   Flask API     │
│   Port 5000     │
│   ├─ Routes     │
│   ├─ Services   │
│   └─ Algorithms │
└────────┬────────┘
         │ SQL Queries
         ↓
┌─────────────────┐
│   MySQL DB      │
│   Port 3306     │
│   ├─ trips      │
│   ├─ taxi_zones │
│   └─ dimensions │
└─────────────────┘
```

**Data Flow:**
1. Raw trip data (1.5M rows) → Cleaning script → Cleaned CSV
2. Cleaned CSV → Insertion script → MySQL database
3. Frontend → API requests → Backend services
4. Backend services → SQL queries + custom algorithms → JSON response
5. Frontend → Renders charts and tables

---

## Installation & Setup

git clone <https://github.com/Jtuyishime6/urban-mobility-project.git>

cd urban-mobility-project.git

### Prerequisites

- **MySQL 8.0+** installed and running
- **Python 3.8+**
- **Git**
- **Web browser** (Chrome, Firefox, Safari)

---

## Database Setup

### Step 1: Download Raw Data

Download the NYC Yellow Taxi trip data file:
- **File:** `yellow_tripdata_2019-01.csv`
- **Source:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Place in:** `data/yellow_tripdata_2019-01.csv`

**Note:** This file is ~200MB and not included in the repo due to size limits.

### Step 2: Create Database Configuration

Create `database/db_config.py`:

```python
DB_CONFIG = {
    "host":     "127.0.0.1",
    "user":     "root",
    "password": "YOUR_MYSQL_PASSWORD",  # Change this
    "database": "urban_mobility"
}
```

**Important:** `db_config.py` is in `.gitignore` for security. Each team member creates it locally with their own MySQL password.

### Step 3: Install Python Dependencies

```bash
pip install mysql-connector-python
```

### Step 4: Create Database Schema

This creates the database, all 7 tables, indexes, and inserts all dimension seed data:

```bash
mysql -u root -p --protocol=TCP --host=127.0.0.1 --port=3306 < database/schema.sql
```

Enter your MySQL password when prompted.

### Step 5: Clean Raw Data

This processes the raw trip file, validates rows, computes derived features, and saves the cleaned output:

```bash
python3 database/clean_data.py
```

**Output:** `data/yellow_cleaned_tripdata.csv`

**Processing time:** ~5-10 minutes for 1.5M rows

### Step 6: Insert Cleaned Data

This inserts all cleaned trip records into the database:

```bash
python3 database/insert_tripdata.py
```

**Processing time:** ~10-15 minutes depending on system

### Step 7: Verify Database

```bash
mysql -u root -p --protocol=TCP --host=127.0.0.1 --port=3306 -e "USE urban_mobility; SHOW TABLES; SELECT COUNT(*) FROM trips;"
```

**Expected output:** 7 tables, 1.3M+ trips inserted

---

## Backend Setup

### Step 1: Navigate to Backend Folder

```bash
cd backend
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- Flask 3.0
- flask-cors 4.0
- mysql-connector-python 8.2

### Step 3: Update Database Password

Edit `services/database.py` and update the password:

```python
connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="YOUR_MYSQL_PASSWORD",  # Change this
    database="urban_mobility",
    port=3306
)
```

### Step 4: Run Flask Server

```bash
python app.py
```

**Expected output:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 5: Test API Health

Open browser and go to: `http://localhost:5000/api/health`

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Urban Mobility Data Explorer API",
  "version": "1.0.0"
}
```

---

## Frontend Setup

### Option 1: Open Directly (Simplest)

Just open `frontend/index.html` in your browser.

**Note:** Some browsers block CORS for local files. If charts don't load, use Option 2.

### Option 2: Use Python HTTP Server

```bash
cd frontend
python -m http.server 8000
```

Then open: `http://localhost:8000`

### Option 3: Use Live Server (VS Code)

1. Install "Live Server" extension in VS Code
2. Right-click `index.html` → "Open with Live Server"

---

## API Documentation

**Base URL:** `http://localhost:5000/api`

### Health Check

**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "Urban Mobility Data Explorer API",
  "version": "1.0.0"
}
```

---

### Trips Endpoints

#### Get Filtered Trips

**GET** `/trips`

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `start_date` | string | Filter by pickup date (YYYY-MM-DD) | `2019-01-15` |
| `end_date` | string | Filter by pickup date (YYYY-MM-DD) | `2019-01-20` |
| `pickup_zone` | string | Filter by pickup borough | `Manhattan` |
| `dropoff_zone` | string | Filter by dropoff borough | `Brooklyn` |
| `min_fare` | float | Minimum fare amount | `10.0` |
| `max_fare` | float | Maximum fare amount | `50.0` |
| `min_distance` | float | Minimum trip distance (miles) | `2.0` |
| `page` | int | Page number (default: 1) | `2` |
| `limit` | int | Items per page (default: 50, max: 500) | `100` |

**Example:**
```
GET /api/trips?start_date=2019-01-10&pickup_zone=Manhattan&min_fare=10&page=1&limit=50
```

**Response:**
```json
{
  "data": [
    {
      "trip_id": 12345,
      "pickup_datetime": "2019-01-10 14:30:00",
      "pickup_zone": "Times Square",
      "dropoff_zone": "Central Park",
      "pickup_borough": "Manhattan",
      "trip_distance": 2.5,
      "fare_amount": 12.50,
      "total_amount": 15.80,
      "trip_duration_minutes": 15.5,
      "avg_speed_mph": 9.67
    }
  ],
  "total": 50000,
  "page": 1,
  "limit": 50
}
```

#### Get Summary Statistics

**GET** `/trips/summary`

**Response:**
```json
{
  "total_trips": 1300000,
  "avg_fare": 13.45,
  "avg_distance": 3.21,
  "avg_speed": 11.8
}
```

---

### Analytics Endpoints

#### Hourly Demand

**GET** `/analytics/hourly-demand`

Returns trip count per hour of day (0-23).

**Response:**
```json
{
  "data": [
    {"pickup_hour": 0, "trip_count": 45000},
    {"pickup_hour": 1, "trip_count": 30000},
    ...
  ]
}
```

#### Revenue by Borough

**GET** `/analytics/revenue-by-zone`

**Response:**
```json
{
  "data": [
    {
      "borough_name": "Manhattan",
      "total_revenue": 15000000.50,
      "trip_count": 800000
    },
    ...
  ]
}
```

#### Average Fare by Distance

**GET** `/analytics/average-fare-per-mile`

**Response:**
```json
{
  "data": [
    {"distance_group": "0-1 mi", "avg_fare": 8.50, "trip_count": 200000},
    {"distance_group": "1-3 mi", "avg_fare": 12.30, "trip_count": 500000},
    ...
  ]
}
```

#### Top Revenue Zones (Custom Merge Sort)

**GET** `/analytics/top-revenue-zones?n=10`

**Query Parameters:**
- `n` - Number of zones (1-50, default: 10)

**Response:**
```json
{
  "algorithm": "merge_sort",
  "sorted_by": "total_revenue (descending)",
  "data": [
    {
      "zone_name": "Upper East Side North",
      "borough_name": "Manhattan",
      "total_revenue": 500000.00,
      "trip_count": 25000
    },
    ...
  ]
}
```

#### Top Pickup Hours (Custom Top-K Selection)

**GET** `/analytics/top-pickup-hours?n=5`

**Query Parameters:**
- `n` - Number of hours (1-24, default: 5)

**Response:**
```json
{
  "algorithm": "top_k_selection (quickselect)",
  "sorted_by": "trip_count (descending)",
  "data": [
    {"pickup_hour": 18, "trip_count": 85000},
    {"pickup_hour": 19, "trip_count": 82000},
    ...
  ]
}
```

#### Anomaly Detection (Custom Z-Score)

**GET** `/analytics/anomalies?field=total_amount&threshold=3.0&limit=10000`

**Query Parameters:**
- `field` - Field to analyze: `total_amount`, `trip_distance`, `trip_duration_minutes`, `fare_per_mile`, `avg_speed_mph`
- `threshold` - Z-score threshold (default: 3.0)
- `limit` - Number of trips to analyze (1-100000, default: 10000)

**Response:**
```json
{
  "algorithm": "z_score_anomaly_detection",
  "field_analyzed": "total_amount",
  "threshold": 3.0,
  "anomalies_found": 45,
  "data": [
    {
      "trip_id": 123456,
      "pickup_zone": "JFK Airport",
      "total_amount": 250.00,
      "z_score": 5.2,
      "mean": 15.50,
      "std_dev": 12.30
    },
    ...
  ]
}
```

---

### Zones Endpoints

#### Get All Boroughs

**GET** `/zones/boroughs`

**Response:**
```json
{
  "data": ["Bronx", "Brooklyn", "EWR", "Manhattan", "Queens", "Staten Island"]
}
```

---

## Custom Algorithms

All algorithms are implemented **manually from scratch** without using built-in Python libraries.

### 1. Merge Sort (Zone Revenue Ranking)

**Purpose:** Sort zones by total revenue in descending order.

**Time Complexity:** O(n log n)  
**Space Complexity:** O(n)

**Implementation:** `algorithms/__init__.py` → `merge_sort()`

**Usage:** `/api/analytics/top-revenue-zones`

---

### 2. Quickselect (Top-K Selection)

**Purpose:** Find top K pickup hours without fully sorting.

**Time Complexity:** O(n) average, O(n²) worst case  
**Space Complexity:** O(1)

**Implementation:** `algorithms/__init__.py` → `top_k_selection()`

**Usage:** `/api/analytics/top-pickup-hours`

---

### 3. Custom Hash Map (Grouping)

**Purpose:** Group trips by zone without SQL GROUP BY.

**Time Complexity:** O(n) average  
**Space Complexity:** O(m) where m = unique groups

**Implementation:** `algorithms/__init__.py` → `CustomHashMap` class

**Usage:** `/api/analytics/grouped-by-zone`

**Features:**
- Chaining for collision resolution
- Custom hash function
- Put, get, contains, keys operations

---

### 4. Z-Score Anomaly Detection

**Purpose:** Identify outlier trips based on statistical deviation.

**Time Complexity:** O(n)  
**Space Complexity:** O(n)

**Implementation:** `algorithms/__init__.py` → `detect_anomalies()`

**Usage:** `/api/analytics/anomalies`

**Algorithm:**
1. Calculate mean and standard deviation manually
2. Compute Z-score for each trip: `z = |value - mean| / std_dev`
3. Flag trips with Z-score > threshold (default: 3.0)

---

## Project Structure

```
urban-mobility-data-explorer/
├── README.md
├── .gitignore
│
├── data/                              # Data files (not in repo)
│   ├── yellow_tripdata_2019-01.csv   # Raw trip data (download separately)
│   ├── yellow_cleaned_tripdata.csv   # Cleaned data (generated)
│   ├── taxi_zone_lookup.csv          # Zone dimension mapping
│   └── taxi_zones.csv                # Zone metadata
│
├── database/                          # Database layer
│   ├── README.md
│   ├── schema.sql                    # Database schema + seed data
│   ├── clean_data.py                 # Data cleaning script
│   ├── insert_tripdata.py            # Data insertion script
│   └── db_config.example.py          # Database config template
│
├── backend/                           # Flask API
│   ├── app.py                        # Main Flask application
│   ├── requirements.txt              # Python dependencies
│   │
│   ├── routes/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── trips.py
│   │   ├── analytics.py
│   │   └── zones.py
│   │
│   ├── services/                     # Business logic
│   │   ├── __init__.py
│   │   ├── database.py               # DB connection helper
│   │   ├── trip_service.py           # Trip queries
│   │   └── analytics_service.py      # Analytics queries
│   │
│   └── algorithms/                   # Custom algorithms
│       └── __init__.py               # Merge sort, quickselect, hash map, Z-score
│
├── frontend/                          # Web dashboard
│   ├── index.html                    # Main HTML page
│   ├── styles.css                    # Stylesheet
│   └── dashboard.js                  # Frontend logic
│
└── docs/                              # Documentation
    ├── er_diagram.png                # ER diagram
    └── team_participation_sheet.pdf  # Team contributions
```

---

## Video Walkthrough

**Link:** [https://youtu.be/Fup0RQvUxkk]

**Contents:**
1. System architecture overview
2. Database schema and normalization
3. Custom algorithms demonstration
4. Backend API endpoints
5. Frontend dashboard features
6. Live filtering and pagination
7. Technical design decisions

---

## Troubleshooting

### Database Connection Failed

**Error:** `Can't connect to MySQL server`

**Solution:**
1. Check MySQL is running: `sudo service mysql status`
2. Verify password in `services/database.py`
3. Try TCP connection: `mysql -u root -p --protocol=TCP --host=127.0.0.1`

### API Returns 500 Error

**Solution:**
1. Check backend logs in terminal
2. Verify database has data: `SELECT COUNT(*) FROM trips;`
3. Check MySQL user has proper permissions

### Frontend Charts Not Loading

**Solution:**
1. Check browser console for errors (F12)
2. Verify backend is running on port 5000
3. Check CORS is enabled in Flask
4. Use HTTP server instead of opening file directly

### Cleaning Script Takes Too Long

**Solution:**
1. Reduce sample size for testing (edit `clean_data.py` line 200)
2. Run on fewer rows first to verify it works
3. Normal processing time: ~10 minutes for full dataset

---

## Database Schema

**Tables:**
- `trips` - Fact table (1.3M+ rows)
- `taxi_zones` - 265 NYC taxi zones
- `boroughs` - 8 boroughs
- `service_zones` - 5 zone types
- `vendors` - 2 taxi vendors
- `rate_codes` - 6 fare rate types
- `payment_types` - 6 payment methods

**Normalization:** Third Normal Form (3NF)

**Indexes:** 9 strategic indexes on timestamps, locations, and derived features

**Relationships:**
```
trips ─┬─> taxi_zones ──> boroughs
       ├─> taxi_zones ──> service_zones
       ├─> vendors
       ├─> rate_codes
       └─> payment_types
```

---

## Key Insights

1. **Peak demand:** 6-7 PM on weekdays (rush hour)
2. **Highest revenue:** Manhattan Upper East Side
3. **Average trip:** 3.2 miles, $13.45 fare, 15 minutes
4. **Fare efficiency:** Longer trips have higher fare-per-mile ratio
5. **Weekend patterns:** Lower volume but longer average distance

---

## License

This project is for educational purposes as part of a university assignment.

---

## Acknowledgments

- **NYC TLC** for providing open taxi trip data
- **Developer** Jean de Dieu Tuyishime