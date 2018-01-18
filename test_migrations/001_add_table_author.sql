PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
-- Create new table
CREATE TABLE `author` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL DEFAULT 'John Doe'
);
ALTER TABLE `post`
    ADD COLUMN `author` INTEGER DEFAULT NULL
        REFERENCES author(id);
-- Fixtures
INSERT INTO author VALUES(1,'John Doe');
INSERT INTO author VALUES(2,'Sascha Peilicke');
COMMIT;
