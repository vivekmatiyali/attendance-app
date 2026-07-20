"""
Database configuration.
Update these values with your own MySQL credentials before running the app.
"""

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",   # <-- change this
    "database": "attendance_db"
}

# Face recognition matching tolerance.
# Lower = stricter match (fewer false positives, but might miss real matches).
# Typical range: 0.4 - 0.6
FACE_MATCH_TOLERANCE = 0.5

# Camera index (0 = default built-in/USB webcam)
CAMERA_INDEX = 0

# How many photos to capture per student when registering
PHOTOS_PER_STUDENT = 5
