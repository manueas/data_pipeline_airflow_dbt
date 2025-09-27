# etl/conexao/data_source.py

import psycopg2
import psycopg2.extras # Usado para retornar dicionários

class PostgresDB:
    """
    Uma classe para interagir com um banco de dados PostgreSQL,
    facilitando operações de CRUD.
    """
    def __init__(self, dbname, user, password, host='localhost', port='5432', schema='public'):
        """
        Inicializa a conexão com o banco de dados.
        :param schema: Schema padrão para as operações (default: 'public')
        """
        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.schema = schema
        self.connection = None
        self.cursor = None

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            # Desconecta se já houver uma conexão ativa
            if self.connection:
                self.disconnect()
            
            self.connection = psycopg2.connect(**self.conn_params)
            # cursor_factory=psycopg2.extras.DictCursor faz com que os selects retornem dicionários
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("Conexão com o PostgreSQL bem-sucedida!")
        except psycopg2.OperationalError as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            raise

    def disconnect(self):
        """Fecha a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Conexão com o PostgreSQL fechada.")

    def __enter__(self):
        """Inicia o gerenciador de contexto, estabelecendo a conexão."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finaliza o gerenciador de contexto, fechando a conexão."""
        self.disconnect()

    def execute_query(self, query, params=None, schema=None):
        """
        Executa uma consulta genérica com suporte a schema.
        """
        if schema:
            query = f"SET search_path TO {schema}; {query}"
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.rowcount
        except psycopg2.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            self.connection.rollback()
            return None

    def fetch_query(self, query, params=None):
        """
        Executa uma consulta de seleção (SELECT) e retorna os resultados.
        """
        try:
            self.cursor.execute(query, params or ())
            # Converte as linhas do resultado (DictRow) para dicionários padrão
            result = [dict(row) for row in self.cursor.fetchall()]
            return result
        except psycopg2.Error as e:
            print(f"Erro ao buscar dados: {e}")
            return None

    # --- Métodos CRUD ---

    def create(self, table, data):
        """
        Insere um novo registro em uma tabela (CREATE).
        :param table: Nome da tabela.
        :param data: Dicionário com {nome_da_coluna: valor}.
        :return: O ID do novo registro inserido ou None em caso de falha.
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        
        try:
            self.cursor.execute(query, tuple(data.values()))
            inserted_id = self.cursor.fetchone()[0]
            self.connection.commit()
            print(f"Registro inserido com sucesso na tabela '{table}' com ID: {inserted_id}")
            return inserted_id
        except psycopg2.Error as e:
            print(f"Erro ao inserir registro: {e}")
            self.connection.rollback()
            return None

    def read(self, table, where=None, params=None, columns='*'):
        """
        Lê registros de uma tabela (READ).
        :param table: Nome da tabela.
        :param where: Condição WHERE (ex: "id = %s AND nome = %s").
        :param params: Tupla de parâmetros para a condição WHERE.
        :param columns: Colunas a serem selecionadas (string, ex: "id, nome").
        :return: Lista de dicionários representando os registros.
        """
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        return self.fetch_query(query, params)

    def update(self, table, data, where, params):
        """
        Atualiza registros em uma tabela (UPDATE).
        :param table: Nome da tabela.
        :param data: Dicionário com {coluna_a_atualizar: novo_valor}.
        :param where: Condição WHERE (ex: "id = %s").
        :param params: Tupla de parâmetros para a condição WHERE.
        :return: Número de linhas atualizadas ou None em caso de falha.
        """
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        # Concatena os valores do SET com os valores do WHERE
        all_params = tuple(data.values()) + params
        
        updated_rows = self.execute_query(query, all_params)
        if updated_rows is not None:
             print(f"{updated_rows} registro(s) atualizado(s) com sucesso na tabela '{table}'.")
        return updated_rows


    def delete(self, table, where, params):
        """
        Deleta registros de uma tabela (DELETE).
        :param table: Nome da tabela.
        :param where: Condição WHERE (ex: "id = %s").
        :param params: Tupla de parâmetros para a condição WHERE.
        :return: Número de linhas deletadas ou None em caso de falha.
        """
        query = f"DELETE FROM {table} WHERE {where}"
        deleted_rows = self.execute_query(query, params)
        if deleted_rows is not None:
            print(f"{deleted_rows} registro(s) deletado(s) com sucesso da tabela '{table}'.")
        return deleted_rows

    def upsert(self, table, data, conflict_columns, schema=None):
        """
        Realiza upsert (INSERT ... ON CONFLICT DO UPDATE)
        """
        schema = schema or self.schema
        columns = data.keys()
        values = data.values()
        
        update_set = ', '.join([f"{col} = EXCLUDED.{col}" 
                               for col in columns 
                               if col not in conflict_columns])
        
        conflict_cols = ', '.join(conflict_columns)
        
        query = f"""
            INSERT INTO {schema}.{table} ({', '.join(columns)})
            VALUES ({', '.join(['%s'] * len(columns))})
            ON CONFLICT ({conflict_cols})
            DO UPDATE SET {update_set}
        """
        return self.execute_query(query, tuple(values))

    def bulk_insert(self, table, columns, values, schema=None):
        """
        Realiza inserção em lote para melhor performance.
        :param table: Nome da tabela
        :param columns: Lista de colunas
        :param values: Lista de tuplas com os valores
        :param schema: Schema específico (opcional)
        """
        schema = schema or self.schema
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        query = f'INSERT INTO {schema}.{table} ({columns_str}) VALUES ({placeholders})'
        
        try:
            psycopg2.extras.execute_batch(self.cursor, query, values)
            self.connection.commit()
            print(f"Inserção em lote concluída com sucesso na tabela '{schema}.{table}'")
            return True
        except psycopg2.Error as e:
            print(f"Erro na inserção em lote: {e}")
            self.connection.rollback()
            return False

    def create_schema(self, schema_name):
        """
        Cria um novo schema se não existir.
        """
        try:
            self.cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            self.connection.commit()
            print(f"Schema '{schema_name}' criado/verificado com sucesso")
            return True
        except psycopg2.Error as e:
            print(f"Erro ao criar schema: {e}")
            self.connection.rollback()
            return False