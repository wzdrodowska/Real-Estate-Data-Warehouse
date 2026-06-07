CREATE TABLE DimCity (
    CityID INTEGER PRIMARY KEY,
    CityName TEXT,
    Voivodeship TEXT
);

CREATE TABLE DimProperty (
    PropertyID INTEGER PRIMARY KEY,
    AreaM2 REAL,
    Rooms INTEGER,
    YearBuilt INTEGER
);

CREATE TABLE DimDate (
    DateID INTEGER PRIMARY KEY,
    FullDate DATE,
    Year INTEGER,
    Month INTEGER,
    Quarter INTEGER
);

CREATE TABLE FactSales (
    SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    DateID INTEGER,
    PropertyID INTEGER,
    CityID INTEGER,
    SalePrice REAL,
    PricePerM2 REAL,
    FOREIGN KEY(DateID) REFERENCES DimDate(DateID),
    FOREIGN KEY(PropertyID) REFERENCES DimProperty(PropertyID),
    FOREIGN KEY(CityID) REFERENCES DimCity(CityID)
);