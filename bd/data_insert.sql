-- Использование базы данных (замените на ваше имя БД, если отличается)
USE library_db; 

-- Отключить проверку внешних ключей для ускорения вставки
SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO"; 
SET SQL_SAFE_UPDATES = 0; 

-- Очистка таблиц перед вставкой (опционально, закомментируйте если не нужно)
-- ПОРЯДОК ВАЖЕН из-за внешних ключей!
DELETE FROM reader_registrations;
DELETE FROM library_fines;
DELETE FROM interlibrary_requests;
DELETE FROM book_loans;
DELETE FROM staff_readers; -- Новая таблица
DELETE FROM temporary_readers;
DELETE FROM teacher_readers;
DELETE FROM student_readers;
DELETE FROM library_readers;
DELETE FROM reader_types;
DELETE FROM book_author_relations;
DELETE FROM book_copies;
DELETE FROM book_catalog;
DELETE FROM book_authors;
DELETE FROM library_locations;
-- DELETE FROM custom_user; -- НЕ удаляем пользователей Django

-- 1. Заполнение таблицы категорий читателей (`reader_types`) - без fine_per_day
INSERT INTO reader_types (type_id, type_name, max_books_allowed, loan_period_days, can_use_reading_room, can_use_loan)
VALUES
(1, 'Студент', 7, 21, TRUE, TRUE),
(2, 'Преподаватель', 10, 45, TRUE, TRUE),
(3, 'Сотрудник', 10, 30, TRUE, TRUE),
-- (4, 'Администратор', 15, 60, TRUE, TRUE), -- Убрал, так как нет таблицы admin_readers
(5, 'Обычный читатель', 5, 14, TRUE, TRUE),
(6, 'Слушатель ФПК', 3, 0, TRUE, FALSE),
(7, 'Абитуриент', 3, 0, TRUE, FALSE),
(8, 'Стажер', 5, 0, TRUE, FALSE)
ON DUPLICATE KEY UPDATE
    max_books_allowed=VALUES(max_books_allowed),
    loan_period_days=VALUES(loan_period_days),
    can_use_reading_room=VALUES(can_use_reading_room),
    can_use_loan=VALUES(can_use_loan);

-- 2. Генерация читателей (`library_readers`) - без can_take_books_home, user_id=NULL
SET @reader_num := 100000; -- Начинаем с большого числа для уникальности
INSERT INTO library_readers (
    user_id, -- Устанавливаем в NULL
    reader_type_id, 
    first_name, 
    last_name, 
    middle_name, 
    library_card_number, 
    registration_date, 
    reader_status, 
    suspension_end_date
)
SELECT
    NULL, -- Пользователь не привязан на этом этапе
    CASE FLOOR(1+RAND()*6) -- Адаптировано под меньшее кол-во типов
        WHEN 1 THEN 1 WHEN 2 THEN 2 WHEN 3 THEN 3 WHEN 4 THEN 5 WHEN 5 THEN 6 WHEN 6 THEN 7 ELSE 8
    END,
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
        WHEN RAND() < 0.02 THEN 'expelled' -- Заменено inactive на expelled
        ELSE 'active'
    END,
    CASE WHEN RAND() < 0.03 THEN DATE_ADD(CURDATE(), INTERVAL FLOOR(RAND() * 180) DAY) ELSE NULL END
FROM
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t1,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t2,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t3
LIMIT 5000;

-- 3. Заполнение студентов (`student_readers`) - изменены имена колонок
INSERT INTO student_readers (reader_id, faculty_name, group_number, course_number)
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

-- 4. Заполнение преподавателей (`teacher_readers`) - изменены имена колонок, убрана должность
INSERT INTO teacher_readers (reader_id, department_name, academic_degree, academic_title)
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
    END
FROM library_readers lr
WHERE lr.reader_type_id = 2  -- Тип 'Преподаватель'
LIMIT 1000;

-- 5. Заполнение других сотрудников (`staff_readers`) - НОВАЯ ТАБЛИЦА
INSERT INTO staff_readers (reader_id, department_name, job_position)
SELECT
    lr.reader_id,
    CASE FLOOR(1+RAND()*5)
        WHEN 1 THEN 'Административный отдел'
        WHEN 2 THEN 'Хозяйственный отдел'
        WHEN 3 THEN 'Бухгалтерия'
        WHEN 4 THEN 'Отдел кадров'
        ELSE 'Научно-исследовательский центр'
    END,
    CASE FLOOR(1+RAND()*6)
        WHEN 1 THEN 'Специалист'
        WHEN 2 THEN 'Ведущий специалист'
        WHEN 3 THEN 'Инженер'
        WHEN 4 THEN 'Менеджер'
        WHEN 5 THEN 'Ассистент'
        ELSE 'Секретарь'
    END
FROM library_readers lr
WHERE lr.reader_type_id = 3  -- Тип 'Сотрудник'
LIMIT 300;


-- 6. Заполнение временных читателей (`temporary_readers`) - тип соответствует ENUM
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

-- 7. Заполнение пунктов выдачи (`library_locations`) - тип соответствует ENUM
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

-- 8. Заполнение каталога книг (`book_catalog`) - статус соответствует ENUM
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
        WHEN RAND() < 0.03 THEN 'lost'
        WHEN RAND() < 0.02 THEN 'damaged'
        ELSE 'available'
    END -- Статус 'available' по умолчанию, но генерация добавляет lost/damaged
FROM
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t1,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t2,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t3,
    (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) AS t4
LIMIT 10000;

-- 9. Заполнение авторов (`book_authors`)
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

-- 10. Связь книг и авторов (`book_author_relations`)
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

-- 11. Создание экземпляров книг (`book_copies`) - без cost, статус соответствует ENUM
INSERT INTO book_copies (book_id, location_id, inventory_number, copy_status)
SELECT
    b.book_id,
    FLOOR(1 + RAND() * 9),  -- location_id от 1 до 9
    CONCAT('INV-', LPAD(b.book_id, 5, '0'), '-', copies.n),
    CASE
        WHEN RAND() < 0.85 THEN 'available'
        WHEN RAND() < 0.08 THEN 'issued'
        WHEN RAND() < 0.04 THEN 'damaged'
        ELSE 'lost' -- Заменили written_off на lost
    END
FROM book_catalog b
CROSS JOIN (SELECT 1 AS n UNION SELECT 2 UNION SELECT 3) AS copies;

-- 12. Заполнение выдачи книг (`book_loans`) - статус соответствует ENUM
-- (Вспомогательные таблицы удалены для краткости, логика сохранена)
INSERT INTO book_loans (reader_id, copy_id, location_id, loan_date, due_date, return_date, loan_status)
SELECT
    lr.reader_id,
    bc.copy_id,
    bc.location_id,
    @loan_date := DATE(DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 730) DAY)),
    @due_date := DATE_ADD(@loan_date, INTERVAL rt.loan_period_days DAY),
    @return_date := CASE 
        WHEN RAND() < 0.8 THEN DATE_ADD(@loan_date, INTERVAL FLOOR(RAND() * (rt.loan_period_days + 30)) DAY)
        ELSE NULL 
    END,
    CASE
        WHEN @return_date IS NOT NULL THEN 'returned'
        WHEN @due_date < CURDATE() THEN 'overdue'
        ELSE 'active'
    END
FROM 
    (SELECT lr.reader_id, rt.loan_period_days FROM library_readers lr JOIN reader_types rt ON lr.reader_type_id = rt.type_id WHERE rt.can_use_loan = TRUE ORDER BY RAND() LIMIT 5000) lr,
    (SELECT bc.copy_id, bc.location_id FROM book_copies bc WHERE bc.copy_status = 'available' ORDER BY RAND() LIMIT 10000) bc
WHERE 
    (lr.reader_id + bc.copy_id) % 10 < 7 -- Примерный шанс на выдачу
LIMIT 20000;

-- Обновляем статус копий, которые были выданы
UPDATE book_copies bc
JOIN book_loans bl ON bc.copy_id = bl.copy_id
SET bc.copy_status = 'issued'
WHERE bl.loan_status IN ('active', 'overdue');

-- 13. Межбиблиотечные запросы (`interlibrary_requests`) - убраны лишние поля, статус соответствует ENUM
INSERT INTO interlibrary_requests (reader_id, book_id, request_date, request_status)
SELECT
    lr.reader_id,
    bc.book_id,
    DATE(DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 200) DAY)),
    CASE FLOOR(1+RAND()*4) -- Только 4 статуса в схеме
        WHEN 1 THEN 'pending' WHEN 2 THEN 'approved' WHEN 3 THEN 'received' ELSE 'returned'
    END
FROM 
    library_readers lr
JOIN 
    reader_types rt ON lr.reader_type_id = rt.type_id,
    (SELECT DISTINCT book_id FROM book_catalog ORDER BY RAND() LIMIT 1000) bc
WHERE 
    rt.type_name IN ('Преподаватель', 'Сотрудник') -- Пример: только они могут МБА
    AND (lr.reader_id + bc.book_id) % 10 < 5  -- ~50% шанс
LIMIT 5000;

-- 14. Штрафы (`library_fines`) - без notes, причины и статусы соответствуют ENUM
-- Штрафы за просрочку
INSERT INTO library_fines (reader_id, loan_id, request_id, fine_amount, fine_date, fine_status, fine_reason)
SELECT
    bl.reader_id,
    bl.loan_id,
    NULL,
    -- Используем фиксированный штраф, т.к. fine_per_day убран из reader_types
    ROUND(DATEDIFF(IFNULL(bl.return_date, CURDATE()), bl.due_date) * 10.00 * (0.8 + RAND() * 0.5), 2),
    DATE_ADD(bl.due_date, INTERVAL FLOOR(1+RAND()*5) DAY),
    CASE FLOOR(1+RAND()*3)
        WHEN 1 THEN 'pending' WHEN 2 THEN 'paid' ELSE 'cancelled'
    END,
    'overdue'
FROM 
    book_loans bl
WHERE 
    bl.loan_status = 'overdue' OR (bl.loan_status = 'returned' AND bl.return_date > bl.due_date)
LIMIT 5000;

-- Штрафы за утерю/повреждение (используем cost из book_copies, если он был бы, иначе - фиксированная сумма)
-- Так как cost нет, используем примерную сумму
INSERT INTO library_fines (reader_id, loan_id, request_id, fine_amount, fine_date, fine_status, fine_reason)
SELECT
    bl.reader_id,
    bl.loan_id,
    NULL,
    ROUND(CASE WHEN bc.copy_status = 'lost' THEN 5000 ELSE 500 END * (0.8 + RAND() * 0.4), 2), -- Примерные суммы
    DATE(IFNULL(bl.return_date, CURDATE())),
    CASE FLOOR(1+RAND()*3)
        WHEN 1 THEN 'pending' WHEN 2 THEN 'paid' ELSE 'cancelled'
    END,
    bc.copy_status -- 'lost' или 'damaged'
FROM 
    book_loans bl
JOIN 
    book_copies bc ON bl.copy_id = bc.copy_id
WHERE 
    bc.copy_status IN ('lost', 'damaged')
LIMIT 5000;

-- 15. Регистрация читателей в пунктах (`reader_registrations`)
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
-- Включить проверку внешних ключей
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1; -- Включаем безопасный режим обратно
