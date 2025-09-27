# etl/main.py
import os
from dotenv import load_dotenv
from conexao import PostgresDB

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# --- DADOS DE CONFIGURAÇÃO ---
# Lê as credenciais das variáveis de ambiente carregadas do .env
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Validação para garantir que todas as variáveis foram carregadas
if not all([DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT]):
    raise ValueError("Uma ou mais variáveis de ambiente do banco de dados não foram definidas.")

def main():
    # A classe recebe as variáveis lidas do ambiente
    with PostgresDB(DB_NAME, DB_USER, DB_PASS, DB_HOST, port=DB_PORT) as db:
        
        # --- 1. CREATE (Inserir) ---
        print("\n--- Inserindo usuários ---")
        usuario1_data = {'nome': 'Alice', 'email': 'alice@example.com'}
        usuario2_data = {'nome': 'Beto', 'email': 'beto@example.com'}
        
        id_alice = db.create('usuarios', usuario1_data)
        id_beto = db.create('usuarios', usuario2_data)

        # --- 2. READ (Ler) ---
        print("\n--- Lendo todos os usuários ---")
        todos_usuarios = db.read('usuarios')
        if todos_usuarios:
            for usuario in todos_usuarios:
                print(usuario)

        print("\n--- Lendo um usuário específico (Alice) ---")
        usuario_alice = db.read('usuarios', where="id = %s", params=(id_alice,))
        if usuario_alice:
            print(usuario_alice[0])

        # --- 3. UPDATE (Atualizar) ---
        print("\n--- Atualizando o email do Beto ---")
        novos_dados_beto = {'email': 'beto_novo_email@example.com'}
        db.update('usuarios', novos_dados_beto, where="id = %s", params=(id_beto,))

        print("\n--- Verificando a atualização do Beto ---")
        usuario_beto_atualizado = db.read('usuarios', where="id = %s", params=(id_beto,))
        if usuario_beto_atualizado:
            print(usuario_beto_atualizado[0])

        # --- 4. DELETE (Deletar) ---
        print("\n--- Deletando a Alice ---")
        if id_alice:
            db.delete('usuarios', where="id = %s", params=(id_alice,))
        
        print("\n--- Verificando usuários restantes ---")
        usuarios_restantes = db.read('usuarios')
        if usuarios_restantes:
            for usuario in usuarios_restantes:
                print(usuario)
        else:
            print("Nenhum usuário restante.")

if __name__ == "__main__":
    main()