import sqlite3

conn = sqlite3.connect("database/real_estate.db")
cursor = conn.cursor()

query = """
SELECT
    c.CityName,
    ROUND(AVG(f.PricePerM2), 2) AS AvgPricePerM2
FROM FactSales f
JOIN DimCity c
ON f.CityID = c.CityID
GROUP BY c.CityName
ORDER BY AvgPricePerM2 DESC;
"""

cursor.execute(query)

results = cursor.fetchall()

print("\nAverage price per m² by city:\n")

for row in results:
    print(row)

conn.close()