-- -- -- -- -- -- -- -- -- -- -- -- -- comment -- -- -- -- -- -- -- -- -- -- -- -- --

-- This script is used to create word.db table which will store words

-- Running this script: sqlite3 word.db < word.sql

-- -- -- -- -- -- -- -- -- -- -- -- -- table -- -- -- -- -- -- -- -- -- -- -- -- --

DROP TABLE IF EXISTS "wordle_word";

CREATE TABLE "wordle_word" (
	"word" TEXT NOT NULL,
	"valid" INTEGER NOT NULL
);

INSERT INTO "wordle_word"
	("word", "valid")
SELECT
	"value" as "word", 0 as "valid"
FROM json_each(readfile('correct.json'));

INSERT INTO "wordle_word"
	("word", "valid")
SELECT
	"value" as "word", 1 as "valid"
FROM json_each(readfile('valid.json'));

-- -- -- -- -- -- -- -- -- -- -- -- -- index -- -- -- -- -- -- -- -- -- -- -- -- --

DROP INDEX IF EXISTS "wordle_word_word_idx";

CREATE INDEX "wordle_word_word_idx" ON "wordle_word"("word");

DROP INDEX IF EXISTS "wordle_word_valid_idx";

CREATE INDEX "wordle_word_valid_idx" ON "wordle_word"("valid");