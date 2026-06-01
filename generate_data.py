import sqlite3
import random

conn = sqlite3.connect("database/real_estate.db")
cursor = conn.cursor()

# ------------------
# Cities
# ------------------

cities = [
    ("Gdańsk", "Pomorskie"),
    ("Gdynia", "Pomorskie"),
    ("Sopot", "Pomorskie"),
    ("Warszawa", "Mazowieckie"),
    ("Kraków", "Małopolskie"),
    ("Białystok", "Podlaskie")
]

cursor.executemany("""
INSERT INTO Cities (CityName, Voivodeship)
VALUES (?, ?)
""", cities)

# ------------------
# Agencies
# ------------------

agencies = [
    ("Home Expert", "500123456"),
    ("Premium Estates", "501234567"),
    ("City House", "502345678")
]

cursor.executemany("""
INSERT INTO Agencies (AgencyName, Phone)
VALUES (?, ?)
""", agencies)

# ------------------
# Properties
# ------------------

for i in range(100):

    city_id = random.randint(1, 6)
    agency_id = random.randint(1, 3)

    area = random.randint(30, 120)
    rooms = random.randint(1, 5)
    year = random.randint(1970, 2025)

    address = f"Street {i+1}"

    cursor.execute("""
    INSERT INTO Properties
    (CityID, AgencyID, Address, AreaM2, Rooms, YearBuilt)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        city_id,
        agency_id,
        address,
        area,
        rooms,
        year
    ))

# ------------------
# Listings
# ------------------

statuses = [
    "Available",
    "Sold",
    "Reserved"
]

for property_id in range(1, 101):

    price = random.randint(250000, 1200000)

    cursor.execute("""
    INSERT INTO Listings
    (PropertyID, ListingDate, Price, Status)
    VALUES (?, DATE('now'), ?, ?)
    """, (
        property_id,
        price,
        random.choice(statuses)
    ))

conn.commit()
conn.close()

print("Data generated successfully!")