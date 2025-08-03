"""
Script de teste para verificar se o sistema está funcionando corretamente
Execute: python test_system.py
"""

import sys
import os
import importlib.util
from datetime import datetime

def test_imports():
    """Testa se todas as dependências estão instaladas"""
    print("🔍 Testando importações...")
    
    required_modules = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'SQLAlchemy'), 
        ('flask_socketio', 'SocketIO'),
        ('flask_login', 'LoginManager'),
        ('cv2', 'OpenCV'),
        ('face_recognition', 'face_recognition'),
        ('mysql.connector', 'MySQL Connector'),
        ('numpy', 'NumPy'),
        ('werkzeug', 'Werkzeug'),
        ('wtforms', 'WTForms'),
        ('dotenv', 'python-dotenv'),
        ('bcrypt', 'bcrypt'),
        ('PIL', 'Pillow')
    ]
    
    errors = []
    
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except ImportError as e:
            errors.append(f"  ❌ {display_name}: {e}")
            print(f"  ❌ {display_name}: Não encontrado")
    
    if errors:
        print("\n❌ Erros encontrados:")
        for error in errors:
            print(error)
        print("\n💡 Execute: pip install -r requirements.txt")
        return False
    else:
        print("✅ Todas as dependências estão instaladas!")
        return True

def test_files():
    """Verifica se todos os arquivos necessários existem"""
    print("\n📁 Testando arquivos...")
    
    required_files = [
        'app.py',
        'models.py', 
        'forms.py',
        'face_recognition_engine.py',
        'camera_client.py',
        'requirements.txt',
        'sdd_project',
        '.env',
        'templates/base.html',
        'templates/dashboard.html',
        'templates/login.html',
        'templates/register.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path}: Não encontrado")
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} arquivo(s) não encontrado(s)")
        return False
    else:
        print("✅ Todos os arquivos estão presentes!")
        return True

def test_env_config():
    """Verifica configuração do arquivo .env"""
    print("\n⚙️ Testando configurações...")
    
    if not os.path.exists('.env'):
        print("  ❌ Arquivo .env não encontrado")
        print("  💡 Copie .env.example para .env e configure")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        db_url = os.getenv('DATABASE_URL')
        secret_key = os.getenv('SECRET_KEY')
        
        if not db_url:
            print("  ❌ DATABASE_URL não configurada")
            return False
        else:
            print(f"  ✅ DATABASE_URL: {db_url[:30]}...")
        
        if not secret_key:
            print("  ❌ SECRET_KEY não configurada")
            return False
        else:
            print("  ✅ SECRET_KEY: Configurada")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao carregar .env: {e}")
        return False

def test_database():
    """Testa conexão com o banco de dados"""
    print("\n🗃️ Testando banco de dados...")
    
    try:
        import mysql.connector
        from dotenv import load_dotenv
        load_dotenv()
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("  ❌ DATABASE_URL não configurada")
            return False
        
        # Parse da URL
        import re
        match = re.match(r'mysql\+mysqlconnector://([^:]+):([^@]+)@([^:]+):?(\d+)?/(.+)', db_url)
        
        if not match:
            print("  ❌ Formato da DATABASE_URL inválido")
            return False
        
        user, password, host, port, database = match.groups()
        port = int(port) if port else 3306
        
        # Testa conexão
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", (database,))
        table_count = cursor.fetchone()[0]
        
        print(f"  ✅ Conexão estabelecida")
        print(f"  ✅ Banco: {database}")
        print(f"  ✅ Tabelas: {table_count}")
        
        connection.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"  ❌ Erro MySQL: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_camera():
    """Testa se há câmeras disponíveis"""
    print("\n📹 Testando câmeras...")
    
    try:
        import cv2
        
        # Testa webcam padrão
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("  ✅ Webcam padrão (índice 0) funcionando")
                print(f"  ✅ Resolução: {frame.shape[1]}x{frame.shape[0]}")
            else:
                print("  ⚠️ Webcam conectada mas sem imagem")
            cap.release()
        else:
            print("  ❌ Webcam padrão não disponível")
        
        # Testa segunda webcam
        cap2 = cv2.VideoCapture(1)
        if cap2.isOpened():
            ret, frame = cap2.read()
            if ret:
                print("  ✅ Segunda webcam (índice 1) funcionando")
            cap2.release()
        else:
            print("  ℹ️ Segunda webcam não disponível (normal)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao testar câmeras: {e}")
        return False

def test_face_recognition():
    """Testa o sistema de reconhecimento facial"""
    print("\n👤 Testando reconhecimento facial...")
    
    try:
        import face_recognition
        import numpy as np
        
        # Cria uma imagem de teste
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Tenta detectar rostos (não deve encontrar nenhum)
        face_locations = face_recognition.face_locations(test_image)
        print(f"  ✅ Detecção funcionando (encontrou {len(face_locations)} rostos)")
        
        # Testa encoding
        if len(face_locations) == 0:
            print("  ✅ Sistema pronto para detectar rostos reais")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no reconhecimento facial: {e}")
        return False

def test_flask_app():
    """Testa se a aplicação Flask pode ser importada"""
    print("\n🌐 Testando aplicação Flask...")
    
    try:
        # Adiciona o diretório atual ao path
        sys.path.insert(0, '.')
        
        # Tenta importar a aplicação
        import app
        print("  ✅ Aplicação Flask importada com sucesso")
        
        # Testa se as rotas principais existem
        if hasattr(app, 'app'):
            routes = [rule.rule for rule in app.app.url_map.iter_rules()]
            important_routes = ['/', '/login', '/register', '/dashboard']
            
            for route in important_routes:
                if route in routes:
                    print(f"  ✅ Rota {route} disponível")
                else:
                    print(f"  ❌ Rota {route} não encontrada")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro ao importar aplicação: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE DO SISTEMA DE RECONHECIMENTO FACIAL")
    print("=" * 50)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    tests = [
        ("Dependências", test_imports),
        ("Arquivos", test_files),
        ("Configurações", test_env_config),
        ("Banco de Dados", test_database),
        ("Câmeras", test_camera),
        ("Reconhecimento Facial", test_face_recognition),
        ("Aplicação Flask", test_flask_app)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Erro inesperado: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 O sistema está pronto para uso!")
        print("\nPróximos passos:")
        print("1. Execute: python app.py")
        print("2. Acesse: http://localhost:5000")
        print("3. Cadastre-se e crie um estabelecimento")
        print("4. Configure suas câmeras")
        print("5. Execute: python camera_client.py --camera-id 1 --source 0")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
        print("🔧 Corrija os problemas antes de executar o sistema")
        
        if passed >= total * 0.7:  # Se 70% ou mais passaram
            print("\n💡 A maioria dos testes passou - você pode tentar executar mesmo assim")

if __name__ == "__main__":
    main()
