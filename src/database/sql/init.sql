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

COPY products FROM '/tmp/database/data.csv' DELIMITER ',' CSV NULL 'null';

CREATE INDEX category_index ON products (master_category);
CREATE INDEX sub_category_index ON products (sub_category);