CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(25) NOT NULL UNIQUE,
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
    title VARCHAR(150) NOT NULL,
    review_text VARCHAR(1000) NOT NULL,
    stars INTEGER NOT NULL,
    date TIMESTAMP,
    museum_id INTEGER REFERENCES museums,
    author_id INTEGER REFERENCES users
);

CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);