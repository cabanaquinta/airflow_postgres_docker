# docker_airflow_postgres

Tutorial on how to run Airflow locally and establish GCP authentication using the local posgres container

## Start Airflow

```bash
cd airflow
```

```bash
docker build . --tag extending_airflow_2:latest
```

```bash
docker-compose up airflow-init
```

```bash
docker-compose up -d
```

## Start postgres

```bash
cd postgres
```

```bash
docker compose up -d
```

## Check postgres DB works

```bash
pgcli 'postgresql://root:root@localhost:5432/wine_quality'
pgcli -h localhost -p 5432 -d wine_quality
```

## Check Airflow connection with Postgres

```bash
docker exec -it <container id> bash
```

```bash
python
```

```bash
python
from sqlalchemy import create_engine
engine = create_engine('postgresql://root:root@pgdatabase:5432/ny_taxi')
engine.connect()
```
