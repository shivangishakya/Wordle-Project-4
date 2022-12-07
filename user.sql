DROP TABLE IF EXISTS "account";

CREATE TABLE "account" (
	"acct_id" VARCHAR(36) NOT NULL,
	"username" TEXT NOT NULL,
	"password" VARCHAR(98) NOT NULL,
	"expire" DATETIME,
	PRIMARY KEY ("acct_id")
);

DROP INDEX IF EXISTS "account_idx";

CREATE INDEX "account_idx" ON "account"("username");