
-- create user with passw
CREATE USER 'MYSQL_USER'@'localhost' IDENTIFIED BY 'MYSQL_PASSWORD';

-- grant privileges
GRANT ALL PRIVILEGES ON *.* TO 'MYSQL_USER' WITH GRANT OPTION;

-- enable privileges
FLUSH PRIVILEGES;

-- create a database using placeholder
CREATE DATABASE IF NOT EXISTS `MYSQL_DATABASE`;

-- switch to the above database
USE `MYSQL_DATABASE`;

-- disable FULL_GROUP_BY
SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', ''));

