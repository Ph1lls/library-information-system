-- Извлечено из PDF-отчёта

SELECT
r.reader_id,
r.reader_lastname,
r.reader_name,
r.reader_surname,
s.specialization_name,
o.occupation_name
FROM readers r
JOIN specialization_occupation so ON r.characteristic_id =
so.characteristic_id
JOIN specializations s ON so.specialization_id =
s.specialization_id
JOIN occupations o ON so.occupation_id = o.occupation_id
WHERE
('Прикладная информатика' IS NULL OR s.specialization_name =
'Прикладная информатика')
AND
('Студент' IS NULL OR o.occupation_name = 'Студент');

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
WHERE b.book_name = 'Двенадцать стульев'
AND rt.return_date IS NULL;

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
WHERE b.book_name = 'Гарри Поттер и Кубок огня'
AND rt.issue_date BETWEEN '2025-04-01' AND '2025-05-31'
Рисунок 20 – Результат выполнения третьего запроса
Запрос 4. Получить данные о выработке библиотекарей (число обслуженных
читателей в указанный период времени) (период времени – входной параметр).
Основная таблица rentals связывается с librarians для идентификации сотрудников и
с readers для учёта читателей. Фильтр оставляет записи по заданному временному
интервалу. Группировка объединяет данные по каждому библиотекарю. COUNT()
используется для подсчета читателей.
Код запроса представлен в Листинге 4. Результат выполнения данного запроса
показан на рисунке 21.

SELECT
l.librarian_id,
l.librarian_lastname,
l.librarian_name,
l.librarian_surname,
COUNT(r.reader_id)
FROM rentals rt
JOIN librarians l ON rt.librarian_id = l.librarian_id
JOIN readers r ON rt.reader_id = r.reader_id
WHERE rt.issue_date BETWEEN '2025-04-01' AND '2025-04-30'
GROUP BY l.librarian_id, l.librarian_lastname, l.librarian_name,
l.librarian_surname
Рисунок 21 – Результат выполнения четвертого запроса
Запрос 5. Получить список читателей с просроченным сроком литературы.
В основе лежит таблица rentals, которая соединяется с таблицами readers,
book_copies и books. При фильтрации остаются только актуальные просрочки: книги,
которые еще не возвращены и срок возврата которых уже наступил. Функция DATEDIFF
вычисляет количество дней просрочки для каждой книги.
Код запроса представлен в Листинге 5. Результат выполнения данного запроса
показан на рисунке 22.

SELECT
r.reader_id,
r.reader_lastname,
r.reader_name,
r.reader_surname,
b.book_name,
rt.issue_date,
rt.expected_date,
DATEDIFF(CURRENT_DATE, rt.expected_date) AS 'Просрочено на'
FROM rentals rt
JOIN readers r ON rt.reader_id = r.reader_id
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE rt.return_date IS NULL
AND rt.expected_date < CURRENT_DATE
Рисунок 22 – Результат выполнения пятого запроса
Запрос 6. Получить перечень указанной литературы, которая поступила (была
списана) в течение некоторого периода (период времени – входной параметр).
Запрос берет данные inventory_logs, где хранятся записи о всех действиях с книгами.
Чтобы получить не просто номера экземпляров, а конкретные названия книг, запрос
соединяется с таблицей book_copies по полю copy_id, а затем с таблицей книг books по
book_id. Это позволяет получить названия произведений.
При фильтрации остаются только операции за указанный период.
Код запроса представлен в Листинге 6. Результат выполнения данного запроса
показан на рисунке 23.

SELECT
b.book_name,
il.action,
il.date,
il.quantity
FROM inventory_logs il
JOIN book_copies bc ON il.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE il.date BETWEEN '2023-01-01' AND '2025-01-01'
Рисунок 23 – Результат выполнения шестого запроса
Запрос 7. Выдать среднее количество книг, выданных определенным библиотекарем
(библиотекарь – входной параметр).
Основная таблица rentals содержит записи о всех операциях выдачи литературы.
Соединение с таблицей librarians выполняется по полю librarian_id, что позволяет
идентифицировать конкретного сотрудника.
После фильтрации остаются данные по указанному библиотекарю. В вычислении
среднего количества учитывается общее число выдач (COUNT(*)) и продолжительность
периода в днях (DATEDIFF). Функция NULLIF защищает от деления на ноль при пустом
результате.
Код запроса представлен в Листинге 7. Результат выполнения данного запроса
показан на рисунке 24.

SELECT
l.librarian_lastname,
l.librarian_name,
COUNT(*) AS 'Общее количество выдач',
ROUND(COUNT(*) /
NULLIF(DATEDIFF('2025-05-01', '2025-04-15') + 1, 0), 2)
AS 'Среднее количество выдач в день'
FROM rentals rt
JOIN librarians l ON rt.librarian_id = l.librarian_id
WHERE l.librarian_lastname = 'Корженец'
GROUP BY l.librarian_id, l.librarian_lastname, l.librarian_name;

SELECT
g.genre_name AS 'Жанр',
ROUND(AVG(DATEDIFF(rt.return_date, rt.issue_date)), 1) AS
'Среднее время возврата'
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
JOIN book_genre bg ON b.book_id = bg.book_id
JOIN genres g ON bg.genre_id = g.genre_id
WHERE g.genre_name = 'Роман'
AND rt.return_date IS NOT NULL
GROUP BY g.genre_id, g.genre_name;

SELECT
b.book_name,
COUNT(*) AS 'Количество аренд',
ROUND(SUM(b.rental_price_per_day * DATEDIFF(rt.return_date,
rt.issue_date)), 2) AS 'Общий доход от аренды',
ROUND(SUM(rt.fine_size), 2) AS 'Общая сумма штрафов',
ROUND(SUM(b.rental_price_per_day * DATEDIFF(rt.return_date,
rt.issue_date)) + SUM(rt.fine_size), 2) AS 'Общий доход'
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE b.book_name = 'Властелин Колец'
AND rt.return_date IS NOT NULL
GROUP BY b.book_id, b.book_name;

SELECT
b.book_name,
COUNT(*) AS 'Количество выдач'
FROM rentals rt
JOIN book_copies bc ON rt.copy_id = bc.copy_id
JOIN books b ON bc.book_id = b.book_id
WHERE rt.issue_date BETWEEN '2025-02-01' AND '2025-03-01'
GROUP BY b.book_id, b.book_name
ORDER BY COUNT(*) DESC
LIMIT 5;
