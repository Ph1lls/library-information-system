-- Извлечено из PDF-отчёта

CREATE USER IF NOT EXISTS 'librarian'@'localhost' IDENTIFIED BY
'librarian123';
GRANT SELECT, INSERT, UPDATE ON library_db.rentals TO
'librarian'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.readers TO
'librarian'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.occupations TO
'librarian'@'localhost';
GRANT SELECT, INSERT, UPDATE ON
library_db.specialization_occupation TO 'librarian'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.specializations TO
'librarian'@'localhost';
GRANT SELECT ON library_db.book_copies TO
'librarian'@'localhost';
GRANT SELECT ON library_db.books TO 'librarian'@'localhost';
GRANT SELECT ON library_db.authors TO 'librarian'@'localhost';
REVOKE DELETE ON library_db.rentals FROM 'librarian'@'localhost';
REVOKE DELETE ON library_db.readers FROM 'librarian'@'localhost';

CREATE USER IF NOT EXISTS 'bibliographer'@'localhost' IDENTIFIED
BY 'bibliographer123';
GRANT SELECT, INSERT, UPDATE ON library_db.books TO
'bibliographer'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.authors TO
'bibliographer'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.book_author TO
'bibliographer'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.publishers TO
'bibliographer'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.genres TO
'bibliographer'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.book_genre TO
'bibliographer'@'localhost';
GRANT SELECT, INSERT, UPDATE ON library_db.book_copies TO
'bibliographer'@'localhost';
REVOKE DELETE ON library_db.books FROM
'bibliographer'@'localhost';
REVOKE DELETE ON library_db.authors FROM
'bibliographer'@'localhost';
REVOKE DELETE ON library_db.book_author FROM
'bibliographer'@'localhost';
REVOKE DELETE ON library_db.publishers FROM
'bibliographer'@'localhost';
REVOKE DELETE ON library_db.genres FROM
'bibliographer'@'localhost';
REVOKE DELETE ON library_db.book_genre FROM
'bibliographer'@'localhost';

CREATE USER IF NOT EXISTS 'director'@'localhost' IDENTIFIED BY
'director123';

GRANT SELECT ON library_db.* TO 'director'@'localhost';
GRANT UPDATE ON library_db.librarians TO 'director'@'localhost';
GRANT UPDATE ON library_db.discounts TO 'director'@'localhost';
GRANT UPDATE ON library_db.discount_occupations TO
'director'@'localhost';
REVOKE DELETE ON library_db.* FROM 'director'@'localhost';

CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY
'admin123';
GRANT ALL PRIVILEGES ON library_db.* TO 'admin'@'localhost';
GRANT GRANT OPTION ON library_db.* TO 'admin'@'localhost';
