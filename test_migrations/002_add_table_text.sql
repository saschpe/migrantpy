PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- Create new table
CREATE TABLE `text` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`text`	TEXT NOT NULL DEFAULT 'Bla',
	`author` INTEGER,
	FOREIGN KEY(author) REFERENCES author(id)
);
-- Fixtures
INSERT INTO text VALUES(1,'Some dummy text', 1);
INSERT INTO text VALUES(2,'Another fancy text', 2);
COMMIT;
