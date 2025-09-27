from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="simple_test_dag",
    start_date=pendulum.datetime(2025, 9, 24, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["test"],
) as dag:
    
    # Task 1: Imprime uma mensagem simples no log
    start_task = BashOperator(
        task_id="start_task",
        bash_command="echo 'Iniciando o DAG de teste...'"
    )
    
    # Task 2: Imprime outra mensagem no log
    end_task = BashOperator(
        task_id="end_task",
        bash_command="echo 'DAG de teste finalizado com sucesso!'"
    )
    
    # Define a ordem de execução das tarefas
    start_task >> end_task