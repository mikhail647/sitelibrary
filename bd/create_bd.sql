-- Создание базы данных
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

-- Таблица пользователей Django (примерная структура, адаптируйте под вашу CustomUser)
CREATE TABLE custom_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT NOT NULL,
    is_active TINYINT NOT NULL,
    date_joined DATETIME(6) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user' -- Добавлено поле роли
);

-- Таблица категорий читателей
CREATE TABLE reader_types (
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) NOT NULL,
    max_books_allowed INT NOT NULL,
    loan_period_days INT NOT NULL,
    can_use_reading_room BOOLEAN NOT NULL DEFAULT TRUE,
    can_use_loan BOOLEAN NOT NULL DEFAULT TRUE
);

-- Таблица читателей
CREATE TABLE library_readers (
    reader_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NULL, -- Связь с custom_user (необязательная)
    reader_type_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL, -- Возвращено
    last_name VARCHAR(50) NOT NULL, -- Возвращено
    middle_name VARCHAR(50), -- Возвращено
    library_card_number VARCHAR(20) UNIQUE NOT NULL,
    registration_date DATE NOT NULL,
    reader_status ENUM('active', 'suspended', 'expelled') NOT NULL DEFAULT 'active',
    suspension_end_date DATE,
    FOREIGN KEY (user_id) REFERENCES custom_user(id) ON DELETE SET NULL, -- Внешний ключ к custom_user (SET NULL при удалении пользователя)
    FOREIGN KEY (reader_type_id) REFERENCES reader_types(type_id)
);

-- Таблица студентов
CREATE TABLE student_readers (
    reader_id INT PRIMARY KEY,
    faculty_name VARCHAR(100) NOT NULL,
    group_number VARCHAR(20) NOT NULL,
    course_number INT NOT NULL,
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id)
);

-- Таблица преподавателей
CREATE TABLE teacher_readers (
    reader_id INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    academic_degree VARCHAR(50),
    academic_title VARCHAR(50),
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id)
);

-- Таблица других сотрудников
CREATE TABLE staff_readers (
    reader_id INT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    job_position VARCHAR(100) NOT NULL,
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id)
);

-- Таблица разовых читателей
CREATE TABLE temporary_readers (
    reader_id INT PRIMARY KEY,
    reader_type ENUM('FPC', 'applicant', 'intern') NOT NULL,
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id)
);

-- Таблица пунктов выдачи
CREATE TABLE library_locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    location_name VARCHAR(100) NOT NULL,
    location_type ENUM('loan', 'reading_room') NOT NULL,
    address VARCHAR(200) NOT NULL
);

-- Таблица книг
CREATE TABLE book_catalog (
    book_id INT PRIMARY KEY AUTO_INCREMENT,
    book_title VARCHAR(200) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    publication_year INT,
    publisher_name VARCHAR(100),
    acquisition_date DATE NOT NULL,
    book_status ENUM('available', 'lost', 'damaged') NOT NULL DEFAULT 'available'
);

-- Таблица авторов
CREATE TABLE book_authors (
    author_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50)
);

-- Таблица связи книг и авторов
CREATE TABLE book_author_relations (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES book_catalog(book_id),
    FOREIGN KEY (author_id) REFERENCES book_authors(author_id)
);

-- Таблица экземпляров книг
CREATE TABLE book_copies (
    copy_id INT PRIMARY KEY AUTO_INCREMENT,
    book_id INT NOT NULL,
    location_id INT NOT NULL,
    inventory_number VARCHAR(50) UNIQUE NOT NULL,
    copy_status ENUM('available', 'issued', 'lost', 'damaged') NOT NULL DEFAULT 'available',
    FOREIGN KEY (book_id) REFERENCES book_catalog(book_id),
    FOREIGN KEY (location_id) REFERENCES library_locations(location_id)
);

-- Таблица выдачи книг
CREATE TABLE book_loans (
    loan_id INT PRIMARY KEY AUTO_INCREMENT,
    reader_id INT NOT NULL,
    copy_id INT NOT NULL,
    location_id INT NOT NULL,
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    loan_status ENUM('active', 'returned', 'overdue', 'lost') NOT NULL DEFAULT 'active',
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id),
    FOREIGN KEY (copy_id) REFERENCES book_copies(copy_id),
    FOREIGN KEY (location_id) REFERENCES library_locations(location_id)
);

-- Таблица межбиблиотечного абонемента
CREATE TABLE interlibrary_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    reader_id INT NOT NULL,
    book_id INT NOT NULL,
    request_date DATE NOT NULL,
    request_status ENUM('pending', 'approved', 'received', 'returned') NOT NULL DEFAULT 'pending',
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id),
    FOREIGN KEY (book_id) REFERENCES book_catalog(book_id)
);

-- Таблица штрафов
CREATE TABLE library_fines (
    fine_id INT PRIMARY KEY AUTO_INCREMENT,
    reader_id INT NOT NULL,
    loan_id INT,
    request_id INT,
    fine_amount DECIMAL(10,2) NOT NULL,
    fine_date DATE NOT NULL,
    fine_status ENUM('pending', 'paid', 'cancelled') NOT NULL DEFAULT 'pending',
    fine_reason ENUM('overdue', 'lost', 'damaged') NOT NULL,
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id),
    FOREIGN KEY (loan_id) REFERENCES book_loans(loan_id),
    FOREIGN KEY (request_id) REFERENCES interlibrary_requests(request_id)
);

-- Таблица регистрации читателей в пунктах выдачи
CREATE TABLE reader_registrations (
    registration_id INT PRIMARY KEY AUTO_INCREMENT,
    reader_id INT NOT NULL,
    location_id INT NOT NULL,
    registration_date DATE NOT NULL,
    registration_expiry_date DATE NOT NULL,
    FOREIGN KEY (reader_id) REFERENCES library_readers(reader_id),
    FOREIGN KEY (location_id) REFERENCES library_locations(location_id)
);