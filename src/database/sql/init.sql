CREATE TYPE season_enum AS ENUM ('Summer', 'Fall', 'Winter', 'Spring');

CREATE TABLE products (
    id              bigint PRIMARY KEY,
    image_id        bigint UNIQUE,
    gender          varchar(20) NOT NULL,
    master_category varchar(30) NOT NULL,
    sub_category    varchar(30),
    article_type    varchar(30),
    base_colour     varchar(30),
    season          varchar(10),
    year            int ,
    usage           varchar(30),
    display_name    varchar(100)
);

-- For local:
-- COPY products FROM '/tmp/database/data.csv' DELIMITER ',' CSV NULL 'null';

-- For Kubernetes:
INSERT INTO products(id, image_id, gender, master_category, sub_category, article_type, base_colour, season, year, usage, display_name)
VALUES
    (1868,10000,'Women','Apparel','Bottomwear','Skirts','White','Summer',2011,'Casual','Palm Tree Girls Sp Jace Sko White Skirts'),
    (4897,10001,'Women','Apparel','Bottomwear','Skirts','Blue','Summer',2011,'Casual','Palm Tree Kids Girls Sp Jema Skt Blue Skirts'),
    (22373,10003,'Women','Apparel','Topwear','Tshirts','White','Fall',2011,'Sports','Nike Women As Nike Eleme White T-Shirt');

CREATE INDEX category_index ON products (master_category);
CREATE INDEX sub_category_index ON products (sub_category);