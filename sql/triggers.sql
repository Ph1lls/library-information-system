-- Извлечено из PDF-отчёта

DELIMITER //
CREATE TRIGGER check_return_date_before_insert
BEFORE INSERT ON rentals
FOR EACH ROW
BEGIN
IF NEW.return_date IS NOT NULL AND NEW.return_date <
NEW.issue_date THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Ошибка: Дата возврата не может быть
раньше даты выдачи';
END IF;
IF NEW.expected_date <= NEW.issue_date THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Ошибка: Ожидаемая дата возврата не
может быть раньше даты выдачи';
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_dates_before_update
BEFORE UPDATE ON rentals
FOR EACH ROW
BEGIN
IF NEW.return_date IS NOT NULL AND NEW.return_date <
NEW.issue_date THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Ошибка: Дата возврата не может быть
раньше даты выдачи';
END IF;
IF NEW.expected_date <= NEW.issue_date THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Ошибка: Ожидаемая дата возврата
должна быть позже даты выдачи';
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_book_status_after_inventory_change
AFTER INSERT ON inventory_logs
FOR EACH ROW
BEGIN
DECLARE total_received INT DEFAULT 0;
DECLARE total_written_off INT DEFAULT 0;
DECLARE total_rented INT DEFAULT 0;
DECLARE available_count INT DEFAULT 0;
SELECT
COALESCE(SUM(CASE WHEN action = 'Поставка' THEN quantity
ELSE 0 END), 0),
COALESCE(SUM(CASE WHEN action = 'Списание' THEN quantity
ELSE 0 END), 0)
INTO total_received, total_written_off
FROM inventory_logs
WHERE copy_id = NEW.copy_id;
IF total_written_off >= total_received THEN
UPDATE book_copies
SET status = 'Списано'
WHERE copy_id = NEW.copy_id;
ELSE
SELECT COUNT(*) INTO total_rented
FROM rentals
WHERE copy_id = NEW.copy_id
AND return_date IS NULL;
SET available_count = (total_received -
total_written_off) - total_rented;
IF available_count <= 0 THEN
UPDATE book_copies
SET status = 'Аренда'
WHERE copy_id = NEW.copy_id;
ELSE
UPDATE book_copies
SET status = 'Доступно'
WHERE copy_id = NEW.copy_id;
END IF;
END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_inventory_before_insert
BEFORE INSERT ON inventory_logs
FOR EACH ROW
BEGIN
DECLARE earliest_delivery_date DATE;
DECLARE total_delivered_before_or_on_date INT DEFAULT 0;
DECLARE total_written_off_before_date INT DEFAULT 0;
DECLARE total_rented INT DEFAULT 0;
DECLARE max_write_off INT DEFAULT 0;
DECLARE error_message VARCHAR(255);
IF NEW.action = 'Списание' THEN
SELECT MIN(date) INTO earliest_delivery_date
FROM inventory_logs
WHERE copy_id = NEW.copy_id AND action = 'Поставка';
IF NEW.date < earliest_delivery_date THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Списание не может быть раньше
первой поставки';
END IF;
SELECT COALESCE(SUM(quantity), 0) INTO
total_delivered_before_or_on_date
FROM inventory_logs
WHERE copy_id = NEW.copy_id AND action = 'Поставка' AND
date <= NEW.date;
SELECT COALESCE(SUM(quantity), 0) INTO
total_written_off_before_date
FROM inventory_logs
WHERE copy_id = NEW.copy_id AND action = 'Списание' AND
date < NEW.date;
SELECT COUNT(*) INTO total_rented
FROM rentals
WHERE copy_id = NEW.copy_id AND return_date IS NULL;
SET max_write_off = total_delivered_before_or_on_date -
total_written_off_before_date - total_rented;
IF NEW.quantity > max_write_off THEN
SET error_message = CONCAT('Недостаточно экземпляров
для списания. Можно списать максимум: ', max_write_off);
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
error_message;
END IF;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER check_rental_before_insert
BEFORE INSERT ON rentals
FOR EACH ROW
BEGIN
DECLARE total_received INT DEFAULT 0;
DECLARE total_written_off INT DEFAULT 0;
DECLARE total_rented INT DEFAULT 0;
DECLARE available_count INT DEFAULT 0;
SELECT
COALESCE(SUM(CASE WHEN action = 'Поставка' THEN quantity
ELSE 0 END), 0),
COALESCE(SUM(CASE WHEN action = 'Списание' THEN quantity
ELSE 0 END), 0)
INTO total_received, total_written_off
FROM inventory_logs
WHERE copy_id = NEW.copy_id;
SELECT COUNT(*) INTO total_rented
FROM rentals
WHERE copy_id = NEW.copy_id AND return_date IS NULL;
SET available_count = (total_received - total_written_off) -
total_rented;
IF available_count <= 0 THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Нет доступных экземпляров для
аренды';
END IF;
IF available_count = 1 THEN
UPDATE book_copies SET status = 'Аренда' WHERE copy_id =
NEW.copy_id;
ELSE
UPDATE book_copies SET status = 'Доступно' WHERE copy_id
= NEW.copy_id;
END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_book_status_after_return
BEFORE UPDATE ON rentals
FOR EACH ROW
BEGIN
IF NEW.return_date IS NOT NULL AND (OLD.return_date IS NULL
OR NEW.return_date <> OLD.return_date) THEN
UPDATE book_copies
SET status = 'Доступно'
WHERE copy_id = NEW.copy_id;
END IF;
END //
DELIMITER ;

DELIMITER//
CREATE TRIGGER calculate_fine_before_update
BEFORE UPDATE ON rentals
FOR EACH ROW
BEGIN
IF NEW.return_date IS NOT NULL AND NEW.return_date >
NEW.expected_date THEN
SET NEW.fine_size = 5 * DATEDIFF(NEW.return_date,
NEW.expected_date);
IF NEW.is_damaged = 1 THEN
DECLARE deposit_amount DECIMAL(10,2);
SELECT deposit_price INTO deposit_amount
FROM books
WHERE book_id = (SELECT book_id FROM book_copies
WHERE copy_id = NEW.copy_id);
SET NEW.fine_size = NEW.fine_size + deposit_amount;
END IF;
END IF;
END //
DELIMITER;

DELIMITER //
CREATE TRIGGER trg_update_inventory_on_damage
AFTER UPDATE ON rentals
FOR EACH ROW
BEGIN
IF NEW.is_damaged = 1 AND (OLD.is_damaged IS NULL OR
OLD.is_damaged != 1) THEN
DECLARE v_book_id INT;
SELECT book_id INTO v_book_id FROM book_copies WHERE
copy_id = NEW.copy_id;
INSERT INTO inventory_logs (copy_id, action, quantity,
date, reason)
VALUES (NEW.copy_id, 'Списание', 1, NEW.return_date,
'Автосписание. Порча');
END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER prevent_duplicate_rental
BEFORE INSERT ON rentals
FOR EACH ROW
BEGIN
DECLARE existing_rental INT;
SELECT COUNT(*) INTO existing_rental FROM rentals
WHERE reader_id = NEW.reader_id
AND copy_id = NEW.copy_id
AND return_date IS NULL;
IF existing_rental > 0 THEN
SIGNAL SQLSTATE '45000'
SET MESSAGE_TEXT = 'Читатель уже арендует этот экземпляр
книги';
END IF;
END//
DELIMITER ;
