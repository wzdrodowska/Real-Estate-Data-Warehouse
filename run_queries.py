import sqlite3

conn = sqlite3.connect("database/real_estate.db")
cursor = conn.cursor()

query = """
SELECT
    c.CityName,
    ROUND(AVG(l.Price),2) AS AvgPrice
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName
ORDER BY AvgPrice DESC;
"""

cursor.execute(query)

results = cursor.fetchall()

for row in results:
    print(row)

conn.close()