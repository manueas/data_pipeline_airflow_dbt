from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import os

# Caminhos dos arquivos
BOOKS_DATA_PATH = "/usr/local/airflow/data_erp/amazon/books/books_data.csv"
BOOKS_RATING_PATH = "/usr/local/airflow/data_erp/amazon/books/Books_rating.csv"

def create_tables():
    """Cria as tabelas necessárias no banco de dados"""
    hook = PostgresHook(postgres_conn_id="dados_dw")
    
    # Criação das tabelas
    with hook.get_conn() as conn:
        with conn.cursor() as cursor:
            # Criar schema se não existir
            cursor.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
            
            # Criar tabela books_data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bronze.books_data (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(500),
                    description TEXT,
                    authors VARCHAR(500),
                    image VARCHAR(500),
                    previewLink VARCHAR(500),
                    publisher VARCHAR(255),
                    publishedDate VARCHAR(50),
                    infoLink VARCHAR(500),
                    categories VARCHAR(255),
                    ratingsCount FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Criar tabela books_rating
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bronze.books_rating (
                    id SERIAL PRIMARY KEY,
                    book_id INTEGER,
                    rating FLOAT,
                    user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()

def load_books_data():
    """Carrega os dados do arquivo books_data.csv"""
    hook = PostgresHook(postgres_conn_id="dados_dw")
    
    # Ler o arquivo CSV em chunks para lidar com arquivos grandes
    chunk_size = 1000
    for chunk in pd.read_csv(BOOKS_DATA_PATH, chunksize=chunk_size):
        # Limpar e preparar os dados
        chunk = chunk.fillna('')  # Substituir NaN por string vazia
        
        with hook.get_conn() as conn:
            # Usar copy_from para inserção mais rápida
            chunk.to_sql(
                'books_data',
                con=conn,
                schema='bronze',
                if_exists='append',
                index=False,
                method='multi'
            )

def load_books_rating():
    """Carrega os dados do arquivo Books_rating.csv"""
    hook = PostgresHook(postgres_conn_id="dados_dw")
    
    # Ler o arquivo CSV em chunks para lidar com arquivos grandes
    chunk_size = 1000
    for chunk in pd.read_csv(BOOKS_RATING_PATH, chunksize=chunk_size):
        # Limpar e preparar os dados
        chunk = chunk.fillna(0)  # Substituir NaN por 0 para campos numéricos
        
        with hook.get_conn() as conn:
            # Usar copy_from para inserção mais rápida
            chunk.to_sql(
                'books_rating',
                con=conn,
                schema='bronze',
                if_exists='append',
                index=False,
                method='multi'
            )

# Configuração da DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'raw_amazon_books_load',
    default_args=default_args,
    description='Carrega dados brutos dos livros da Amazon',
    schedule=None,  # ou '@daily' se quiser executar diariamente
    start_date=datetime(2025, 9, 28),
    catchup=False,
    tags=['raw', 'amazon', 'books'],
) as dag:

    create_tables_task = PythonOperator(
        task_id='create_tables',
        python_callable=create_tables,
    )

    load_books_data_task = PythonOperator(
        task_id='load_books_data',
        python_callable=load_books_data,
    )

    load_books_rating_task = PythonOperator(
        task_id='load_books_rating',
        python_callable=load_books_rating,
    )

    # Definir ordem de execução
    create_tables_task >> [load_books_data_task, load_books_rating_task]
