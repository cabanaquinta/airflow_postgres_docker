
import pandas as pd
from ingest_data import ingest_callable
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.utils.dates import days_ago

from airflow import DAG

# TODO This should be placed in a .env file and passed to the docker-compose.yaml file environment section
dataset_file = "winequality-red.csv"
user = "root"
password = "root"
host = "localhost"
port = 5432
db = "wine_quality"
name = "winequality_red"
# we download in this location so file is is not deleted when the downloading task finishes
path_to_local_home = '/opt/airflow/'
dataset_url = f"https://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/{dataset_file}"


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="local_ingestion_v1.0",
    schedule_interval="0 6 2 * *",
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    download_dataset_task = BashOperator(
        task_id="download_dataset_task",
        bash_command=f"curl -sS {dataset_url} > {path_to_local_home}/{dataset_file}"
    )

    ingest_task = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest_callable,
        op_kwargs=dict(user=user, password=password, port=port, db=db, table_name=name,
                       csv_name=f'{path_to_local_home}/{dataset_file}')
    )

    # Another way of connecting to postgres using the operator
    # For this we created a connection in Airflow UI first
    # The three tasks next, create a log containing runs
    create_logs_task = PostgresOperator(
        task_id='create_log_task_table',
        postgres_conn_id='postgress_localhost',
        sql="""
            create table if not exists dag_runs (
                dt date,
                dag_id character varying,
                primary key (dt, dag_id)
            )
        """
    )

    # postgres will raise error if we insert twice the same primary key. This is way we delete first, then we insert
    delete_logs_task = PostgresOperator(
        task_id='delete_logs_task',
        postgres_conn_id='postgress_localhost',
        sql="""
            delete from dag_runs where dt = '{{ ds }}' and dag_id =  '{{ dag.dag_id }}';
        """
    )

    insert_logs_task = PostgresOperator(
        task_id='insert_logs_task',
        postgres_conn_id='postgress_localhost',
        sql="""
            insert into dag_runs (dt, dag_id) values ('{{ ds }}', '{{ dag.dag_id }}')
        """
    )

    download_dataset_task >> ingest_task >> create_logs_task >> delete_logs_task >> insert_logs_task
