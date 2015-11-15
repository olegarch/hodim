DROP TABLE IF EXISTS realestate;
CREATE TABLE realestate (
  guid CHAR(32) PRIMARY KEY,
  url TEXT,
  id TEXT,
  title TEXT,
  description TEXT,

  rooms TEXT,
  floor TINYINT UNSIGNED,
  totfloors TINYINT UNSIGNED,
  m2 FLOAT,

  price DECIMAL(10),

  location POINT,
  city TEXT,
  district TEXT,
  street TEXT,
  
  updated DATETIME
) DEFAULT CHARSET=utf8;
