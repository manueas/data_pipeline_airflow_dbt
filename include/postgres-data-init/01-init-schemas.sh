#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Criar schema bronze
    CREATE SCHEMA IF NOT EXISTS bronze;
    GRANT ALL PRIVILEGES ON SCHEMA bronze TO $POSTGRES_USER;

    -- Criar schema prata
    CREATE SCHEMA IF NOT EXISTS prata;
    GRANT ALL PRIVILEGES ON SCHEMA prata TO $POSTGRES_USER;

    -- Criar schema ouro
    CREATE SCHEMA IF NOT EXISTS ouro;
    GRANT ALL PRIVILEGES ON SCHEMA ouro TO $POSTGRES_USER;
EOSQL