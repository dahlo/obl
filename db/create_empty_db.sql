DROP TABLE IF EXISTS "sound";
CREATE TABLE "sound" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "start" TEXT NOT NULL,
    "end" TEXT NOT NULL,
    "intensity" INTEGER NOT NULL,
    "other" TEXT
);
DROP TABLE IF EXISTS "motion";
CREATE TABLE "motion" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "start" TEXT NOT NULL,
    "end" TEXT NOT NULL,
    "intensity" INTEGER NOT NULL,
    "other" TEXT
);
VACUUM;
