CREATE DATABASE IF NOT EXISTS news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE news_db;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    content TEXT NOT NULL,
    category_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

INSERT INTO categories (name) VALUES ('CONG NGHE'), ('AN TOAN THONG TIN');
INSERT INTO articles (title, summary, content, category_id) VALUES 
('Docker 2026', 'Container hoa he thong.', 'Trien khai bang Docker Compose...', 1);

-- Hardening: Hạn chế quyền user DB
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'news_app_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON news_db.* TO 'news_app_user'@'%';
FLUSH PRIVILEGES;
