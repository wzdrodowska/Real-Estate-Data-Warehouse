SELECT
    p.PropertyID,
    c.CityName,
    p.AreaM2,
    p.Rooms
FROM Properties p
JOIN Cities c
ON p.CityID = c.CityID;

SELECT
    c.CityName,
    ROUND(AVG(l.Price), 2) AS AvgPrice
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName;

SELECT
    c.CityName,
    ROUND(AVG(l.Price), 2) AS AvgPrice
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName
ORDER BY AvgPrice DESC;

SELECT
    c.CityName,
    COUNT(*) AS PropertyCount
FROM Properties p
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName;

SELECT
    ROUND(AVG(AreaM2), 2) AS AvgArea
FROM Properties;

SELECT
    a.AgencyName,
    COUNT(*) AS ListingsCount
FROM Properties p
JOIN Agencies a
ON p.AgencyID = a.AgencyID
GROUP BY a.AgencyName
ORDER BY ListingsCount DESC;

SELECT
    COUNT(*) AS SoldProperties
FROM Listings
WHERE Status = 'Sold';

SELECT
    p.Rooms,
    ROUND(AVG(l.Price), 2) AS AvgPrice
FROM Properties p
JOIN Listings l
ON p.PropertyID = l.PropertyID
GROUP BY p.Rooms
ORDER BY p.Rooms;

SELECT
    p.PropertyID,
    l.Price
FROM Properties p
JOIN Listings l
ON p.PropertyID = l.PropertyID
ORDER BY l.Price DESC
LIMIT 1;

SELECT
    c.CityName,
    COUNT(*) AS PropertyCount
FROM Properties p
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName
HAVING COUNT(*) > 10;

SELECT
    c.CityName,
    MAX(l.Price) AS MaxPrice
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName;

SELECT
    c.CityName,
    MIN(l.Price) AS MinPrice
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
JOIN Cities c
ON p.CityID = c.CityID
GROUP BY c.CityName;

SELECT
    PropertyID,
    Price
FROM Listings
WHERE Price >
(
    SELECT AVG(Price)
    FROM Listings
);

SELECT
    c.CityName,
    p.Rooms,
    l.Price
FROM Listings l
JOIN Properties p
ON l.PropertyID = p.PropertyID
JOIN Cities c
ON p.CityID = c.CityID
WHERE l.Status = 'Sold';

SELECT
    PropertyID,
    Price,
    CASE
        WHEN Price < 500000 THEN 'Cheap'
        WHEN Price < 800000 THEN 'Medium'
        ELSE 'Expensive'
    END AS PriceCategory
FROM Listings;