CREATE VIEW CityPriceStats AS
SELECT
    c.CityName,
    ROUND(AVG(l.Price),2) AS AvgPrice
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName;

SELECT *
FROM CityPriceStats;