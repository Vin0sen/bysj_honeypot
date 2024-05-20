CREATE database `emp`;
use emp;

CREATE USER `admin01`@`%` IDENTIFIED WITH mysql_native_password BY 'p@ssword';
GRANT ALL ON *.* TO `admin01`@`%` WITH GRANT OPTION;
FLUSH PRIVILEGES;
