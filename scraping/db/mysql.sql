DROP TABLE IF EXISTS realestate;
CREATE TABLE realestate (
  guid CHAR(32) PRIMARY KEY,
  url TEXT,
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
  
  wc TEXT,
  walls TEXT,
  ceilings DECIMAL(5,2),
  rennovation TEXT,
  builtdate YEAR,
  heating TEXT,
  water TEXT,
  balcony TEXT,
  security TEXT,
  
  postDate DATETIME,
  updated DATETIME
) DEFAULT CHARSET=utf8;
