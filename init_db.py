"""
Script para inicializar o banco de dados do sistema de reconhecimento facial
Execute este script antes de rodar a aplicação pela primeira vez
"""

import mysql.connector
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

def create_database():
    """Cria o banco de dados se não existir"""
    try:
        # Conecta ao MySQL sem especificar banco
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Altere conforme necessário
            password=os.getenv('MYSQL_PASSWORD', '')  # Adicione sua senha no .env
        )
        
        cursor = connection.cursor()
        
        # Cria o banco de dados
        cursor.execute("CREATE DATABASE IF NOT EXISTS sdd_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Banco de dados 'sdd_project' criado/verificado com sucesso!")
        
        # Seleciona o banco de dados
        cursor.execute("USE sdd_project")
        
        # Executa o script SQL das tabelas
        with open('sdd_project', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Executa cada comando SQL separadamente
        commands = sql_script.split(';')
        for command in commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        
        connection.commit()
        print("✓ Tabelas criadas com sucesso!")
        
    except mysql.connector.Error as err:
        print(f"❌ Erro ao configurar banco de dados: {err}")
    except FileNotFoundError:
        print("❌ Arquivo 'sdd_project' não encontrado!")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        # Parse da URL do banco
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL não configurada no arquivo .env")
            return False
        
        # Extrai informações da URL
        # Formato: mysql+mysqlconnector://user:password@host:port/database
        import re
        match = re.match(r'mysql\+mysqlconnector://([^:]+):([^@]+)@([^:]+):?(\d+)?/(.+)', db_url)
        
        if not match:
            print("❌ Formato da DATABASE_URL inválido")
            return False
        
        user, password, host, port, database = match.groups()
        port = int(port) if port else 3306
        
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        print("✓ Conexão com o banco de dados testada com sucesso!")
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Inicializando banco de dados do Sistema de Reconhecimento Facial...")
    print()
    
    # Verifica se o arquivo .env existe
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        print("📝 Copie o arquivo .env.example para .env e configure suas credenciais")
        exit(1)
    
    # Cria o banco e tabelas
    create_database()
    
    # Testa a conexão
    print()
    print("🔍 Testando conexão...")
    if test_connection():
        print()
        print("🎉 Configuração concluída! Você pode executar a aplicação com:")
        print("   python app.py")
    else:
        print()
        print("❌ Configuração incompleta. Verifique as credenciais no arquivo .env")
