-- Использование базы данных
USE library_db; -- Убедись, что имя БД правильное (на PythonAnywhere может быть gods0ft$default)

-- Отключить проверку внешних ключей для ускорения вставки
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO"; -- Может помочь с AUTO_INCREMENT проблемами
SET SQL_SAFE_UPDATES = 0; -- Отключаем безопасный режим для массовых операций

-- Очистка таблиц перед вставкой (с проверкой существования таблиц)
-- Удаляем таблицу book_requests только если она существует
DROP TABLE IF EXISTS temp_tables;
CREATE TEMPORARY TABLE temp_tables (name VARCHAR(50));

-- Получаем список существующих таблиц
INSERT INTO temp_tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = DATABASE() AND table_name IN (
    'reader_registrations',
    'library_fines',
    'interlibrary_requests',
    'book_loans',
    'book_author_relations',
    'book_copies',
    'book_catalog',
    'book_authors',
    'library_locations',
    'temporary_readers',
    'teacher_readers',
    'student_readers',
    'library_readers',
    'reader_types'
);

-- Удаляем данные только из существующих таблиц
DELETE FROM reader_registrations WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'reader_registrations');
DELETE FROM library_fines WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'library_fines');
DELETE FROM interlibrary_requests WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'interlibrary_requests');
DELETE FROM book_loans WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'book_loans');
DELETE FROM book_author_relations WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'book_author_relations');
DELETE FROM book_copies WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'book_copies');
DELETE FROM book_catalog WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'book_catalog');
DELETE FROM book_authors WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'book_authors');
DELETE FROM library_locations WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'library_locations');
DELETE FROM temporary_readers WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'temporary_readers');
DELETE FROM teacher_readers WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'teacher_readers');
DELETE FROM student_readers WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'student_readers');
DELETE FROM library_readers WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'library_readers');
DELETE FROM reader_types WHERE EXISTS (SELECT 1 FROM temp_tables WHERE name = 'reader_types');
-- DELETE FROM custom_user; -- НЕ удаляем пользователей, они должны быть созданы отдельно

DROP TEMPORARY TABLE IF EXISTS temp_tables;

-- 1. Заполнение таблицы категорий читателей (`reader_types`)
-- Добавляем fine_per_day если его нет (совместимо со старыми версиями MySQL)
SET @column_exists = 0;
SELECT COUNT(*) INTO @column_exists 
FROM information_schema.columns 
WHERE table_schema = DATABASE() 
AND table_name = 'reader_types' 
AND column_name = 'fine_per_day';

SET @alter_command = IF(@column_exists = 0, 
    'ALTER TABLE reader_types ADD COLUMN fine_per_day DECIMAL(10,2) DEFAULT 10.00',
    'SELECT 1');

PREPARE alter_stmt FROM @alter_command;
EXECUTE alter_stmt;
DEALLOCATE PREPARE alter_stmt;

INSERT INTO reader_types (type_id, type_name, max_books_allowed, loan_period_days, can_use_reading_room, can_use_loan, fine_per_day)
VALUES
(1, 'Студент', 7, 21, TRUE, TRUE, 5.00),
(2, 'Преподаватель', 10, 45, TRUE, TRUE, 8.00),
(3, 'Сотрудник', 10, 30, TRUE, TRUE, 8.00),
(4, 'Администратор', 15, 60, TRUE, TRUE, 10.00),
(5, 'Обычный читатель', 5, 14, TRUE, TRUE, 5.00),
(6, 'Слушатель ФПК', 3, 0, TRUE, FALSE, 5.00),
(7, 'Абитуриент', 3, 0, TRUE, FALSE, 5.00),
(8, 'Стажер', 5, 0, TRUE, FALSE, 5.00)
ON DUPLICATE KEY UPDATE
    max_books_allowed=VALUES(max_books_allowed),
    loan_period_days=VALUES(loan_period_days),
    can_use_reading_room=VALUES(can_use_reading_room),
    can_use_loan=VALUES(can_use_loan),
    fine_per_day=VALUES(fine_per_day);

-- 2. Генерация читателей (`library_readers`)
SET @reader_num := 100000; -- Начинаем с большого числа для уникальности

-- Проверяем структуру таблицы library_readers
SET @has_can_take_books_home = 0;
SELECT COUNT(*) INTO @has_can_take_books_home 
FROM information_schema.columns 
WHERE table_schema = DATABASE() 
AND table_name = 'library_readers' 
AND column_name = 'can_take_books_home';

-- Вставка с учетом наличия/отсутствия поля can_take_books_home
INSERT INTO library_readers (
    reader_type_id, 
    first_name, 
    last_name, 
    middle_name, 
    library_card_number, 
    registration_date, 
    reader_status, 
    suspension_end_date
    -- can_take_books_home добавляется динамически если столбец существует
)
SELECT
    FLOOR(1+RAND()*8),
    CASE FLOOR(1+RAND()*20)
        WHEN 1 THEN 'Иван' WHEN 2 THEN 'Алексей' WHEN 3 THEN 'Дмитрий' WHEN 4 THEN 'Сергей'
        WHEN 5 THEN 'Андрей' WHEN 6 THEN 'Михаил' WHEN 7 THEN 'Артем' WHEN 8 THEN 'Павел'
        WHEN 9 THEN 'Максим' WHEN 10 THEN 'Никита' WHEN 11 THEN 'Анна' WHEN 12 THEN 'Мария'
        WHEN 13 THEN 'Елена' WHEN 14 THEN 'Ольга' WHEN 15 THEN 'Наталья' WHEN 16 THEN 'Ирина'
        WHEN 17 THEN 'Татьяна' WHEN 18 THEN 'Юлия' WHEN 19 THEN 'Екатерина' ELSE 'Александра'
    END,
    CASE FLOOR(1+RAND()*20)
        WHEN 1 THEN 'Иванов' WHEN 2 THEN 'Петров' WHEN 3 THEN 'Сидоров' WHEN 4 THEN 'Смирнов'
        WHEN 5 THEN 'Кузнецов' WHEN 6 THEN 'Попов' WHEN 7 THEN 'Васильев' WHEN 8 THEN 'Павлов'
        WHEN 9 THEN 'Семенов' WHEN 10 THEN 'Голубев' WHEN 11 THEN 'Волков' WHEN 12 THEN 'Козлов'
        WHEN 13 THEN 'Лебедев' WHEN 14 THEN 'Новиков' WHEN 15 THEN 'Морозов' WHEN 16 THEN 'Романов'
        WHEN 17 THEN 'Орлов' WHEN 18 THEN 'Алексеев' WHEN 19 THEN 'Николаев' ELSE 'Сергеев'
    END,
    CASE WHEN RAND() < 0.8 THEN 
        CASE FLOOR(1+RAND()*15)
            WHEN 1 THEN 'Александрович' WHEN 2 THEN 'Дмитриевич' WHEN 3 THEN 'Сергеевич'
            WHEN 4 THEN 'Андреевич' WHEN 5 THEN 'Игоревич' WHEN 6 THEN 'Олегович'
            WHEN 7 THEN 'Владимирович' WHEN 8 THEN 'Борисович' WHEN 9 THEN 'Анатольевич'
            WHEN 10 THEN 'Николаевич' WHEN 11 THEN 'Викторович' WHEN 12 THEN 'Станиславович'
            WHEN 13 THEN 'Геннадьевич' WHEN 14 THEN 'Валентинович' ELSE 'Юрьевич'
        END
    ELSE NULL END,
    CONCAT('ЛК', LPAD(@reader_num := @reader_num + 1, 6, '0')),
    DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND() * 1825) DAY),
    CASE
        WHEN RAND() < 0.05 THEN 'suspended'
        WHEN RAND() < 0.02 THEN 'inactive'
        ELSE 'active'
    END,
    CASE WHEN RAND() < 0.03 THEN DATE_ADD(CURDATE(), INTERVAL FLOOR(RAND() * 180) DAY) ELSE NULL END
    -- Значение для can_take_books_home не добавляем, так как столбца нет
FROM
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t1,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t2,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t3
LIMIT 5000;

-- 3. Заполнение студентов (`student_readers`)
INSERT INTO student_readers (reader_id, faculty, study_group, course_number)
SELECT
    lr.reader_id,
    CASE FLOOR(1+RAND()*6)
        WHEN 1 THEN 'Информационные технологии' 
        WHEN 2 THEN 'Экономика и управление' 
        WHEN 3 THEN 'Гуманитарные науки'
        WHEN 4 THEN 'Естественные науки' 
        WHEN 5 THEN 'Инженерные науки' 
        ELSE 'Юридический'
    END,
    CONCAT(
        CASE FLOOR(1+RAND()*6)
            WHEN 1 THEN 'Б' WHEN 2 THEN 'М' WHEN 3 THEN 'А' 
            WHEN 4 THEN 'С' WHEN 5 THEN 'К' ELSE 'П'
        END,
        FLOOR(RAND()*10), FLOOR(RAND()*10), '-', FLOOR(RAND()*10), FLOOR(RAND()*10)
    ),
    FLOOR(1+RAND()*5)
FROM library_readers lr
WHERE lr.reader_type_id = 1  -- Тип 'Студент'
LIMIT 2000;

-- 4. Заполнение преподавателей/сотрудников (`teacher_readers`)
INSERT INTO teacher_readers (reader_id, department, academic_degree, academic_title, position)
SELECT
    lr.reader_id,
    CASE FLOOR(1+RAND()*10)
        WHEN 1 THEN 'Кафедра высшей математики'
        WHEN 2 THEN 'Кафедра информационных систем'
        WHEN 3 THEN 'Кафедра теоретической физики'
        WHEN 4 THEN 'Кафедра мировой экономики'
        WHEN 5 THEN 'Кафедра русской литературы'
        WHEN 6 THEN 'Кафедра международного права'
        WHEN 7 THEN 'Кафедра органической химии'
        WHEN 8 THEN 'Кафедра биоинженерии'
        WHEN 9 THEN 'Кафедра робототехники'
        ELSE 'Кафедра искусственного интеллекта'
    END,
    CASE FLOOR(1+RAND()*5)
        WHEN 1 THEN 'Кандидат наук'
        WHEN 2 THEN 'Доктор наук'
        WHEN 3 THEN 'PhD'
        ELSE NULL
    END,
    CASE FLOOR(1+RAND()*5)
        WHEN 1 THEN 'Доцент'
        WHEN 2 THEN 'Профессор'
        WHEN 3 THEN 'Старший научный сотрудник'
        ELSE NULL
    END,
    CASE FLOOR(1+RAND()*8)
        WHEN 1 THEN 'Преподаватель'
        WHEN 2 THEN 'Старший преподаватель'
        WHEN 3 THEN 'Доцент'
        WHEN 4 THEN 'Профессор'
        WHEN 5 THEN 'Зав. кафедрой'
        WHEN 6 THEN 'Научный сотрудник'
        WHEN 7 THEN 'Лаборант'
        ELSE 'Инженер'
    END
FROM library_readers lr
WHERE lr.reader_type_id IN (2, 3, 4)  -- Типы 'Преподаватель', 'Сотрудник', 'Администратор'
LIMIT 1300;

-- 5. Заполнение временных читателей (`temporary_readers`)
INSERT INTO temporary_readers (reader_id, reader_type)
SELECT
    lr.reader_id,
    CASE FLOOR(1+RAND()*3)
        WHEN 1 THEN 'FPC'
        WHEN 2 THEN 'applicant'
        ELSE 'intern'
    END
FROM library_readers lr
WHERE lr.reader_type_id IN (6, 7, 8)  -- Типы 'Слушатель ФПК', 'Абитуриент', 'Стажер'
LIMIT 300;

-- 6. Заполнение пунктов выдачи (`library_locations`)
INSERT INTO library_locations (location_id, location_name, location_type, address)
VALUES
    (1, 'Главный абонемент', 'loan', 'Корпус А, этаж 1'),
    (2, 'Читальный зал №1', 'reading_room', 'Корпус А, этаж 2'),
    (3, 'Научный абонемент', 'loan', 'Корпус Б, этаж 3'),
    (4, 'Зал периодики', 'reading_room', 'Корпус Б, этаж 1'),
    (5, 'Фонд редких книг', 'loan', 'Корпус В, этаж 4'),
    (6, 'Межбиблиотечный абонемент', 'loan', 'Корпус А, этаж 1'),
    (7, 'Электронный читальный зал', 'reading_room', 'Корпус Г, этаж 2'),
    (8, 'Абонемент №2 (Технический)', 'loan', 'Корпус Д, этаж 1'),
    (9, 'Читальный зал №2 (Гуманитарный)', 'reading_room', 'Корпус Е, этаж 3')
ON DUPLICATE KEY UPDATE 
    location_name=VALUES(location_name),
    location_type=VALUES(location_type),
    address=VALUES(address);

-- 7. Заполнение каталога книг (`book_catalog`)
SET @book_num := 0;
INSERT INTO book_catalog (book_title, isbn, publication_year, publisher_name, acquisition_date, book_status)
SELECT
    CONCAT(
        CASE FLOOR(1+RAND()*10)
            WHEN 1 THEN 'Введение в ' WHEN 2 THEN 'Основы ' WHEN 3 THEN 'Теория '
            WHEN 4 THEN 'Практика ' WHEN 5 THEN 'Современные методы ' WHEN 6 THEN 'Исследование '
            WHEN 7 THEN 'Анализ ' WHEN 8 THEN 'Система ' WHEN 9 THEN 'Принципы '
            ELSE 'Разработка '
        END,
        CASE FLOOR(1+RAND()*10)
            WHEN 1 THEN 'мат. анализа' WHEN 2 THEN 'квант. физики' WHEN 3 THEN 'ИИ'
            WHEN 4 THEN 'эконом. систем' WHEN 5 THEN 'биоинформатики' WHEN 6 THEN 'робототехники'
            WHEN 7 THEN 'БД' WHEN 8 THEN 'комп. сетей' WHEN 9 THEN 'машин. обучения'
            ELSE 'орг. химии'
        END
    ),
    CONCAT('978', LPAD(@book_num := @book_num + 1, 9, '0'), FLOOR(RAND()*10)),
    1960 + FLOOR(RAND()*60),
    CASE FLOOR(1+RAND()*10)
        WHEN 1 THEN 'Наука' WHEN 2 THEN 'Техносфера' WHEN 3 THEN 'Питер'
        WHEN 4 THEN 'Эксмо' WHEN 5 THEN 'АСТ' WHEN 6 THEN 'МИФ'
        WHEN 7 THEN 'Дрофа' WHEN 8 THEN 'Просвещение' WHEN 9 THEN 'Юрайт'
        ELSE 'Лань'
    END,
    DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND()*3650) DAY),
    CASE
        WHEN RAND() < 0.02 THEN 'lost'
        WHEN RAND() < 0.01 THEN 'damaged'
        ELSE 'available'
    END
FROM
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t1,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t2,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t3,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t4
LIMIT 10000;

-- 8. Заполнение авторов (`book_authors`)
INSERT INTO book_authors (first_name, last_name, middle_name)
SELECT
    CASE FLOOR(1+RAND()*20)
        WHEN 1 THEN 'Лев' WHEN 2 THEN 'Федор' WHEN 3 THEN 'Александр'
        WHEN 4 THEN 'Николай' WHEN 5 THEN 'Михаил' WHEN 6 THEN 'Иван'
        WHEN 7 THEN 'Антон' WHEN 8 THEN 'Алексей' WHEN 9 THEN 'Владимир'
        WHEN 10 THEN 'Борис' WHEN 11 THEN 'Марк' WHEN 12 THEN 'Эрнест'
        WHEN 13 THEN 'Джордж' WHEN 14 THEN 'Оскар' WHEN 15 THEN 'Виктор'
        WHEN 16 THEN 'Джон' WHEN 17 THEN 'Уильям' WHEN 18 THEN 'Чарльз'
        WHEN 19 THEN 'Джейн' ELSE 'Теодор'
    END,
    CASE FLOOR(1+RAND()*20)
        WHEN 1 THEN 'Толстой' WHEN 2 THEN 'Достоевский' WHEN 3 THEN 'Пушкин'
        WHEN 4 THEN 'Гоголь' WHEN 5 THEN 'Булгаков' WHEN 6 THEN 'Тургенев'
        WHEN 7 THEN 'Чехов' WHEN 8 THEN 'Гончаров' WHEN 9 THEN 'Лермонтов'
        WHEN 10 THEN 'Шолохов' WHEN 11 THEN 'Оруэлл' WHEN 12 THEN 'Хемингуэй'
        WHEN 13 THEN 'Маркес' WHEN 14 THEN 'Фицджеральд' WHEN 15 THEN 'Сэлинджер'
        WHEN 16 THEN 'Стивенсон' WHEN 17 THEN 'Диккенс' WHEN 18 THEN 'Бронте'
        WHEN 19 THEN 'Уайльд' ELSE 'Дюма'
    END,
    CASE WHEN RAND() < 0.7 THEN
        CASE FLOOR(1+RAND()*15)
            WHEN 1 THEN 'Николаевич' WHEN 2 THEN 'Федорович' WHEN 3 THEN 'Сергеевич'
            WHEN 4 THEN 'Александрович' WHEN 5 THEN 'Михайлович' WHEN 6 THEN 'Иванович'
            WHEN 7 THEN 'Борисович' WHEN 8 THEN 'Львович' WHEN 9 THEN 'Анатольевич'
            WHEN 10 THEN 'Васильевич' WHEN 11 THEN 'Георгиевич' WHEN 12 THEN 'Павлович'
            WHEN 13 THEN 'Викторович' WHEN 14 THEN 'Олегович' ELSE 'Юрьевич'
        END
    ELSE NULL END
FROM
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t1,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t2,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t3
LIMIT 500;

-- 9. Связь книг и авторов (`book_author_relations`)
-- Сначала добавим по одному автору каждой книге
INSERT IGNORE INTO book_author_relations (book_id, author_id)
SELECT 
    b.book_id,
    a.author_id
FROM 
    book_catalog b,
    (SELECT author_id, @row_num1 := @row_num1 + 1 AS row_num FROM book_authors, (SELECT @row_num1 := 0) r) a
WHERE 
    MOD(b.book_id, (SELECT COUNT(*) FROM book_authors)) + 1 = a.row_num;

-- Добавим вторых авторов для ~60% книг
INSERT IGNORE INTO book_author_relations (book_id, author_id)
SELECT 
    b.book_id,
    a.author_id
FROM 
    book_catalog b,
    (SELECT author_id, @row_num2 := @row_num2 + 1 AS row_num FROM book_authors, (SELECT @row_num2 := 0) r) a
WHERE 
    MOD(b.book_id + 100, (SELECT COUNT(*) FROM book_authors)) + 1 = a.row_num
    AND MOD(b.book_id, 10) < 6;  -- ~60% шанс

-- Добавим третьих авторов для ~30% книг
INSERT IGNORE INTO book_author_relations (book_id, author_id)
SELECT 
    b.book_id,
    a.author_id
FROM 
    book_catalog b,
    (SELECT author_id, @row_num3 := @row_num3 + 1 AS row_num FROM book_authors, (SELECT @row_num3 := 0) r) a
WHERE 
    MOD(b.book_id + 200, (SELECT COUNT(*) FROM book_authors)) + 1 = a.row_num
    AND MOD(b.book_id, 10) < 3;  -- ~30% шанс

-- 10. Создание экземпляров книг (`book_copies`)
INSERT INTO book_copies (book_id, location_id, inventory_number, copy_status, cost)
SELECT
    b.book_id,
    FLOOR(1 + RAND() * 9),  -- location_id от 1 до 9
    CONCAT('INV-', LPAD(b.book_id, 5, '0'), '-', copies.n),
    CASE
        WHEN RAND() < 0.85 THEN 'available'
        WHEN RAND() < 0.08 THEN 'issued'
        WHEN RAND() < 0.04 THEN 'damaged'
        WHEN RAND() < 0.02 THEN 'lost'
        ELSE 'written_off'
    END,
    ROUND(RAND() * 1500 + 100, 2)
FROM book_catalog b
CROSS JOIN (SELECT 1 AS n UNION SELECT 2 UNION SELECT 3) AS copies;

-- 11. Заполнение выдачи книг (`book_loans`)
-- Создаем временную таблицу для хранения ID выданных копий
CREATE TEMPORARY TABLE IF NOT EXISTS temp_issued_copies (
    copy_id INT PRIMARY KEY
);

-- Создаем временную таблицу с читателями
CREATE TEMPORARY TABLE IF NOT EXISTS temp_loan_readers AS
SELECT 
    lr.reader_id, 
    lr.reader_type_id,
    rt.loan_period_days
FROM 
    library_readers lr
JOIN 
    reader_types rt ON lr.reader_type_id = rt.type_id
WHERE 
    rt.can_use_loan = TRUE 
LIMIT 7000;

-- Создаем временную таблицу с доступными копиями
CREATE TEMPORARY TABLE IF NOT EXISTS temp_available_copies AS
SELECT 
    bc.copy_id, 
    bc.book_id, 
    bc.location_id 
FROM 
    book_copies bc
WHERE 
    bc.copy_status = 'available' 
LIMIT 30000;

-- Создаем выдачи
INSERT INTO book_loans (reader_id, copy_id, location_id, loan_date, due_date, return_date, loan_status)
SELECT
    r.reader_id,
    c.copy_id,
    c.location_id,
    @loan_date := DATE(DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 730) DAY)),
    @due_date := DATE_ADD(@loan_date, INTERVAL r.loan_period_days DAY),
    @return_date := CASE 
        WHEN RAND() < 0.8 THEN DATE_ADD(@loan_date, INTERVAL FLOOR(RAND() * (r.loan_period_days + 30)) DAY)
        ELSE NULL 
    END,
    CASE
        WHEN @return_date IS NOT NULL THEN 'returned'
        WHEN @due_date < CURDATE() THEN 'overdue'
        ELSE 'active'
    END
FROM
    temp_loan_readers r,
    temp_available_copies c
WHERE
    (r.reader_id + c.copy_id) % 10 < 7  -- ~70% шанс
LIMIT 20000;

-- Сохраняем ID копий с активными или просроченными выдачами
INSERT INTO temp_issued_copies (copy_id)
SELECT bl.copy_id
FROM book_loans bl
WHERE bl.loan_status IN ('active', 'overdue');

-- Обновляем статус копий
UPDATE book_copies bc
JOIN temp_issued_copies tic ON bc.copy_id = tic.copy_id
SET bc.copy_status = 'issued';

-- Удаляем временные таблицы
DROP TEMPORARY TABLE IF EXISTS temp_issued_copies;
DROP TEMPORARY TABLE IF EXISTS temp_loan_readers;
DROP TEMPORARY TABLE IF EXISTS temp_available_copies;

-- 12. Межбиблиотечные запросы (`interlibrary_requests`)
-- Пропускаем processed_by если таблица custom_user не существует
INSERT INTO interlibrary_requests (reader_id, book_id, request_date, request_status, required_by_date, notes, staff_notes, processed_date)
SELECT
    lr.reader_id,
    bc.book_id,
    @req_date := DATE(DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 200) DAY)),
    @req_status := CASE FLOOR(1+RAND()*9)
        WHEN 1 THEN 'pending' WHEN 2 THEN 'approved' WHEN 3 THEN 'rejected'
        WHEN 4 THEN 'processing' WHEN 5 THEN 'received' WHEN 6 THEN 'issued'
        WHEN 7 THEN 'returned' WHEN 8 THEN 'closed' ELSE 'cancelled'
    END,
    CASE WHEN RAND() < 0.3 THEN DATE_ADD(@req_date, INTERVAL FLOOR(RAND()*30)+7 DAY) ELSE NULL END,
    CASE WHEN RAND() < 0.2 THEN 'Нужно для курсовой работы' ELSE NULL END,
    CASE WHEN @req_status NOT IN ('pending', 'cancelled') AND RAND() < 0.4 THEN 'Заказано у партнера XYZ' ELSE NULL END,
    CASE WHEN @req_status NOT IN ('pending', 'cancelled') THEN DATE_ADD(@req_date, INTERVAL FLOOR(RAND()*10)+1 DAY) ELSE NULL END
FROM 
    library_readers lr
JOIN 
    reader_types rt ON lr.reader_type_id = rt.type_id,
    (SELECT DISTINCT book_id FROM book_catalog ORDER BY RAND() LIMIT 1000) bc
WHERE 
    rt.type_name IN ('Преподаватель', 'Сотрудник') 
    AND (lr.reader_id + bc.book_id) % 10 < 5  -- ~50% шанс
LIMIT 5000;

-- 13. Штрафы (`library_fines`)
-- Штрафы за просрочку
INSERT INTO library_fines (reader_id, loan_id, request_id, fine_amount, fine_date, fine_status, fine_reason, notes)
SELECT
    bl.reader_id,
    bl.loan_id,
    NULL,
    -- Учитываем возможное отсутствие fine_per_day, используя дефолтное значение
    ROUND(DATEDIFF(IFNULL(bl.return_date, CURDATE()), bl.due_date) * 
          IFNULL(rt.fine_per_day, 10.00) * (0.8 + RAND() * 0.5), 2),
    DATE_ADD(bl.due_date, INTERVAL FLOOR(1+RAND()*5) DAY),
    CASE FLOOR(1+RAND()*3)
        WHEN 1 THEN 'pending' WHEN 2 THEN 'paid' ELSE 'cancelled'
    END,
    'overdue',
    CASE WHEN RAND() < 0.1 THEN 'Напоминание отправлено' ELSE NULL END
FROM 
    book_loans bl
JOIN 
    library_readers lr ON bl.reader_id = lr.reader_id
JOIN 
    reader_types rt ON lr.reader_type_id = rt.type_id
WHERE 
    bl.loan_status = 'overdue' OR (bl.loan_status = 'returned' AND bl.return_date > bl.due_date)
LIMIT 5000;

-- Штрафы за утерю/повреждение
INSERT INTO library_fines (reader_id, loan_id, request_id, fine_amount, fine_date, fine_status, fine_reason, notes)
SELECT
    bl.reader_id,
    bl.loan_id,
    NULL,
    ROUND(IFNULL(bc.cost, 500) * 
          CASE WHEN bc.copy_status = 'lost' THEN 10 ELSE 0.5 END * 
          (0.8 + RAND() * 0.4), 2),
    DATE(IFNULL(bl.return_date, CURDATE())),
    CASE FLOOR(1+RAND()*3)
        WHEN 1 THEN 'pending' WHEN 2 THEN 'paid' ELSE 'cancelled'
    END,
    bc.copy_status,
    CASE WHEN RAND() < 0.1 THEN 'Составлен акт' ELSE NULL END
FROM 
    book_loans bl
JOIN 
    book_copies bc ON bl.copy_id = bc.copy_id
WHERE 
    bc.copy_status IN ('lost', 'damaged')
LIMIT 5000;

-- 14. Регистрация читателей в пунктах (`reader_registrations`)
INSERT INTO reader_registrations (reader_id, location_id, registration_date, registration_expiry_date)
SELECT
    lr.reader_id,
    loc.location_id,
    @reg_date := DATE_SUB(lr.registration_date, INTERVAL FLOOR(RAND()*60) DAY),
    DATE_ADD(@reg_date, INTERVAL 365 DAY)
FROM 
    (SELECT reader_id, registration_date FROM library_readers ORDER BY RAND() LIMIT 2000) lr,
    library_locations loc
WHERE 
    (lr.reader_id + loc.location_id) % 10 < 5  -- ~50% шанс
LIMIT 20000;

-- 15. Запросы на книги от пользователей (`book_requests`)
-- Таблица отсутствует, поэтому эту секцию пропускаем
/*
INSERT INTO book_requests (book_id, requested_location_id, request_date, status, notes)
SELECT
    (SELECT book_id FROM book_catalog ORDER BY RAND() LIMIT 1),
    (SELECT location_id FROM library_locations ORDER BY RAND() LIMIT 1),
    @req_bk_date := DATE(DATE_SUB(NOW(), INTERVAL FLOOR(RAND()*90) DAY)),
    @req_bk_status := CASE FLOOR(1+RAND()*5)
        WHEN 1 THEN 'pending' WHEN 2 THEN 'approved' WHEN 3 THEN 'rejected'
        WHEN 4 THEN 'issued' ELSE 'cancelled'
    END,
    CASE WHEN @req_bk_status = 'rejected' AND RAND() < 0.5 
         THEN 'Книга в ремонте' 
         ELSE NULL 
    END
FROM 
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t1,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t2,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t3
LIMIT 3000;
*/

-- Включить проверку внешних ключей
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1; -- Включаем безопасный режим обратно