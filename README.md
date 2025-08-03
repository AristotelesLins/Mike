# 🎯 Sistema de Reconhecimento Facial em Tempo Real

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Sistema completo de reconhecimento facial desenvolvido em Python com Flask, OpenCV e face_recognition. Oferece detecção e identificação de rostos em tempo real através de câmeras IP e webcams, com interface web moderna e responsiva.

## 📋 Índice

- [🚀 Características](#-características)
- [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [📋 Pré-requisitos](#-pré-requisitos)
- [⚙️ Instalação](#️-instalação)
- [🗄️ Configuração do Banco de Dados](#️-configuração-do-banco-de-dados)
- [🎮 Como Usar](#-como-usar)
- [📸 Funcionalidades Detalhadas](#-funcionalidades-detalhadas)
- [🔧 Configurações Avançadas](#-configurações-avançadas)
- [🔍 Troubleshooting](#-troubleshooting)
- [📊 Estrutura do Projeto](#-estrutura-do-projeto)
- [🤝 Contribuição](#-contribuição)
- [📄 Licença](#-licença)

## 🚀 Características

### ✨ **Principais Funcionalidades**
- 👁️ **Reconhecimento Facial em Tempo Real** - Detecção e identificação instantânea de rostos
- 📹 **Múltiplas Câmeras** - Suporte para webcams locais e câmeras IP
- 🏢 **Multi-estabelecimento** - Gerenciamento de múltiplos locais e câmeras
- 👤 **Cadastro de Rostos** - Interface intuitiva para registro de pessoas
- 📊 **Dashboard Interativo** - Monitoramento em tempo real com estatísticas
- 📈 **Histórico de Avistamentos** - Registro completo de detecções
- 🔐 **Sistema de Autenticação** - Controle de acesso seguro
- 📱 **Interface Responsiva** - Compatível com desktop e mobile

### 🎯 **Tecnologias Avançadas**
- **Socket.IO** - Comunicação bidirecional em tempo real
- **Threading** - Processamento paralelo para múltiplas câmeras
- **Cache Inteligente** - Otimização de performance
- **Auto-reconexão** - Estabilidade em câmeras IP
- **Throttling** - Controle de spam de detecções

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **Python >3.8 <= 11.9** - Linguagem principal
- **Flask 2.3+** - Framework web
- **Flask-SocketIO** - Comunicação em tempo real
- **Flask-Login** - Autenticação de usuários
- **SQLAlchemy** - ORM para banco de dados
- **OpenCV 4.8+** - Processamento de imagem
- **face_recognition** - Biblioteca de reconhecimento facial
- **NumPy** - Computação científica
- **MySQL Connector** - Conexão com MySQL

### **Frontend**
- **HTML5** - Estrutura
- **Bootstrap 5** - Framework CSS
- **JavaScript ES6** - Interatividade
- **Socket.IO Client** - Comunicação tempo real
- **Font Awesome** - Ícones

### **Banco de Dados**
- **MySQL 8.0+** - Sistema de gerenciamento de banco de dados

## 📋 Pré-requisitos

### **Sistema Operacional**
- Windows 10/11
- macOS 10.14+
- Ubuntu 18.04+ / Debian 10+

### **Software Necessário**
```bash
# Python (versão 3.8 ou superior)
python --version  # deve retornar Python 3.8.x ou superior

# MySQL Server (versão 8.0 ou superior)
mysql --version   # deve retornar mysql Ver 8.0.x

# Git (para clonar o repositório)
git --version     # qualquer versão recente
```

### **Hardware Recomendado**
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **CPU**: Processador dual-core ou superior
- **Câmera**: Webcam USB ou câmera IP compatível
- **Rede**: Conexão estável para câmeras IP

## ⚙️ Instalação

### **1. Preparar o Ambiente**
```bash
# Clone o projeto ou baixe os arquivos
# Navegue para o diretório do projeto
cd c:\dev\teste-rani

# Verificar se Python está instalado
python --version  # deve mostrar Python 3.8+
```

### **2. Criar Ambiente Virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **3. Instalar Dependências**
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências principais
pip install flask flask-socketio flask-login flask-sqlalchemy
pip install opencv-python face-recognition numpy
pip install mysql-connector-python python-dotenv
pip install flask-wtf wtforms

# Para desenvolvimento (opcional)
pip install pytest black flake8
```

### **4. Configurar Variáveis de Ambiente**
Crie um arquivo `.env` na raiz do projeto:
```env
# Configurações do Banco de Dados
DATABASE_URL="mysql+mysqlconnector://usuario:senha@localhost/nome_banco"

# Chave Secreta (gere uma chave única)
SECRET_KEY="sua_chave_secreta_super_segura_aqui_123456789"
```

## 🗄️ Configuração do Banco de Dados

### **1. Instalar MySQL**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# Windows
# Baixe e instale do site oficial: https://dev.mysql.com/downloads/installer/

# macOS (com Homebrew)
brew install mysql
```

### **2. Configurar Banco de Dados**
```sql
-- Conecte ao MySQL como root
mysql -u root -p

-- Crie o banco de dados
CREATE DATABASE sdd_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crie um usuário específico (recomendado)
CREATE USER 'ari'@'localhost' IDENTIFIED BY 'ari';
GRANT ALL PRIVILEGES ON sdd_project.* TO 'ari'@'localhost';
FLUSH PRIVILEGES;

-- Sair do MySQL
EXIT;
```

### **3. Atualizar .env**
```env
DATABASE_URL="mysql+mysqlconnector://ari:ari@localhost/sdd_project"
SECRET_KEY="sistema_facial_recognition_2025_super_seguro_key_123456789"
```

### **4. Inicializar Tabelas**
```bash
# As tabelas são criadas automaticamente na primeira execução
# Ativar ambiente virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Executar aplicação
python app.py
```

## 🎮 Como Usar

### **1. Iniciar o Sistema**
```bash
# Navegar para o diretório do projeto
cd c:\dev\teste-rani

# Ativar ambiente virtual (IMPORTANTE!)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Executar aplicação
python app.py
```

### **2. Acessar Interface Web**
Abra seu navegador e acesse:
- **Local**: http://localhost:5000
- **Rede local**: http://192.168.x.x:5000 (IP mostrado no console)

### **3. Configuração Inicial**
1. **Registrar Usuário** - Crie sua conta na tela de registro
2. **Fazer Login** - Acesse com suas credenciais
3. **Criar Estabelecimento** - Configure seu primeiro local
4. **Adicionar Câmera** - Configure webcam ou câmera IP
5. **Cadastrar Rostos** - Registre pessoas conhecidas
6. **Iniciar Monitoramento** - Ative as câmeras no dashboard

## 📸 Funcionalidades Detalhadas

### **🏠 Dashboard Principal**
- ✅ Visualização em tempo real de todas as câmeras
- ✅ Estatísticas atualizadas automaticamente
- ✅ Controle de ativação/desativação de câmeras
- ✅ Notificações de detecções em tempo real
- ✅ Indicadores de status das câmeras

### **🏢 Gerenciamento de Estabelecimentos**
```
Menu: Estabelecimentos → Novo Estabelecimento
- Nome do estabelecimento
- Associação automática ao usuário logado
- Edição e exclusão
- Visualização de câmeras por estabelecimento
```

### **📹 Configuração de Câmeras**
```
Tipos Suportados:
✅ Webcam USB: ID numérico (0, 1, 2...)
✅ Câmera IP: URL completa (http://192.168.1.100:8080)
✅ Stream MJPEG: Adiciona automaticamente /video

Exemplos de URLs:
- Webcam: 0
- DroidCam: http://192.168.1.100:4747
- IP Webcam: http://192.168.1.100:8080
```

### **👤 Cadastro de Rostos**
1. **Captura Automática**:
   - Selecione a câmera desejada
   - Clique em "Capturar Rosto"
   - Sistema detecta automaticamente
   - Visualize a imagem capturada
   - Digite o nome da pessoa
   - Confirme o cadastro

2. **Validações Implementadas**:
   - ✅ Detecta apenas um rosto por vez
   - ✅ Verifica duplicatas automaticamente
   - ✅ Valida qualidade mínima da imagem
   - ✅ Cache temporário para segurança

### **📊 Histórico e Relatórios**
- ✅ Registro de todos os avistamentos
- ✅ Filtros por data, pessoa e câmera
- ✅ Paginação automática
- ✅ Estatísticas em tempo real
- ✅ Informações de estabelecimento

### **🔐 Sistema de Autenticação**
- ✅ Registro de usuários
- ✅ Login seguro com hash de senha
- ✅ Sessões protegidas
- ✅ Isolamento de dados por usuário
- ✅ Logout automático

## 🔧 Configurações Avançadas

### **🎛️ Parâmetros de Reconhecimento**
```python
# Em face_recognition_engine.py

# Sensibilidade de detecção (0.0 - 1.0)
RECOGNITION_TOLERANCE = 0.6  # Padrão: 0.6 (menor = mais restritivo)

# Modelo de detecção
DETECTION_MODEL = "hog"  # ou "cnn" para maior precisão (requer GPU)

# Throttling de detecções (segundos)
DETECTION_THROTTLE = 60  # Evita spam de detecções
```

### **📹 Configurações de Câmera**
```python
# Resolução de captura
CAPTURE_WIDTH = 640
CAPTURE_HEIGHT = 480

# FPS de processamento
PROCESSING_FPS = 15

# Buffer de câmeras IP
CAMERA_BUFFER_SIZE = 1  # Reduz latência
```

### **🔧 Otimizações de Performance**
```python
# Processamento a cada N frames
FRAME_SKIP = 3  # Processa 1 a cada 3 frames

# Escala de redimensionamento
SCALE_FACTOR = 0.5  # 50% do tamanho original

# Qualidade JPEG de stream
JPEG_QUALITY = 80  # 0-100 (menor = menos qualidade, mais velocidade)
```

## 🔍 Troubleshooting

### **❌ Problemas Comuns**

#### **1. Erro: "No module named cv2"**
```bash
# Reinstalar OpenCV
pip uninstall opencv-python
pip install opencv-python

# Se persistir, instalar com conda
conda install opencv
```

#### **2. Erro: "Can't connect to MySQL"**
```bash
# Verificar se MySQL está rodando
# Windows:
net start mysql

# Linux:
sudo systemctl start mysql
sudo systemctl status mysql

# Testar conexão manualmente
mysql -u ari -p
```

#### **3. Erro: "Camera not found"**
```bash
# Testar câmera separadamente
python -c "import cv2; cap = cv2.VideoCapture(0); print('Câmera OK:', cap.isOpened())"

# Para câmeras IP, testar URL no navegador
# Exemplo: http://192.168.1.100:8080/video
```

#### **4. Erro: "face_recognition not found"**
```bash
# Windows - instalar Visual C++ Build Tools primeiro
# Baixe: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Reinstalar face_recognition
pip uninstall face_recognition dlib
pip install dlib
pip install face_recognition
```

#### **5. Erro: "Stream ends prematurely"**
```bash
# Problema comum com câmeras IP
# Verificar se a URL está correta
# Tentar diferentes formatos:
# - http://IP:PORT
# - http://IP:PORT/video
# - http://IP:PORT/mjpeg
```

#### **6. Performance lenta**
```python
# Otimizar configurações em face_recognition_engine.py
# Reduzir resolução
CAPTURE_WIDTH = 320
CAPTURE_HEIGHT = 240

# Aumentar skip de frames
FRAME_SKIP = 5

# Usar modelo HOG (mais rápido que CNN)
DETECTION_MODEL = "hog"
```

### **🚀 Dicas de Performance**

#### **Para Sistemas com Recursos Limitados**
- Reduza a resolução das câmeras
- Aumente o intervalo de processamento (FRAME_SKIP)
- Use apenas o modelo HOG
- Limite o número de câmeras simultâneas

#### **Para Múltiplas Câmeras**
- Aumente o throttling de detecções
- Reduza a qualidade JPEG dos streams
- Use SSDs para melhor I/O
- Configure mais RAM se possível

## 📊 Estrutura do Projeto

```
c:\dev\teste-rani/
├── 📄 app.py                    # Aplicação principal Flask + Socket.IO
├── 📄 models.py                 # Modelos do banco de dados SQLAlchemy
├── 📄 forms.py                  # Formulários WTForms para validação
├── 📄 face_recognition_engine.py # Engine de reconhecimento facial
├── 📄 camera_client.py          # Cliente de câmera (utilitário)
├── 📄 .env                      # Variáveis de ambiente (não versionado)
├── 📄 README.md                 # Este arquivo de documentação
├── 📁 templates/               # Templates HTML Jinja2
│   ├── 📄 base.html            # Template base com Bootstrap
│   ├── 📄 dashboard.html       # Dashboard principal
│   ├── 📄 faces.html           # Gerenciamento de rostos
│   ├── 📄 cameras.html         # Configuração de câmeras
│   ├── 📄 establishments.html   # Gerenciamento de estabelecimentos
│   ├── 📄 sightings.html       # Histórico de avistamentos
│   ├── 📄 login.html           # Tela de login
│   └── 📄 register.html        # Tela de registro
├── 📁 venv/                    # Ambiente virtual Python
│   ├── 📁 Scripts/             # Executáveis (Windows)
│   ├── 📁 Lib/                 # Bibliotecas Python
│   └── 📁 pyvenv.cfg           # Configuração do venv
└── 📁 __pycache__/             # Cache Python (gerado automaticamente)
```

### **📋 Principais Arquivos**

#### **app.py** - Aplicação Principal
- Configuração Flask e extensões
- Rotas de autenticação e CRUD
- Socket.IO para tempo real
- Threading para múltiplas câmeras
- Sistema de cache inteligente

#### **models.py** - Modelos de Dados
- User: Usuários do sistema
- Establishment: Estabelecimentos
- Camera: Configuração de câmeras
- KnownFace: Rostos cadastrados
- Sighting: Histórico de avistamentos

#### **face_recognition_engine.py** - Engine de IA
- Carregamento de rostos conhecidos
- Processamento de frames em tempo real
- Detecção e reconhecimento facial
- Cache e otimizações de performance
- Registro de avistamentos

#### **forms.py** - Validação de Dados
- LoginForm: Formulário de login
- RegisterForm: Registro de usuários
- EstablishmentForm: Criar estabelecimentos
- CameraForm: Configurar câmeras
- FaceRegisterForm: Cadastrar rostos

## 🚦 Status das Funcionalidades

### **✅ Implementadas e Testadas**
- [x] Sistema de autenticação completo (login/registro/logout)
- [x] Reconhecimento facial em tempo real com OpenCV + face_recognition
- [x] Suporte a múltiplas câmeras (webcam + IP cameras)
- [x] Interface web responsiva com Bootstrap 5
- [x] Cadastro e gerenciamento de rostos via interface
- [x] Histórico completo de avistamentos com paginação
- [x] Estatísticas em tempo real via Socket.IO
- [x] Cache inteligente para otimização de performance
- [x] Auto-reconexão automática para câmeras IP instáveis
- [x] Throttling de detecções para evitar spam
- [x] Threading para processamento paralelo
- [x] Validação de dados e tratamento de erros
- [x] Isolamento de dados por usuário
- [x] Sistema de logs detalhado

### **🔄 Melhorias Contínuas**
- [ ] API REST completa para integração externa
- [ ] Notificações push em tempo real
- [ ] Exportação de relatórios em PDF/Excel
- [ ] Suporte a múltiplos algoritmos de reconhecimento
- [ ] Interface mobile dedicada (PWA)
- [ ] Análise de sentimentos e emoções

### **📋 Roadmap Futuro**
- [ ] Reconhecimento de objetos além de rostos
- [ ] Detecção de comportamentos suspeitos
- [ ] Integração com sistemas de segurança externos
- [ ] Machine Learning avançado com TensorFlow
- [ ] Análise comportamental e padrões
- [ ] Alertas automáticos por email/SMS
- [ ] Dashboard administrativo avançado
- [ ] Backup automático de dados

## 🔐 Segurança e Boas Práticas

### **�️ Medidas de Segurança Implementadas**
- ✅ Hash seguro de senhas usando Werkzeug
- ✅ Validação rigorosa de entrada em todos os formulários
- ✅ Autenticação baseada em sessão com Flask-Login
- ✅ Controle de acesso por usuário (isolamento de dados)
- ✅ Sanitização de dados de câmera e URLs
- ✅ Proteção contra SQL injection via SQLAlchemy ORM
- ✅ Validação de tipos de arquivo para uploads

### **⚠️ Recomendações para Produção**
```python
# Configurações de segurança para produção
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS obrigatório
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Previne XSS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # Timeout de sessão

# CORS configurado adequadamente
socketio = SocketIO(app, cors_allowed_origins=["https://seu-dominio.com"])

# Use servidor WSGI de produção (não o servidor de desenvolvimento)
# gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### **🔒 Dados Sensíveis**
- Rostos são armazenados como encoding numérico (não imagens)
- Senhas nunca são armazenadas em texto plano
- Logs não contêm informações pessoais identificáveis
- Cache temporário é limpo automaticamente

## 📈 Monitoramento e Análise

### **📊 Métricas Disponíveis em Tempo Real**
- Total de rostos cadastrados por usuário
- Proporção rostos conhecidos vs desconhecidos
- Avistamentos das últimas 24 horas
- Número de câmeras ativas simultaneamente
- Performance de detecção e FPS das câmeras

### **🔍 Sistema de Logs**
```bash
# Logs são exibidos no console durante desenvolvimento
# Níveis de log disponíveis:
# - INFO: Operações normais
# - WARNING: Situações anômalas mas não críticas
# - ERROR: Erros que requerem atenção

# Para produção, redirecionar logs para arquivo:
python app.py > sistema_facial.log 2>&1

# Monitorar logs em tempo real:
tail -f sistema_facial.log
```

### **📋 Tipos de Eventos Registrados**
- Conexões e desconexões de usuários
- Início e parada de câmeras
- Detecções de rostos (conhecidos/desconhecidos)
- Erros de conexão com câmeras
- Operações de cadastro de rostos
- Performance de processamento

## 🆘 Suporte e Comunidade

### **💬 Canais de Ajuda**
- **Issues GitHub**: Para reportar bugs e solicitar features
- **Documentação**: Este README completo
- **Wiki do Projeto**: Tutoriais avançados e exemplos
- **Discussions**: Perguntas e discussões da comunidade

### **🐛 Como Reportar Bugs**
Ao reportar um problema, inclua:

1. **Informações do Sistema**:
   - Sistema operacional e versão
   - Versão do Python (`python --version`)
   - Versões das dependências (`pip list`)

2. **Descrição do Problema**:
   - Comportamento esperado vs atual
   - Passos exatos para reproduzir
   - Screenshots se aplicável

3. **Logs de Erro**:
   - Saída completa do console
   - Stack trace completo
   - Configurações relevantes (sem senhas!)

4. **Ambiente**:
   - Tipo de câmera (webcam/IP)
   - Configuração de rede
   - Hardware utilizado

### **✨ Como Contribuir**
1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Implemente as mudanças seguindo os padrões do projeto
4. Adicione testes se aplicável
5. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
6. Push para a branch (`git push origin feature/MinhaFeature`)
7. Abra um Pull Request com descrição detalhada

### **📝 Padrões de Código**
```bash
# Formatação automática com Black
black *.py

# Verificação de qualidade com Flake8
flake8 *.py --max-line-length=88

# Testes automatizados
pytest tests/ -v

# Type hints (recomendado)
mypy *.py
```

## 📊 Especificações Técnicas

### **🔧 Requisitos Mínimos**
- **CPU**: 2 cores @ 2.0GHz
- **RAM**: 4GB
- **Storage**: 2GB livres
- **Network**: 10Mbps para câmeras IP
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04

### **🚀 Configuração Recomendada**
- **CPU**: 4+ cores @ 3.0GHz
- **RAM**: 8GB+
- **Storage**: SSD com 10GB+ livres
- **Network**: 100Mbps para múltiplas câmeras IP
- **GPU**: Opcional para aceleração (CUDA)

### **📏 Limitações Conhecidas**
- Máximo recomendado: 10 câmeras simultâneas
- Processamento single-threaded por câmera
- Detecção otimizada para rostos frontais
- Requer boa iluminação para melhor precisão
- Performance varia com qualidade da câmera

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - consulte o arquivo `LICENSE` para detalhes completos.

### **Resumo da Licença MIT**
- ✅ Uso comercial permitido
- ✅ Modificação permitida
- ✅ Distribuição permitida
- ✅ Uso privado permitido
- ❌ Nenhuma garantia fornecida
- ❌ Autor não é responsável por danos

## 👨‍💻 Informações do Desenvolvedor

**Sistema desenvolvido para fins educacionais e demonstração de conceitos de visão computacional e desenvolvimento web.**

### **Tecnologias Core**
- **Backend**: Python 3.8+ com Flask
- **Frontend**: HTML5, CSS3, JavaScript ES6
- **Database**: MySQL 8.0+
- **AI/ML**: OpenCV + face_recognition
- **Real-time**: Socket.IO
- **UI**: Bootstrap 5 + Font Awesome

### **Arquitetura**
- **Padrão MVC** com separação clara de responsabilidades
- **Threading** para processamento paralelo
- **WebSocket** para comunicação bidirecional
- **ORM** para abstração de banco de dados
- **Cache em memória** para otimização

## 🙏 Agradecimentos e Créditos

### **Bibliotecas e Ferramentas**
- **[face_recognition](https://github.com/ageitgey/face_recognition)** - Por fornecer uma biblioteca Python incrível para reconhecimento facial
- **[OpenCV](https://opencv.org/)** - Pela base sólida de visão computacional e processamento de imagem
- **[Flask](https://flask.palletsprojects.com/)** - Pelo framework web elegante e flexível
- **[Bootstrap](https://getbootstrap.com/)** - Pela interface responsiva e moderna
- **[Socket.IO](https://socket.io/)** - Pela comunicação em tempo real eficiente

### **Comunidade e Suporte**
- **Comunidade Python** - Pelo suporte contínuo e documentação excelente
- **Stack Overflow** - Pelas respostas e soluções compartilhadas
- **GitHub** - Pela plataforma de desenvolvimento colaborativo
- **MySQL** - Pelo sistema de banco de dados robusto e confiável

### **Inspirações e Referências**
- Projetos open-source de reconhecimento facial
- Documentação oficial das bibliotecas utilizadas
- Tutoriais e artigos da comunidade de visão computacional
- Boas práticas de desenvolvimento web com Flask

---

## 🎯 Início Rápido (TL;DR)

```bash
# 1. Clonar/baixar projeto
cd c:\dev\teste-rani

# 2. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install flask flask-socketio flask-login flask-sqlalchemy
pip install opencv-python face-recognition numpy mysql-connector-python python-dotenv flask-wtf wtforms

# 4. Configurar .env
echo 'DATABASE_URL="mysql+mysqlconnector://ari:ari@localhost/sdd_project"' > .env
echo 'SECRET_KEY="sistema_facial_recognition_2025_super_seguro_key_123456789"' >> .env

# 5. Configurar MySQL
mysql -u root -p
CREATE DATABASE sdd_project;
CREATE USER 'ari'@'localhost' IDENTIFIED BY 'ari';
GRANT ALL PRIVILEGES ON sdd_project.* TO 'ari'@'localhost';
EXIT;

# 6. Executar aplicação
python app.py

# 7. Acessar http://localhost:5000
```

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!**

**🔄 Última atualização**: 3 de Agosto de 2025  
**📅 Versão**: 2.0.0  
**🎯 Status**: Estável e em Produção  
**🏆 Funcionalidades**: 100% Operacionais

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt
```

### 2. Configuração do MySQL

```sql
-- 1. Abra o MySQL Workbench ou linha de comando do MySQL
-- 2. Crie um usuário para o projeto (substitua 'sua_senha' por uma senha segura)
CREATE USER 'ari'@'localhost' IDENTIFIED BY 'sua_senha';

-- 3. Dê permissões para o usuário
GRANT ALL PRIVILEGES ON *.* TO 'ari'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configuração do Arquivo .env

```bash
# 1. Copie o arquivo de exemplo
copy .env.example .env

# 2. Edite o arquivo .env com suas configurações
# Abra o arquivo .env e configure:
DATABASE_URL="mysql+mysqlconnector://ari:sua_senha@localhost:3306/sdd_project"
SECRET_KEY="sua_chave_secreta_super_segura_aqui"
MYSQL_PASSWORD=sua_senha
```

### 4. Inicialização do Banco de Dados

```bash
# Execute o script de inicialização
python init_db.py
```

## 🏃‍♂️ Executando o Sistema

### 1. Servidor Principal

```bash
# Inicie o servidor Flask
python app.py
```

O sistema estará disponível em: **http://localhost:5000**

### 2. Cliente de Câmera (Para cada câmera)

```bash
# Para webcam padrão (câmera ID 1)
python camera_client.py --camera-id 1 --source 0

# Para segunda webcam (câmera ID 2)  
python camera_client.py --camera-id 2 --source 1

# Para câmera IP (câmera ID 3)
python camera_client.py --camera-id 3 --source "http://192.168.1.100:8080/video"
```

### 3. Gerenciador de Câmeras (Opcional)

```bash
# Configure múltiplas câmeras
python camera_manager.py config

# Inicie todas as câmeras configuradas
python camera_manager.py start-all

# Pare todas as câmeras
python camera_manager.py stop-all
```

## 🎮 Como Usar o Sistema

### 1. Primeiro Acesso

1. **Cadastre um usuário**: Acesse http://localhost:5000 e clique em "Cadastro"
2. **Faça login**: Use suas credenciais criadas
3. **Crie um estabelecimento**: Vá em "Estabelecimentos" → "Novo Estabelecimento"
4. **Adicione câmeras**: Vá em "Câmeras" → Configure nome e fonte

### 2. Cadastrando Rostos

1. **Acesse "Rostos"** no menu
2. **Selecione uma câmera** no dropdown
3. **Clique em "Capturar Rosto"**
4. **Posicione-se na frente da câmera** (apenas uma pessoa por vez)
5. **Digite o nome** da pessoa
6. **Clique em "Cadastrar"**

### 3. Monitoramento

1. **Acesse o Dashboard**
2. **Selecione um estabelecimento**
3. **Clique em "Iniciar"** nas câmeras desejadas
4. **Execute o camera_client.py** para cada câmera
5. **Monitore em tempo real** os rostos detectados

### 4. Histórico

- **Vá em "Histórico"** para ver todos os avistamentos
- **Filtre por data** e estabelecimento
- **Exporte relatórios** se necessário

## 🔧 Configurações Avançadas

### Tipos de Fontes de Câmera

```bash
# Webcam USB
--source 0          # Primeira webcam
--source 1          # Segunda webcam

# Câmera IP
--source "http://192.168.1.100:8080/video"     # MJPEG stream
--source "rtsp://admin:123456@192.168.1.100"   # RTSP stream

# Arquivo de vídeo (para testes)
--source "C:\videos\teste.mp4"
```

### Configuração de Performance

No arquivo `face_recognition_engine.py`, você pode ajustar:

```python
# Linha 36 - Fator de redimensionamento (menor = mais rápido)
scale_factor = 0.25  # Padrão: 0.25 (4x menor)

# Linha 38 - Modelo de detecção
face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
# Opções: "hog" (CPU, mais rápido) ou "cnn" (GPU, mais preciso)

# Linha 67 - Limiar de similaridade
if face_distances[best_match_index] < 0.5:  # Padrão: 0.5 (mais restritivo)
```

### Configuração de Rede

Para acessar de outros dispositivos:

```python
# No app.py, linha final:
socketio.run(app, debug=False, host='0.0.0.0', port=5000)

# Acesse via: http://IP_DO_SERVIDOR:5000
```

## 🐛 Solução de Problemas

### Problema: "ModuleNotFoundError"
```bash
# Solução: Instale as dependências
pip install -r requirements.txt
```

### Problema: "mysql.connector.errors.ProgrammingError"
```bash
# Solução: Verifique credenciais no .env
# Teste a conexão MySQL manualmente
```

### Problema: "Camera not found"
```bash
# Solução: Verifique se a câmera está conectada
# Teste com diferentes valores de --source (0, 1, 2...)
```

### Problema: Performance lenta
```bash
# Soluções:
# 1. Reduza o scale_factor para 0.15
# 2. Use modelo "hog" em vez de "cnn"
# 3. Adicione mais RAM
# 4. Use GPU com modelo "cnn"
```

### Problema: Socket.IO não conecta
```bash
# Soluções:
# 1. Verifique se o servidor está rodando
# 2. Desabilite firewall/antivírus temporariamente
# 3. Use navegador diferente
```

## 📱 Recursos do Sistema

### ✅ Funcionalidades Implementadas

- **👤 Sistema de usuários** com login/cadastro
- **🏢 Gerenciamento de estabelecimentos** com paginação
- **📹 Múltiplas câmeras** por estabelecimento
- **🎯 Reconhecimento facial** em tempo real
- **📊 Dashboard interativo** com estatísticas
- **🔍 Detecção automática** de rostos desconhecidos
- **📝 Cadastro manual** de rostos conhecidos
- **📈 Histórico completo** de avistamentos
- **🔄 Atualizações em tempo real** via Socket.IO
- **🎨 Interface responsiva** e moderna
- **🔊 Notificações sonoras** para detecções
- **🖥️ Modo tela cheia** para câmeras
- **⚙️ Múltiplos layouts** de visualização

### 🎛️ Recursos Avançados

- **🧵 Multi-threading** para múltiplas câmeras
- **🛡️ Segurança por usuário** (dados isolados)
- **📊 Estatísticas em tempo real**
- **🔄 Auto-limpeza** de conexões inativas
- **📱 Interface responsiva** (desktop/mobile)
- **🎯 Detecção inteligente** (evita duplicatas)
- **💾 Backup automático** de encodings faciais

## 📞 Suporte

### Logs e Debug

```bash
# Para ver logs detalhados, execute:
python app.py

# Os logs mostrarão:
# - Conexões de clientes
# - Detecções de rostos  
# - Erros de processamento
# - Status das câmeras
```

### Comandos Úteis

```bash
# Verificar status do MySQL
net start mysql80

# Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Limpar cache do Python
rd /s "__pycache__"
del "*.pyc"

# Backup do banco
mysqldump -u ari -p sdd_project > backup.sql

# Restaurar banco
mysql -u ari -p sdd_project < backup.sql
```

---

## 🎉 Pronto!

Seu Sistema de Reconhecimento Facial está configurado e funcionando! 

**Acesse**: http://localhost:5000

**Principais funcionalidades**:
- Dashboard com múltiplas câmeras
- Cadastro e reconhecimento de rostos
- Histórico completo de avistamentos
- Notificações em tempo real
- Interface moderna e responsiva

**Para dúvidas**, consulte os logs do sistema ou verifique as configurações do arquivo `.env`.
