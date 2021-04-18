CREATE TABLE "journaliste" (
	"id"	INTEGER NOT NULL,
	"prenom"	VARCHAR(50),
	"nom"	VARCHAR(50),
	"email"	VARCHAR(255),
	"password"	TEXT,
	"telephone"	TEXT,
	"ville"	VARCHAR(30),
	"date_creation"	DATETIME,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "article" (
	"id"	INTEGER NOT NULL,
	"id_journaliste"	INTEGER,
	"titre"	TEXT,
	"texte"	TEXT NOT NULL,
	"lien"	TEXT,
	"date_publication"	DATETIME,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("id_journaliste") REFERENCES "journaliste"("id")
);
