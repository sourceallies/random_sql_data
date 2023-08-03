FROM postgres:14.7-alpine3.17 as dumper

COPY data/random_data_0_tables.sql /docker-entrypoint-initdb.d/
COPY data/random_data_1_customers.sql /docker-entrypoint-initdb.d/
COPY data/random_data_2_products.sql /docker-entrypoint-initdb.d/
COPY data/random_data_3_stores.sql /docker-entrypoint-initdb.d/
COPY data/random_data_4_orders.sql /docker-entrypoint-initdb.d/

RUN ["sed", "-i", "s/exec \"$@\"/echo \"skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]

ENV POSTGRES_DB=random_data
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=pass
ENV PGDATA=/data

RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres", "-c",  "log_statement=none"]

# final stage
FROM postgres:14.7-alpine3.17

COPY --from=dumper /data $PGDATA
