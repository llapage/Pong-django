sleep 5

PG_HBA_FILE="/var/lib/postgresql/data/pg_hba.conf"

while [ ! -f $PG_HBA_FILE ]; do
  echo "Waiting for pg_hba.conf to be created..."
  sleep 1
done

# Ensure PostgreSQL is accepting remote connections
if ! grep -q "0.0.0.0/0" "$PG_HBA_FILE"; then
  echo "host    all             all             0.0.0.0/0            md5" >> "$PG_HBA_FILE"
  echo "Added 0.0.0.0/0 to pg_hba.conf"
fi

if ! grep -q "::1/128" "$PG_HBA_FILE"; then
  echo "host    all             all             ::1/128               md5" >> "$PG_HBA_FILE"
  echo "Added ::1/128 to pg_hba.conf"
fi

until pg_isready -U postgres; do
  echo "Waiting for Postgres to be ready... (pg_isready check)"
  sleep 1
done

psql -c "SET timezone = 'UTC';"

# Create the database if it doesn't exist
echo "Creating database $DB..."
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='$DB'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE $DB OWNER $POSTGRES_USER;"

# Create the user and set password if it doesn't exist
echo "Creating user $POSTGRES_USER..."
psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='$POSTGRES_USER'" | grep -q 1 || psql -U postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$DB_PASSWORD';"

# Grant privileges to the user on the database
echo "Granting privileges to $POSTGRES_USER on database $DB..."
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB TO $POSTGRES_USER;"

# Execute the original command
exec "$@"
