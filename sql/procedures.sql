-- Извлечено из PDF-отчёта

DELIMITER //
CREATE PROCEDURE GetReadersBySpecializationAndOccupation(
IN p_specialization VARCHAR(100),
IN p_occupation VARCHAR(100)
)
BEGIN
IF (p_specialization IS NOT NULL AND NOT EXISTS (
SELECT 1 FROM specializations WHERE specialization_name =
p_specialization
)) THEN
SELECT CONCAT('Ошибка: специальность "',
p_specialization, '" не найдена') AS message;
ELSEIF (p_occupation IS NOT NULL AND NOT EXISTS (
SELECT 1 FROM occupations WHERE occupation_name =
p_occupation
)) THEN
SELECT CONCAT('Ошибка: род занятий "', p_occupation, '"
не найден') AS message;
ELSE
SELECT
r.reader_id,
r.reader_lastname,
r.reader_name,
r.reader_surname,
s.specialization_name,
o.occupation_name
FROM readers r
JOIN specialization_occupation so ON r.characteristic_id
= so.characteristic_id
JOIN specializations s ON so.specialization_id =
s.specialization_id
JOIN occupations o ON so.occupation_id = o.occupation_id
WHERE
(p_specialization IS NULL OR s.specialization_name =
p_specialization)
AND
(p_occupation IS NULL OR o.occupation_name =
p_occupation);
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetReadersWithBook(
IN p_book_name VARCHAR(255)
)
BEGIN
IF NOT EXISTS (SELECT 1 FROM books WHERE book_name =
p_book_name) THEN
SELECT CONCAT('Ошибка: книга "', p_book_name, '" не
найдена') AS message;
ELSE
SELECT
r.reader_id,
r.reader_lastname,
r.reader_name,
r.reader_surname,
b.book_name
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
JOIN readers r ON rt.reader_id = r.reader_id
WHERE b.book_name = p_book_name
AND rt.return_date IS NULL;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetBookRentalHistory(
IN p_book_name VARCHAR(255),
IN p_start_date DATE,
IN p_end_date DATE
)
BEGIN
IF p_start_date > p_end_date THEN
SELECT 'Ошибка: начальная дата должна быть раньше
конечной' AS message;
ELSEIF NOT EXISTS (SELECT 1 FROM books WHERE book_name =
p_book_name) THEN
SELECT CONCAT('Ошибка: книга "', p_book_name, '" не
найдена') AS message;
ELSE
SELECT
r.reader_lastname,
r.reader_name,
r.reader_surname,
b.book_name,
p.publisher_name,
rt.issue_date,
rt.return_date
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
JOIN publishers p ON bc.publisher_id = p.publisher_id
JOIN readers r ON rt.reader_id = r.reader_id
WHERE b.book_name = p_book_name
AND rt.issue_date BETWEEN p_start_date AND p_end_date;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetLibrarianPerformance(
IN p_start_date DATE,
IN p_end_date DATE
)
BEGIN
IF p_start_date > p_end_date THEN
SELECT 'Ошибка: начальная дата должна быть раньше
конечной' AS message;
ELSE
SELECT
l.librarian_id,
l.librarian_lastname,
l.librarian_name,
l.librarian_surname,
COUNT(r.reader_id) AS readers_served
FROM rentals rt
JOIN librarians l ON rt.librarian_id = l.librarian_id
JOIN readers r ON rt.reader_id = r.reader_id
WHERE rt.issue_date BETWEEN p_start_date AND p_end_date
GROUP BY l.librarian_id, l.librarian_lastname,
l.librarian_name, l.librarian_surname
ORDER BY readers_served DESC;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetOverdueReturns()
BEGIN
SELECT
r.reader_id,
r.reader_lastname,
r.reader_name,
r.reader_surname,
b.book_name,
rt.issue_date,
rt.expected_date,
DATEDIFF(CURRENT_DATE, rt.expected_date) AS 'Просрочено
на'
FROM rentals rt
JOIN readers r ON rt.reader_id = r.reader_id
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE rt.return_date IS NULL
AND rt.expected_date < CURRENT_DATE;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetInventoryMovements(
IN p_start_date DATE,
IN p_end_date DATE
)
BEGIN
IF p_start_date > p_end_date THEN
SELECT 'Ошибка: начальная дата должна быть раньше
конечной' AS message;
ELSE
SELECT
b.book_name,
il.action,
il.date,
il.quantity
FROM inventory_logs il
JOIN book_copies bc ON il.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE il.date BETWEEN p_start_date AND p_end_date
ORDER BY il.date DESC;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetLibrarianWorkload(
IN p_librarian_lastname VARCHAR(45),
IN p_start_date DATE,
IN p_end_date DATE
)
BEGIN
DECLARE v_total_days INT DEFAULT DATEDIFF(p_end_date,
p_start_date) + 1;
IF p_start_date > p_end_date THEN
SELECT 'Ошибка: начальная дата должна быть раньше
конечной' AS message;
ELSEIF NOT EXISTS (SELECT 1 FROM librarians WHERE
librarian_lastname = p_librarian_lastname) THEN
SELECT CONCAT('Ошибка: библиотекарь "',
p_librarian_lastname, '" не найден') AS message;
ELSE
SELECT
l.librarian_lastname,
l.librarian_name,
COUNT(*) AS 'Общее количество выдач',
ROUND(COUNT(*) / NULLIF(v_total_days, 0), 2) AS
'Среднее количество выдач в день'
FROM rentals rt
JOIN librarians l ON rt.librarian_id = l.librarian_id
WHERE l.librarian_lastname = p_librarian_lastname
AND rt.issue_date BETWEEN p_start_date AND p_end_date
GROUP BY l.librarian_id, l.librarian_lastname,
l.librarian_name;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetAverageReturnTimeByGenre(
IN p_genre_name VARCHAR(100)
)
BEGIN
IF NOT EXISTS (SELECT 1 FROM genres WHERE genre_name =
p_genre_name) THEN
SELECT CONCAT('Ошибка: жанр "', p_genre_name, '" не
найден') AS message;
ELSE
SELECT
g.genre_name AS 'Жанр',
ROUND(AVG(DATEDIFF(rt.return_date, rt.issue_date)),
1) AS 'Среднее время возврата'
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
JOIN book_genre bg ON b.book_id = bg.book_id
JOIN genres g ON bg.genre_id = g.genre_id
WHERE g.genre_name = p_genre_name
AND rt.return_date IS NOT NULL
GROUP BY g.genre_id, g.genre_name;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetBookFinancials(
IN p_book_name VARCHAR(255)
)
BEGIN
IF NOT EXISTS (SELECT 1 FROM books WHERE book_name =
p_book_name) THEN
SELECT CONCAT('Ошибка: книга "', p_book_name, '" не
найдена') AS message;
ELSE
SELECT
b.book_name,
COUNT(*) AS 'Количество аренд',
ROUND(SUM(b.rental_price_per_day *
DATEDIFF(rt.return_date, rt.issue_date)), 2) AS 'Общий доход от
аренды',
ROUND(SUM(rt.fine_size), 2) AS 'Общая сумма штрафов',
ROUND(SUM(b.rental_price_per_day *
DATEDIFF(rt.return_date, rt.issue_date)) + SUM(rt.fine_size), 2)
AS 'Общий доход'
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE b.book_name = p_book_name
AND rt.return_date IS NOT NULL
GROUP BY b.book_id, b.book_name;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetTopBooks(
IN p_start_date DATE,
IN p_end_date DATE
)
BEGIN
IF p_start_date > p_end_date THEN
SELECT 'Ошибка: начальная дата должна быть раньше
конечной' AS message;
ELSE
SELECT
b.book_name,
COUNT(*) AS 'Количество выдач'
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE rt.issue_date BETWEEN p_start_date AND p_end_date
GROUP BY b.book_id, b.book_name
ORDER BY COUNT(*) DESC
LIMIT 5;
END IF;
END //
DELIMITER ;
