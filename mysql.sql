CREATE TABLE product.items (
    `Name` VARCHAR(255) NOT NULL,
    `code` VARCHAR(20) PRIMARY KEY,
    `category` VARCHAR(100),
    `size` VARCHAR(50),
    `unit_price` INT UNSIGNED,
    `inventory` INT UNSIGNED,
    `color` VARCHAR(100)
);