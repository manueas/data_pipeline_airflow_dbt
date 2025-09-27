# dags/test_dag.py
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def test_function():
    print("DAG está funcionando!")
    return "Sucesso"

with DAG(
    dag_id="test_dag",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:
    
    test_task = PythonOperator(
        task_id="test_task",
        python_callable=test_function,
    )