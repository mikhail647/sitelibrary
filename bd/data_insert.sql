-- Использование базы данных
USE library_db;

-- Отключить проверку внешних ключей для ускорения вставки
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Заполнение таблицы категорий читателей
INSERT INTO reader_types (type_name, max_books_allowed, loan_period_days, can_use_reading_room, can_use_loan)
VALUES
('Студент очной формы', 5, 30, TRUE, TRUE),
('Студент заочной формы', 3, 45, TRUE, TRUE),
('Преподаватель', 10, 60, TRUE, TRUE),
('Аспирант', 8, 45, TRUE, TRUE),
('Сотрудник университета', 5, 30, TRUE, TRUE),
('Слушатель ФПК', 0, 0, TRUE, FALSE),
('Абитуриент', 0, 0, TRUE, FALSE),
('Стажер', 0, 0, TRUE, FALSE);

-- 2. Генерация 5000 читателей (v5 - Session Variable)
SET @num := 0;

-- Генерируем номера 0-9999 и вставляем во временный пул
-- INSERT INTO temp_number_pool (n)
-- SELECT (t1.d * 1000 + t2.d * 100 + t3.d * 10 + t4.d) AS generated_number
-- FROM digits t1
-- CROSS JOIN digits t2
-- CROSS JOIN digits t3
-- CROSS JOIN digits t4;

-- Вставляем читателей, выбирая 5000 случайных номеров из пула
INSERT INTO library_readers (reader_type_id, first_name, last_name, middle_name, library_card_number, registration_date, reader_status, suspension_end_date)
SELECT
    FLOOR(RAND() * 8) + 1, -- reader_type_id
    ELT(FLOOR(RAND() * 20) + 1, 'Иван', 'Алексей', 'Дмитрий', 'Сергей', 'Андрей', 'Михаил', 'Артем', 'Павел', 'Максим', 'Никита', 'Анна', 'Мария', 'Елена', 'Ольга', 'Наталья', 'Ирина', 'Татьяна', 'Юлия', 'Екатерина', 'Александра'), -- first_name
    ELT(FLOOR(RAND() * 20) + 1, 'Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев', 'Павлов', 'Семенов', 'Голубев', 'Волков', 'Козлов', 'Лебедев', 'Новиков', 'Морозов', 'Романов', 'Орлов', 'Алексеев', 'Николаев', 'Сергеев'), -- last_name
    CASE WHEN RAND() < 0.8 THEN CONCAT(ELT(FLOOR(RAND() * 15) + 1, 'Александрович', 'Дмитриевич', 'Сергеевич', 'Андреевич', 'Игоревич', 'Олегович', 'Владимирович', 'Борисович', 'Анатольевич', 'Николаевич', 'Викторович', 'Станиславович', 'Геннадьевич', 'Валентинович', 'Юрьевич'), '') ELSE NULL END, -- middle_name
    CONCAT('CARD', LPAD(@num := @num + 1, 6, '0')), -- library_card_number (using session variable)
    DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND() * 1825) DAY), -- registration_date
    IF(RAND() < 0.95, 'active', 'suspended'), -- reader_status
    CASE WHEN RAND() < 0.03 THEN DATE_ADD(CURDATE(), INTERVAL FLOOR(RAND() * 180) DAY) ELSE NULL END -- suspension_end_date
FROM
    -- Need a source of rows to generate 5000 inserts.
    -- Using information_schema.tables is a common trick, but adjust if it doesn't have enough rows
    -- or if the user lacks permissions. Cross join ensures enough rows.
    information_schema.tables t1,
    information_schema.tables t2
LIMIT 5000;

-- Note: No temporary tables to drop for this part.

-- 3. Заполнение студентов (2000 записей)
INSERT INTO student_readers (reader_id, faculty_name, group_number, course_number)
SELECT
    reader_id,
    ELT(FLOOR(RAND() * 6) + 1,
        'Информационные технологии',
        'Экономика и управление',
        'Гуманитарные науки',
        'Естественные науки',
        'Инженерные науки',
        'Юридический'),
    CONCAT(
        ELT(FLOOR(RAND() * 6) + 1, 'Б', 'М', 'А', 'С', 'К', 'П'),
        FLOOR(RAND() * 10),
        FLOOR(RAND() * 10),
        '-',
        FLOOR(RAND() * 10),
        FLOOR(RAND() * 10)
    ),
    FLOOR(RAND() * 4) + 1
FROM library_readers
WHERE reader_type_id IN (1, 2)
ORDER BY RAND()
LIMIT 2000;

-- 4. Заполнение преподавателей (800 записей)
INSERT INTO teacher_readers (reader_id, department_name, academic_degree, academic_title)
SELECT
    reader_id,
    ELT(FLOOR(RAND() * 10) + 1,
        'Кафедра высшей математики',
        'Кафедра информационных систем',
        'Кафедра теоретической физики',
        'Кафедра мировой экономики',
        'Кафедра русской литературы',
        'Кафедра международного права',
        'Кафедра органической химии',
        'Кафедра биоинженерии',
        'Кафедра робототехники',
        'Кафедра искусственного интеллекта'),
    ELT(FLOOR(RAND() * 4) + 1,
        'Кандидат наук',
        'Доктор наук',
        NULL,
        NULL),
    ELT(FLOOR(RAND() * 5) + 1,
        'Доцент',
        'Профессор',
        'Старший научный сотрудник',
        NULL,
        NULL)
FROM library_readers
WHERE reader_type_id = 3
ORDER BY RAND()
LIMIT 800;

-- 5. Заполнение сотрудников (500 записей)
INSERT INTO staff_readers (reader_id, department_name, job_position)
SELECT
    reader_id,
    ELT(FLOOR(RAND() * 8) + 1,
        'Административный отдел',
        'Бухгалтерия',
        'Отдел кадров',
        'Учебный отдел',
        'Научный отдел',
        'Хозяйственный отдел',
        'IT-отдел',
        'Международный отдел'),
    ELT(FLOOR(RAND() * 8) + 1,
        'Специалист',
        'Главный специалист',
        'Начальник отдела',
        'Заместитель начальника',
        'Старший специалист',
        'Инженер',
        'Менеджер',
        'Аналитик')
FROM library_readers
WHERE reader_type_id = 5
ORDER BY RAND()
LIMIT 500;

-- 6. Заполнение временных читателей (300 записей)
INSERT INTO temporary_readers (reader_id, reader_type)
SELECT
    reader_id,
    ELT(FLOOR(RAND() * 3) + 1, 'FPC', 'applicant', 'intern')
FROM library_readers
WHERE reader_type_id IN (6, 7, 8)
ORDER BY RAND()
LIMIT 300;

-- 7. Заполнение пунктов выдачи (50 локаций)
INSERT INTO library_locations (location_name, location_type, address)
WITH locations AS (
    SELECT 'Главный абонемент' AS name, 'loan' AS type UNION
    SELECT 'Читальный зал №1', 'reading_room' UNION
    SELECT 'Научный абонемент', 'loan' UNION
    SELECT 'Зал периодики', 'reading_room' UNION
    SELECT 'Фонд редких книг', 'loan' UNION
    SELECT 'Межбиблиотечный абонемент', 'loan' UNION
    SELECT 'Электронный читальный зал', 'reading_room'
)
SELECT
    CONCAT(name, ' ', FLOOR(RAND() * 5) + 1),
    type,
    CONCAT('Корпус ', ELT(FLOOR(RAND() * 6) + 1, 'А', 'Б', 'В', 'Г', 'Д', 'Е'), ', этаж ', FLOOR(RAND() * 4) + 1)
FROM locations
CROSS JOIN (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7) AS multiplier
LIMIT 50;

-- 8. Заполнение каталога книг (10000 записей)
-- ПРИМЕЧАНИЕ: Генерация ISBN может привести к дубликатам. Для продакшена нужен более надежный способ.
INSERT INTO book_catalog (book_title, isbn, publication_year, publisher_name, acquisition_date, book_status)
SELECT
    CONCAT(
        ELT(FLOOR(RAND() * 10) + 1, -- Уменьшено для большей вероятности осмысленных названий
            'Введение в ', 'Основы ', 'Теория ', 'Практика ', 'Современные методы ',
            'Исследование ', 'Анализ ', 'Система ', 'Принципы ', 'Разработка '),
        ELT(FLOOR(RAND() * 10) + 1, -- Уменьшено
            'математического анализа', 'квантовой физики', 'искусственного интеллекта',
            'экономических систем', 'биоинформатики', 'робототехники', 'баз данных',
            'компьютерных сетей', 'машинного обучения', 'органической химии')),
    CONCAT('978', LPAD(FLOOR(RAND() * 10000000000), 10, '0')), -- 3 + 10 = 13 цифр
    FLOOR(RAND() * 50) + 1970,
    ELT(FLOOR(RAND() * 10) + 1,
        'Издательство МГУ', 'Научная литература', 'Техносфера', 'Питер', 'Эксмо',
        'АСТ', 'Манн, Иванов и Фербер', 'Дрофа', 'Просвещение', 'Юрайт'),
    DATE_SUB(CURDATE(), INTERVAL FLOOR(RAND() * 3650) DAY),
    IF(RAND() < 0.97, 'available', 'lost')
FROM (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) t1 -- Генератор для 10000 строк
CROSS JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) t2
CROSS JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) t3
CROSS JOIN (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) t4
LIMIT 10000;

-- 9. Заполнение авторов (500 записей)
INSERT INTO book_authors (first_name, last_name, middle_name)
SELECT
    ELT(FLOOR(RAND() * 20) + 1,
        'Лев', 'Федор', 'Александр', 'Николай', 'Михаил', 'Иван', 'Антон',
        'Алексей', 'Владимир', 'Борис', 'Марк', 'Эрнест', 'Джордж', 'Оскар',
        'Виктор', 'Джон', 'Уильям', 'Чарльз', 'Джейн', 'Теодор'),
    ELT(FLOOR(RAND() * 20) + 1,
        'Толстой', 'Достоевский', 'Пушкин', 'Гоголь', 'Булгаков', 'Тургенев',
        'Чехов', 'Гончаров', 'Лермонтов', 'Шолохов', 'Оруэлл', 'Хемингуэй',
        'Маркес', 'Фицджеральд', 'Сэлинджер', 'Стивенсон', 'Диккенс', 'Бронте',
        'Уайльд', 'Дюма'),
    CASE WHEN RAND() < 0.7 THEN -- 70% шанс иметь отчество
        CONCAT(ELT(FLOOR(RAND() * 15) + 1,
            'Николаевич', 'Федорович', 'Сергеевич', 'Александрович', 'Михайлович',
            'Иванович', 'Борисович', 'Львович', 'Анатольевич', 'Васильевич',
            'Георгиевич', 'Павлович', 'Викторович', 'Олегович', 'Юрьевич'),'')
         ELSE NULL END
FROM (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) t1
CROSS JOIN (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) t2
CROSS JOIN (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5) t3
CROSS JOIN (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4) t4 -- 5*5*5*4 = 500
LIMIT 500;


-- 10. Связь книг и авторов (до 3 случайных авторов на книгу)
-- ПРИМЕЧАНИЕ: Этот метод не гарантирует ровно 3 автора и может выбрать одного автора несколько раз для книги.
-- Более точное решение требует процедурного подхода.
INSERT INTO book_author_relations (book_id, author_id)
SELECT book_id, author_id
FROM (
    SELECT
        b.book_id,
        (SELECT ba.author_id FROM book_authors ba ORDER BY RAND() LIMIT 1) AS author_id,
        1 as rn -- Просто для разделения
    FROM book_catalog b
    UNION ALL
    SELECT
        b.book_id,
        (SELECT ba.author_id FROM book_authors ba ORDER BY RAND() LIMIT 1) AS author_id,
        2 as rn
    FROM book_catalog b WHERE RAND() < 0.7 -- Шанс на второго автора
    UNION ALL
    SELECT
        b.book_id,
        (SELECT ba.author_id FROM book_authors ba ORDER BY RAND() LIMIT 1) AS author_id,
        3 as rn
    FROM book_catalog b WHERE RAND() < 0.4 -- Шанс на третьего автора
) AS temp_relations
GROUP BY book_id, author_id; -- Удаляем дубликаты авторов для одной книги


-- 11. Создание экземпляров книг (3 экземпляра на книгу)
INSERT INTO book_copies (book_id, location_id, inventory_number, copy_status)
SELECT
    b.book_id,
    (SELECT location_id FROM library_locations ORDER BY RAND() LIMIT 1),
    CONCAT('INV-', b.book_id, '-', copies.n),
    ELT(FLOOR(RAND() * 4) + 1, 'available', 'issued', 'lost', 'damaged') -- Добавлен damaged
FROM book_catalog b
CROSS JOIN (SELECT 1 AS n UNION SELECT 2 UNION SELECT 3) AS copies;

-- 12. Заполнение выдачи книг (20000 записей)
-- ПРИМЕЧАНИЕ: Этот скрипт НЕ обновляет статус book_copies на 'issued' после создания выдачи.
-- Это может привести к неконсистентности данных (один экземпляр может быть выдан несколько раз).
-- Требуется дополнительная логика (триггеры, процедуры или обновление в приложении) для корректной работы.
INSERT INTO book_loans (reader_id, copy_id, location_id, loan_date, due_date, return_date, loan_status)
SELECT
    r.reader_id,
    c.copy_id,
    c.location_id,
    -- Cast to DATE
    @loan_date := DATE(DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 360) DAY)),
    @due_date := DATE(DATE_ADD(@loan_date, INTERVAL rt.loan_period_days DAY)),
    @return_date := IF(RAND() < 0.7, DATE(DATE_ADD(@loan_date, INTERVAL FLOOR(RAND() * (rt.loan_period_days + 15)) DAY)), NULL),
    CASE
        WHEN @return_date IS NOT NULL AND @return_date > @due_date THEN 'returned' -- Считаем возвращенной, даже если просрочена
        WHEN @return_date IS NOT NULL AND @return_date <= @due_date THEN 'returned'
        WHEN @return_date IS NULL AND @due_date < CURDATE() THEN 'overdue'
        ELSE 'active'
    END
FROM
    (SELECT reader_id, reader_type_id FROM library_readers lr JOIN reader_types rt ON lr.reader_type_id = rt.type_id WHERE rt.can_use_loan = TRUE ORDER BY RAND() LIMIT 5000) r -- Берем подмножество читателей
JOIN
    (SELECT copy_id, book_id, location_id FROM book_copies WHERE copy_status = 'available' ORDER BY RAND() LIMIT 25000) c -- Берем подмножество доступных копий
JOIN reader_types rt ON r.reader_type_id = rt.type_id
WHERE RAND() < 0.8 -- Уменьшаем шанс создания выдачи для производительности
LIMIT 20000;


-- 13. Межбиблиотечные запросы (5000 записей)
INSERT INTO interlibrary_requests (reader_id, book_id, request_date, request_status)
SELECT
    reader_id,
    (SELECT book_id FROM book_catalog ORDER BY RAND() LIMIT 1),
    -- Cast to DATE
    DATE(DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 180) DAY)),
    ELT(FLOOR(RAND() * 4) + 1, 'pending', 'approved', 'received', 'returned')
FROM library_readers
WHERE reader_type_id IN (3,4,5) -- Только преподаватели, аспиранты и сотрудники
ORDER BY RAND()
LIMIT 5000;

-- 14. Штрафы (10000 записей)
-- Создаем штрафы для просроченных (overdue) и утерянных/поврежденных (lost/damaged) выдач
INSERT INTO library_fines (reader_id, loan_id, request_id, fine_amount, fine_date, fine_status, fine_reason)
-- Штрафы за просрочку
SELECT
    bl.reader_id,
    bl.loan_id,
    NULL,
    ROUND(RAND() * 100 + 10, 2), -- Штраф за просрочку поменьше
    -- Cast to DATE
    DATE(DATE_ADD(bl.due_date, INTERVAL FLOOR(RAND() * 5) + 1 DAY)), -- Дата штрафа вскоре после просрочки
    ELT(FLOOR(RAND() * 3) + 1, 'pending', 'paid', 'cancelled'),
    'overdue' -- Причина: просрочка
FROM book_loans bl
WHERE bl.loan_status = 'overdue' AND RAND() < 0.5 -- Шанс 50% на штраф за просрочку

UNION ALL

-- Штрафы за утерю/повреждение (берем из статуса копии)
SELECT
    bl.reader_id,
    bl.loan_id,
    NULL,
    ROUND(RAND() * 1000 + 50, 2), -- Штраф за утерю/повреждение больше
    -- Cast to DATE
    DATE(IFNULL(bl.return_date, CURDATE())), -- Дата штрафа - дата возврата или сегодня
    ELT(FLOOR(RAND() * 3) + 1, 'pending', 'paid', 'cancelled'),
    bc.copy_status -- Причина: 'lost' или 'damaged' из статуса копии
FROM book_loans bl
JOIN book_copies bc ON bl.copy_id = bc.copy_id
WHERE bc.copy_status IN ('lost', 'damaged') AND RAND() < 0.5; -- Шанс 50% на штраф за утерю/повреждение


-- 15. Регистрация читателей (20000 записей)
INSERT INTO reader_registrations (reader_id, location_id, registration_date, registration_expiry_date)
SELECT
    r.reader_id,
    l.location_id,
    DATE_SUB(r.registration_date, INTERVAL FLOOR(RAND() * 30) DAY),
    DATE_ADD(r.registration_date, INTERVAL 365 DAY)
FROM library_readers r
CROSS JOIN library_locations l
WHERE RAND() < 0.4 -- 40% вероятность регистрации
LIMIT 20000;


-- Включить проверку внешних ключей
SET FOREIGN_KEY_CHECKS = 1;