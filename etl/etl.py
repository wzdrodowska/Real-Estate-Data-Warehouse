from datetime import datetime
from pathlib import Path
import sqlite3


# =====================================
# PATHS
# =====================================

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "real_estate.db"
WAREHOUSE_SQL_PATH = BASE_DIR / "sql" / "warehouse.sql"
REPORT_PATH = BASE_DIR / "data_quality_report.txt"


# =====================================
# DATA QUALITY HELPERS
# =====================================

VALID_STATUSES = {"Available", "Sold", "Reserved"}
MIN_YEAR_BUILT = 1900
CURRENT_YEAR = datetime.now().year


def clean_text(value):
    if value is None:
        return None
    return str(value).strip()


def parse_listing_date(value):
    try:
        return datetime.strptime(clean_text(value), "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def is_positive_number(value):
    return value is not None and value > 0


def write_quality_report(stats):
    lines = [
        "DATA QUALITY REPORT",
        "===================",
        f"Source cities checked: {stats['cities_checked']}",
        f"Source properties checked: {stats['properties_checked']}",
        f"Source listings checked: {stats['listings_checked']}",
        "",
        f"DimCity rows loaded: {stats['cities_loaded']}",
        f"DimProperty rows loaded: {stats['properties_loaded']}",
        f"DimDate rows loaded: {stats['dates_loaded']}",
        f"FactSales rows loaded: {stats['facts_loaded']}",
        "",
        f"Rows skipped because of empty city data: {stats['invalid_city_rows']}",
        f"Rows skipped because of invalid property data: {stats['invalid_property_rows']}",
        f"Rows skipped because of invalid price: {stats['invalid_price_rows']}",
        f"Rows skipped because of invalid area: {stats['invalid_area_rows']}",
        f"Rows skipped because of invalid listing date: {stats['invalid_date_rows']}",
        f"Rows skipped because of invalid status: {stats['invalid_status_rows']}",
        f"Rows skipped because of invalid year built: {stats['invalid_year_rows']}",
        f"Rows skipped because of invalid room count: {stats['invalid_room_rows']}",
        f"Rows skipped because of invalid property reference: {stats['invalid_property_reference_rows']}",
        f"Duplicate fact rows skipped: {stats['duplicate_fact_rows']}",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# =====================================
# CONNECT TO DATABASE
# =====================================

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

stats = {
    "cities_checked": 0,
    "properties_checked": 0,
    "listings_checked": 0,
    "cities_loaded": 0,
    "properties_loaded": 0,
    "dates_loaded": 0,
    "facts_loaded": 0,
    "invalid_city_rows": 0,
    "invalid_property_rows": 0,
    "invalid_price_rows": 0,
    "invalid_area_rows": 0,
    "invalid_date_rows": 0,
    "invalid_status_rows": 0,
    "invalid_year_rows": 0,
    "invalid_room_rows": 0,
    "invalid_property_reference_rows": 0,
    "duplicate_fact_rows": 0,
}


# =====================================
# REBUILD WAREHOUSE TABLES
# =====================================

cursor.executescript("""
DROP TABLE IF EXISTS FactSales;
DROP TABLE IF EXISTS DimDate;
DROP TABLE IF EXISTS DimProperty;
DROP TABLE IF EXISTS DimCity;
""")

warehouse_sql = WAREHOUSE_SQL_PATH.read_text(encoding="utf-8")
cursor.executescript(warehouse_sql)


# =====================================
# LOAD AND CLEAN DIMCITY
# =====================================

cursor.execute("""
SELECT
    CityID,
    CityName,
    Voivodeship
FROM Cities
""")

valid_city_ids = set()

for city_id, city_name, voivodeship in cursor.fetchall():
    stats["cities_checked"] += 1

    city_name = clean_text(city_name)
    voivodeship = clean_text(voivodeship)

    if not city_name or not voivodeship:
        stats["invalid_city_rows"] += 1
        continue

    cursor.execute("""
    INSERT INTO DimCity
    (CityID, CityName, Voivodeship)
    VALUES (?, ?, ?)
    """, (
        city_id,
        city_name,
        voivodeship,
    ))

    valid_city_ids.add(city_id)
    stats["cities_loaded"] += 1


# =====================================
# LOAD AND CLEAN DIMPROPERTY
# =====================================

cursor.execute("""
SELECT
    PropertyID,
    CityID,
    AreaM2,
    Rooms,
    YearBuilt
FROM Properties
""")

valid_property_ids = set()
valid_property_area = {}

for property_id, city_id, area, rooms, year_built in cursor.fetchall():
    stats["properties_checked"] += 1

    is_valid_property = True

    if city_id not in valid_city_ids:
        is_valid_property = False

    if not is_positive_number(area):
        stats["invalid_area_rows"] += 1
        is_valid_property = False

    if rooms is None or rooms <= 0:
        stats["invalid_room_rows"] += 1
        is_valid_property = False

    if year_built is None or year_built < MIN_YEAR_BUILT or year_built > CURRENT_YEAR:
        stats["invalid_year_rows"] += 1
        is_valid_property = False

    if not is_valid_property:
        stats["invalid_property_rows"] += 1
        continue

    cursor.execute("""
    INSERT INTO DimProperty
    (PropertyID, AreaM2, Rooms, YearBuilt)
    VALUES (?, ?, ?, ?)
    """, (
        property_id,
        area,
        rooms,
        year_built,
    ))

    valid_property_ids.add(property_id)
    valid_property_area[property_id] = area
    stats["properties_loaded"] += 1


# =====================================
# LOAD AND CLEAN FACTSALES + DIMDATE
# =====================================

cursor.execute("""
SELECT
    l.ListingID,
    l.PropertyID,
    p.CityID,
    l.Price,
    l.ListingDate,
    l.Status
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
""")

date_ids = {}
seen_facts = set()
next_date_id = 1

for listing_id, property_id, city_id, sale_price, listing_date, status in cursor.fetchall():
    stats["listings_checked"] += 1

    status = clean_text(status)
    parsed_date = parse_listing_date(listing_date)

    if property_id not in valid_property_ids or city_id not in valid_city_ids:
        stats["invalid_property_reference_rows"] += 1
        continue

    if not is_positive_number(sale_price):
        stats["invalid_price_rows"] += 1
        continue

    area = valid_property_area[property_id]
    if not is_positive_number(area):
        stats["invalid_area_rows"] += 1
        continue

    if parsed_date is None:
        stats["invalid_date_rows"] += 1
        continue

    if status not in VALID_STATUSES:
        stats["invalid_status_rows"] += 1
        continue

    fact_key = (property_id, city_id, sale_price, listing_date)
    if fact_key in seen_facts:
        stats["duplicate_fact_rows"] += 1
        continue
    seen_facts.add(fact_key)

    full_date = parsed_date.strftime("%Y-%m-%d")

    if full_date not in date_ids:
        date_ids[full_date] = next_date_id

        cursor.execute("""
        INSERT INTO DimDate
        (DateID, FullDate, Year, Month, Quarter)
        VALUES (?, ?, ?, ?, ?)
        """, (
            next_date_id,
            full_date,
            parsed_date.year,
            parsed_date.month,
            (parsed_date.month - 1) // 3 + 1,
        ))

        stats["dates_loaded"] += 1
        next_date_id += 1

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
        date_ids[full_date],
        property_id,
        city_id,
        sale_price,
        price_per_m2,
    ))

    stats["facts_loaded"] += 1


# =====================================
# SAVE
# =====================================

conn.commit()
conn.close()

write_quality_report(stats)

print("ETL completed successfully!")
print(f"Data quality report saved to: {REPORT_PATH}")
