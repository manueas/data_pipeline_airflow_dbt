# dags/test_dbt_connection.py

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import logging

def test_postgres_connection():
    """Testa a conexão com o PostgreSQL"""
    try:
        hook = PostgresHook(postgres_conn_id="airflow_db")
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        logging.info(f"PostgreSQL version: {result[0]}")
        cursor.close()
        conn.close()
        return "Conexão PostgreSQL bem-sucedida!"
    except Exception as e:
        logging.error(f"Erro na conexão PostgreSQL: {e}")
        raise

def test_dbt_project_structure():
    """Testa se a estrutura do projeto dbt está acessível"""
    import os
    dbt_path = "/opt/airflow/dbt_project"
    
    if os.path.exists(dbt_path):
        files = os.listdir(dbt_path)
        logging.info(f"Arquivos em dbt_project: {files}")
        return f"Estrutura dbt encontrada: {files}"
    else:
        raise Exception(f"Pasta dbt_project não encontrada em: {dbt_path}")

with DAG(
    dag_id="test_dbt_environment",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["test"],
) as dag:
    
    test_postgres = PythonOperator(
        task_id="test_postgres_connection",
        python_callable=test_postgres_connection,
    )
    
    test_dbt_structure = PythonOperator(
        task_id="test_dbt_structure",
        python_callable=test_dbt_project_structure,
    )
    
    test_postgres >> test_dbt_structure