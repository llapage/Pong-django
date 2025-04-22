FROM    postgres:latest

COPY    entrypoint.sh /docker-entrypoint-initdb.d/
RUN     mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data && chmod -R 755 /var/lib/postgresql/data

EXPOSE 5432