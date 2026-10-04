import sqlite3


DB_NAME = "automotive.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Vehicle master table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY,
            model TEXT NOT NULL,
            body_type TEXT NOT NULL,
            transmission TEXT NOT NULL,
            price_lakh REAL NOT NULL
        )
    """)

    # Dealer inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY,
            vehicle_id INTEGER NOT NULL,
            city TEXT NOT NULL,
            units INTEGER NOT NULL,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        )
    """)

    # Insert sample vehicles only if table is empty
    cursor.execute("SELECT COUNT(*) FROM vehicles")
    vehicle_count = cursor.fetchone()[0]

    if vehicle_count == 0:
        vehicles = [
            (1, "Hyundai Creta", "SUV", "automatic", 18.5),
            (2, "Kia Seltos", "SUV", "automatic", 19.2),
            (3, "Toyota Urban Cruiser Hyryder", "SUV", "automatic", 20.5),
            (4, "Tata Nexon", "SUV", "automatic", 14.5),
            (5, "Hyundai Venue", "SUV", "automatic", 15.8),
            (6, "Honda City", "Sedan", "automatic", 17.2),
        ]

        cursor.executemany("""
            INSERT INTO vehicles
            (vehicle_id, model, body_type, transmission, price_lakh)
            VALUES (?, ?, ?, ?, ?)
        """, vehicles)

    # Insert sample inventory only if table is empty
    cursor.execute("SELECT COUNT(*) FROM inventory")
    inventory_count = cursor.fetchone()[0]

    if inventory_count == 0:
        inventory = [
            (1, 1, "Ranchi", 3),
            (2, 2, "Ranchi", 2),
            (3, 3, "Ranchi", 1),
            (4, 4, "Ranchi", 4),
            (5, 5, "Ranchi", 2),
            (6, 6, "Ranchi", 3),

            (7, 1, "Delhi", 8),
            (8, 2, "Delhi", 5),
            (9, 4, "Delhi", 7),
            (10, 5, "Delhi", 6),
        ]

        cursor.executemany("""
            INSERT INTO inventory
            (inventory_id, vehicle_id, city, units)
            VALUES (?, ?, ?, ?)
        """, inventory)

    conn.commit()
    conn.close()


def check_inventory(
    city: str,
    max_price_lakh: float,
    transmission: str,
    body_type: str
) -> str:

    try:
        max_price_lakh = float(max_price_lakh)
    except (TypeError, ValueError):
        return "Invalid max_price_lakh. It must be a number in lakh, for example 20."
    conn = get_connection()
    cursor = conn.cursor()
    if max_price_lakh <= 0:
        return "Invalid price. max_price_lakh must be greater than 0."

    if max_price_lakh > 100:
        return (
            "Invalid price. max_price_lakh must be expressed in lakh, "
            "for example 20 for ₹20 lakh."
        )
    query = """
        SELECT
            v.model,
            v.price_lakh,
            v.transmission,
            v.body_type,
            i.city,
            i.units
        FROM vehicles v
        JOIN inventory i
            ON v.vehicle_id = i.vehicle_id
        WHERE LOWER(i.city) = LOWER(?)
          AND v.price_lakh <= ?
          AND LOWER(v.transmission) = LOWER(?)
          AND LOWER(v.body_type) = LOWER(?)
          AND i.units > 0
        ORDER BY v.price_lakh ASC
    """

    cursor.execute(
        query,
        (city, max_price_lakh, transmission, body_type)
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No matching vehicles found."

    import json
    results = []

    for row in rows:
        model, price, transmission, body_type, city, units = row

        results.append({
            "model": model,
            "price_lakh": price,
            "transmission": transmission,
            "body_type": body_type,
            "city": city,
            "units_available": units
        })

    return json.dumps(results)

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
