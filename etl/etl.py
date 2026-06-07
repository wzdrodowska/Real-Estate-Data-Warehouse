import sqlite3
from datetime import datetime

# =====================================
# CONNECT TO DATABASE
# =====================================

conn = sqlite3.connect("database/real_estate.db")
cursor = conn.cursor()

# =====================================
# LOAD WAREHOUSE TABLES
# =====================================

with open("sql/warehouse.sql", "r", encoding="utf-8") as f:
    warehouse_sql = f.read()

cursor.executescript(warehouse_sql)

# =====================================
# LOAD DIMCITY
# =====================================

cursor.execute("""
INSERT OR IGNORE INTO DimCity
SELECT
    CityID,
    CityName,
    Voivodeship
FROM Cities
""")

# =====================================
# LOAD DIMPROPERTY
# =====================================

cursor.execute("""
INSERT OR IGNORE INTO DimProperty
SELECT
    PropertyID,
    AreaM2,
    Rooms,
    YearBuilt
FROM Properties
""")

# =====================================
# LOAD DIMDATE
# =====================================

cursor.execute("""
SELECT DISTINCT ListingDate
FROM Listings
""")

dates = cursor.fetchall()

date_id = 1

for row in dates:

    full_date = row[0]

    dt = datetime.strptime(full_date, "%Y-%m-%d")

    year = dt.year
    month = dt.month
    quarter = (month - 1) // 3 + 1

    cursor.execute("""
    INSERT OR IGNORE INTO DimDate
    (DateID, FullDate, Year, Month, Quarter)
    VALUES (?, ?, ?, ?, ?)
    """, (
        date_id,
        full_date,
        year,
        month,
        quarter
    ))

    date_id += 1

# =====================================
# LOAD FACTSALES
# =====================================

cursor.execute("""
SELECT
    l.PropertyID,
    p.CityID,
    l.Price,
    p.AreaM2,
    l.ListingDate
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
""")

sales = cursor.fetchall()

for property_id, city_id, sale_price, area, listing_date in sales:

    cursor.execute("""
    SELECT DateID
    FROM DimDate
    WHERE FullDate = ?
    """, (listing_date,))

    date_id = cursor.fetchone()[0]

    price_per_m2 = round(sale_price / area, 2)

    cursor.execute("""
    INSERT INTO FactSales
    (
        DateID,
        PropertyID,
        CityID,
        SalePrice,
        PricePerM2
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        date_id,
        property_id,
        city_id,
        sale_price,
        price_per_m2
    ))

# =====================================
# SAVE
# =====================================

conn.commit()
conn.close()

print("ETL completed successfully!")