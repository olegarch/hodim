DROP TABLE IF EXISTS realestate;
CREATE TABLE realestate (
  guid CHAR(32) PRIMARY KEY,
  url TEXT,
  id TEXT,
  title TEXT,
  description TEXT,

  rooms INT,
  floor TINYINT UNSIGNED,
  totfloors TINYINT UNSIGNED,
  
  m2 DECIMAL(5,2),
  kitchenm2 DECIMAL(5,2),
  restm2 DECIMAL(5,2),

  price DECIMAL(10),

  location POINT,
  city TEXT,
  district TEXT,
  street TEXT,
  
  updated DATETIME
) DEFAULT CHARSET=utf8;
