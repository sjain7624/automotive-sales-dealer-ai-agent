import sqlite3
from datetime import datetime


DB_NAME = "automotive.db"


def schedule_call(vehicle_model, city):
    """
    Mock scheduling tool.
    Creates a call appointment in the local SQLite database.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create appointments table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_model TEXT NOT NULL,
            city TEXT NOT NULL,
            appointment_type TEXT NOT NULL,
            status TEXT NOT NULL,
            scheduled_at TEXT NOT NULL
        )
    """)

    scheduled_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO appointments
        (
            vehicle_model,
            city,
            appointment_type,
            status,
            scheduled_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        vehicle_model,
        city,
        "Sales Call",
        "Scheduled",
        scheduled_at
    ))

    appointment_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "status": "Scheduled",
        "appointment_id": f"CALL-{appointment_id:04d}",
        "vehicle_model": vehicle_model,
        "city": city,
        "scheduled_at": scheduled_at
    }