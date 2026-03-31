-- init-db.sql — Creates both application databases on first PostgreSQL startup
-- Mounted at /docker-entrypoint-initdb.d/ — runs automatically when data volume is empty

CREATE DATABASE auth_db;
CREATE DATABASE orders_db;
