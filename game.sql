-- -- -- -- -- -- -- -- -- -- -- -- -- table -- -- -- -- -- -- -- -- -- -- -- -- --

DROP TABLE IF EXISTS "wordle_guess";
DROP TABLE IF EXISTS "wordle_game";

CREATE TABLE "wordle_game" (
	"game_id" VARCHAR(36) NOT NULL,
	"username" TEXT NOT NULL,
	"word" TEXT NOT NULL,
	PRIMARY KEY ("game_id")
);

CREATE TABLE "wordle_guess" (
	"game_id" VARCHAR(36) NOT NULL,
	"order" BIGINT NOT NULL,
	"word" TEXT NOT NULL,
	PRIMARY KEY ("game_id", "order"),
	FOREIGN KEY ("game_id") REFERENCES "wordle_game" ("game_id") ON DELETE CASCADE
);

-- -- -- -- -- -- -- -- -- -- -- -- -- index -- -- -- -- -- -- -- -- -- -- -- -- --

DROP INDEX IF EXISTS "wordle_game_idx";

CREATE INDEX "wordle_game_idx" ON "wordle_game"("username");
