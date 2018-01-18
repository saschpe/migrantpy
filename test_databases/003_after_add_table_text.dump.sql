PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE `post` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`title`	TEXT NOT NULL,
	`body`	TEXT NOT NULL,
	`created_at`	INTEGER DEFAULT CURRENT_TIMESTAMP,
	`updated_at`	INTEGER DEFAULT CURRENT_TIMESTAMP
, `author` INTEGER DEFAULT NULL
        REFERENCES author(id));
INSERT INTO post VALUES(1,'Hello World','This is the first blog post!','2016-12-22 08:32:08','2016-12-22 08:32:08',NULL);
INSERT INTO post VALUES(2,'Again','Another blog post','2016-12-22 08:32:22','2016-12-22 08:32:22',NULL);
INSERT INTO post VALUES(3,'Migrant rocks!','Check it out...','2016-12-22 08:32:43','2016-12-22 08:32:43',NULL);
CREATE TABLE `author` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT NOT NULL DEFAULT 'John Doe'
);
INSERT INTO author VALUES(1,'John Doe');
INSERT INTO author VALUES(2,'Sascha Peilicke');
CREATE TABLE `text` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`text`	TEXT NOT NULL DEFAULT 'Bla',
	`author` INTEGER,
	FOREIGN KEY(author) REFERENCES author(id)
);
INSERT INTO text VALUES(1,'Some dummy text',1);
INSERT INTO text VALUES(2,'Another fancy text',2);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('post',3);
INSERT INTO sqlite_sequence VALUES('author',2);
INSERT INTO sqlite_sequence VALUES('text',2);
COMMIT;
