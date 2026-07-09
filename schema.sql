-- Run this once, e.g.  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS taskmanager;
USE taskmanager;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id VARCHAR(20) NOT NULL,
    emp_name VARCHAR(100) NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    completed ENUM('Yes', 'No') NOT NULL DEFAULT 'No',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
