"""
database.py
Handles all MySQL operations: creating tables, saving students,
saving face encodings, and recording/reading attendance.
"""

import pickle
import datetime
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_connection():
    """Open and return a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """
    Create the database (if missing) and the required tables.
    Safe to run every time the app starts.
    """
    # First connect without specifying a database, to create it if needed
    temp_config = {k: v for k, v in DB_CONFIG.items() if k != "database"}
    conn = mysql.connector.connect(**temp_config)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.commit()
    cursor.close()
    conn.close()

    # Now connect to the actual database and create tables
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            roll_no VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            face_encoding LONGBLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            status ENUM('Present') DEFAULT 'Present',
            FOREIGN KEY (student_id) REFERENCES students(id),
            UNIQUE KEY unique_daily_attendance (student_id, date)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def add_student(roll_no, name, encoding):
    """
    Save a new student with their face encoding.
    `encoding` is a numpy array; we pickle it to store as bytes (BLOB).
    Returns True on success, False if roll_no already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        encoding_bytes = pickle.dumps(encoding)
        cursor.execute(
            "INSERT INTO students (roll_no, name, face_encoding) VALUES (%s, %s, %s)",
            (roll_no, name, encoding_bytes)
        )
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    finally:
        cursor.close()
        conn.close()


def get_all_students():
    """
    Return a list of tuples: (student_id, roll_no, name, encoding_as_numpy_array)
    Used to load known faces at the start of an attendance session.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, roll_no, name, face_encoding FROM students")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    students = []
    for student_id, roll_no, name, encoding_bytes in rows:
        encoding = pickle.loads(encoding_bytes)
        students.append((student_id, roll_no, name, encoding))
    return students


def mark_attendance(student_id):
    """
    Mark a student present for today's date.
    Does nothing if already marked today (thanks to the UNIQUE key).
    Returns True if a new record was inserted, False if already marked.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.date.today()
    now = datetime.datetime.now().time().strftime("%H:%M:%S")
    try:
        cursor.execute(
            "INSERT INTO attendance (student_id, date, time) VALUES (%s, %s, %s)",
            (student_id, today, now)
        )
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        # Already marked present today
        return False
    finally:
        cursor.close()
        conn.close()


def get_attendance_by_date(date):
    """
    Return attendance records for a given date (as a date object or 'YYYY-MM-DD' string).
    Returns list of tuples: (roll_no, name, time, status)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.roll_no, s.name, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = %s
        ORDER BY a.time
    """, (date,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_all_attendance():
    """Return every attendance record ever recorded, most recent first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.roll_no, s.name, a.date, a.time, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, a.time DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
