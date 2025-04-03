-- PROJECT DATABASE INITIALIZER SCRIPT
 
CREATE DATABASE species_detection_db;
USE species_detection_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(100),
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password varchar(50) NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE birds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    scientific_name VARCHAR(150),
    description TEXT
);
INSERT INTO birds (name, scientific_name, description) VALUES
('Common-Kingfisher', 'Alcedo atthis', 'A small, brightly colored bird with a distinctive blue and orange plumage, commonly found near rivers and lakes.'),
('Common-Myna', 'Acridotheres tristis', 'A medium-sized bird with brown body, black head, and bright yellow eye patches, known for its adaptability and ability to mimic sounds.'),
('Indian-Peacock', 'Pavo cristatus', 'The national bird of India, famous for its iridescent blue and green feathers and extravagant courtship displays.'),
('Indian-Roller', 'Coracias benghalensis', 'A strikingly colorful bird with shades of blue and green, often seen performing aerial acrobatics during flight.'),
('Vulture', 'Gyps indicus', 'A large scavenging bird of prey, known for its bald head and keen sense of smell, playing a crucial role in the ecosystem by cleaning up carcasses.');

select * from birds;

CREATE TABLE images (
    image_id INT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    name varchar(150),
    image_blob mediumblob NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    prediction varchar(150),
    accuracy INT,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES images(image_id) ON DELETE CASCADE
);



-- SAMPLE QUERIES (Do Not Execute)
-- REGISTRATION
INSERT INTO users (name, username, email, password) 
VALUES ('admin','admin_user', 'admin@gmail.com', 'admin');

-- LOGIN
SELECT id, username, email, password FROM users WHERE email = 'admin@gmail.com';

-- UPLOAD IMAGE
INSERT INTO images (image_id, user_id, image_blob) 
VALUES (12345,1, 'img_file_here');

-- SET PREDICTION
INSERT INTO predictions (image_id, prediction, accuracy) 
VALUES (12345, 'predicted_class', 92);

-- GET RESULT
SELECT predictions.prediction, predictions.accuracy
FROM predictions
JOIN images ON predictions.image_id = images.image_id
WHERE images.image_id = 12345;

SELECT scientific_name, description FROM birds where name = 'Common-Kingfisher';
