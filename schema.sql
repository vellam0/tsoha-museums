CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(150) NOT NULL
);

CREATE TABLE museums (
    id SERIAL PRIMARY KEY,
    name VARCHAR(250) NOT NULL UNIQUE,
    bio TEXT NOT NULL,
    address TEXT NOT NULL,
    opening_hours VARCHAR(1000) NOT NULL,
    museum_type VARCHAR(250) NOT NULL,
    tags VARCHAR(250),
    img_url VARCHAR(250)
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    review_text TEXT NOT NULL,
    stars INTEGER NOT NULL,
    date TIMESTAMP,
    museum_id INTEGER REFERENCES museums,
    author_id INTEGER REFERENCES users
);