import os
import cv2
import numpy as np
import face_recognition
import base64
import threading
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Importa nossos módulos
from models import db, User, Establishment, Camera, KnownFace, Sighting
from forms import LoginForm, RegisterForm, EstablishmentForm, CameraForm, FaceRegisterForm
from face_recognition_engine import FaceRecognitionEngine

# Carrega variáveis de ambiente do .env
load_dotenv()

# --- CONFIGURAÇÃO ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'seu_super_segredo_aqui!')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Inicializa extensões
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar esta página.'
login_manager.login_message_category = 'info'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Dicionário para armazenar engines de reconhecimento por usuário
face_engines = {}
active_cameras = {}  # Dicionário para rastrear câmeras ativas
camera_threads = {}  # Threads de streaming das câmeras
temp_face_cache = {}  # Cache temporário para rostos capturados

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- ROTAS PRINCIPAIS ---
@app.route('/')
@login_required
def dashboard():
    """Dashboard principal com estabelecimentos e câmeras"""
    page = request.args.get('page', 1, type=int)
    establishments = Establishment.query.filter_by(user_id=current_user.id).paginate(
        per_page=5, page=page, error_out=False
    )
    
    # Estabelecimento selecionado
    selected_est_id = request.args.get('establishment', type=int)
    if selected_est_id:
        selected_establishment = Establishment.query.filter_by(
            id=selected_est_id, user_id=current_user.id
        ).first()
    else:
        selected_establishment = establishments.items[0] if establishments.items else None
    
    cameras = []
    if selected_establishment:
        cameras = Camera.query.filter_by(establishment_id=selected_establishment.id).all()
    
    # Estatísticas rápidas
    stats = None
    if current_user.id in face_engines:
        stats = face_engines[current_user.id].get_statistics()
    else:
        # Carrega engine se não existir
        face_engines[current_user.id] = FaceRecognitionEngine(current_user.id, app)
        stats = face_engines[current_user.id].get_statistics()
    
    return render_template('dashboard.html', 
                         establishments=establishments,
                         selected_establishment=selected_establishment,
                         cameras=cameras,
                         stats=stats)

@app.route('/api/stats')
@login_required
def get_stats():
    """API para obter estatísticas em tempo real"""
    if current_user.id not in face_engines:
        face_engines[current_user.id] = FaceRecognitionEngine(current_user.id, app)
    
    stats = face_engines[current_user.id].get_statistics()
    
    # Adiciona informações sobre câmeras ativas
    user_cameras = Camera.query.join(Establishment).filter(
        Establishment.user_id == current_user.id
    ).count()
    
    stats['total_cameras'] = user_cameras
    stats['active_cameras'] = len([cam for cam in active_cameras.values() 
                                 if cam.get('user_id') == current_user.id])
    
    return jsonify(stats)

@app.route('/establishments', methods=['GET', 'POST'])
@login_required
def manage_establishments():
    """Gerenciar estabelecimentos"""
    form = EstablishmentForm()
    if form.validate_on_submit():
        establishment = Establishment(
            name=form.name.data,
            user_id=current_user.id
        )
        db.session.add(establishment)
        db.session.commit()
        flash('Estabelecimento criado com sucesso!')
        return redirect(url_for('manage_establishments'))
    
    establishments = Establishment.query.filter_by(user_id=current_user.id).all()
    return render_template('establishments.html', form=form, establishments=establishments)

@app.route('/establishments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_establishment(id):
    establishment = Establishment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = EstablishmentForm(obj=establishment)
    
    if form.validate_on_submit():
        establishment.name = form.name.data
        db.session.commit()
        flash('Estabelecimento atualizado com sucesso!')
        return redirect(url_for('manage_establishments'))
    
    return render_template('edit_establishment.html', form=form, establishment=establishment)

@app.route('/establishments/<int:id>/delete')
@login_required
def delete_establishment(id):
    establishment = Establishment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(establishment)
    db.session.commit()
    flash('Estabelecimento excluído com sucesso!')
    return redirect(url_for('manage_establishments'))

@app.route('/cameras', methods=['GET', 'POST'])
@login_required
def manage_cameras():
    """Gerenciar câmeras"""
    form = CameraForm(current_user.id)
    if form.validate_on_submit():
        camera = Camera(
            name=form.name.data,
            camera_source=form.camera_source.data,
            establishment_id=form.establishment_id.data
        )
        db.session.add(camera)
        db.session.commit()
        flash('Câmera criada com sucesso!')
        return redirect(url_for('manage_cameras'))
    
    # Busca todas as câmeras dos estabelecimentos do usuário
    user_establishments = Establishment.query.filter_by(user_id=current_user.id).all()
    cameras = []
    for est in user_establishments:
        cameras.extend(est.cameras)
    
    return render_template('cameras.html', form=form, cameras=cameras)

@app.route('/cameras/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_camera(id):
    camera = Camera.query.join(Establishment).filter(
        Camera.id == id,
        Establishment.user_id == current_user.id
    ).first_or_404()
    
    form = CameraForm(current_user.id, obj=camera)
    
    if form.validate_on_submit():
        camera.name = form.name.data
        camera.camera_source = form.camera_source.data
        camera.establishment_id = form.establishment_id.data
        db.session.commit()
        flash('Câmera atualizada com sucesso!')
        return redirect(url_for('manage_cameras'))
    
    return render_template('edit_camera.html', form=form, camera=camera)

@app.route('/cameras/<int:id>/delete')
@login_required
def delete_camera(id):
    camera = Camera.query.join(Establishment).filter(
        Camera.id == id,
        Establishment.user_id == current_user.id
    ).first_or_404()
    db.session.delete(camera)
    db.session.commit()
    flash('Câmera excluída com sucesso!')
    return redirect(url_for('manage_cameras'))

@app.route('/faces', methods=['GET', 'POST'])
@login_required
def manage_faces():
    """Gerenciar rostos conhecidos"""
    form = FaceRegisterForm(current_user.id)
    faces = KnownFace.query.filter_by(user_id=current_user.id).all()
    
    return render_template('faces.html', form=form, faces=faces)

@app.route('/faces/capture', methods=['POST'])
@login_required
def capture_face():
    """Capturar rosto de uma câmera"""
    camera_id = request.json.get('camera_id')
    
    # Garante que o engine do usuário está carregado
    if current_user.id not in face_engines:
        face_engines[current_user.id] = FaceRecognitionEngine(current_user.id, app)
    
    engine = face_engines[current_user.id]
    
    # Pausa temporariamente o streaming desta câmera para evitar conflitos
    camera_key = f"{current_user.id}_{camera_id}"
    was_streaming = camera_key in active_cameras
    
    if was_streaming:
        print(f"⏸️ Pausando streaming da câmera {camera_id} para captura...")
        # Para o streaming temporariamente
        if camera_key in camera_threads:
            active_cameras[camera_key]['stop_requested'] = True
            time.sleep(1)  # Aguarda um pouco para liberar a câmera
    
    try:
        result, message = engine.capture_face_from_camera(camera_id)
        
        if result:
            # Armazena temporariamente no cache do servidor
            cache_key = f"{current_user.id}_{camera_id}_{int(time.time())}"
            temp_face_cache[cache_key] = {
                'encoding': result['encoding'],
                'frame': result['frame'],
                'location': result['location'],
                'timestamp': time.time(),
                'user_id': current_user.id
            }
            
            # Remove entradas antigas do cache (mais de 10 minutos)
            current_time = time.time()
            keys_to_remove = [k for k, v in temp_face_cache.items() 
                             if current_time - v['timestamp'] > 600]
            for key in keys_to_remove:
                del temp_face_cache[key]
            
            # Limpa dados antigos da sessão se existirem
            session.pop('temp_face_data', None)
            
            return jsonify({
                'success': True, 
                'message': message,
                'frame': result['frame'],
                'cache_key': cache_key
            })
        else:
            return jsonify({'success': False, 'message': message})
            
    finally:
        # Retoma o streaming se estava ativo
        if was_streaming:
            print(f"▶️ Retomando streaming da câmera {camera_id}...")
            # Reinicia o streaming
            active_cameras[camera_key]['stop_requested'] = False

@app.route('/faces/register', methods=['POST'])
@login_required
def register_face():
    """Registrar um rosto capturado"""
    name = request.json.get('name')
    cache_key = request.json.get('cache_key')
    
    if not cache_key or cache_key not in temp_face_cache:
        return jsonify({'success': False, 'message': 'Nenhum rosto foi capturado ou o tempo expirou'})
    
    face_data = temp_face_cache[cache_key]
    
    # Verifica se o rosto pertence ao usuário atual
    if face_data['user_id'] != current_user.id:
        return jsonify({'success': False, 'message': 'Acesso negado'})
    
    # Garante que o engine do usuário está carregado
    if current_user.id not in face_engines:
        face_engines[current_user.id] = FaceRecognitionEngine(current_user.id, app)
    
    engine = face_engines[current_user.id]
    
    success, message = engine.register_new_face(name, face_data)
    
    if success:
        # Remove do cache após o sucesso
        del temp_face_cache[cache_key]
    
    return jsonify({'success': success, 'message': message})

@app.route('/faces/<int:id>/delete')
@login_required
def delete_face(id):
    face = KnownFace.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(face)
    db.session.commit()
    
    # Recarrega o engine
    if current_user.id in face_engines:
        face_engines[current_user.id].load_known_faces()
    
    flash('Rosto excluído com sucesso!')
    return redirect(url_for('manage_faces'))

@app.route('/sightings')
@login_required
def view_sightings():
    """Visualizar histórico de avistamentos"""
    page = request.args.get('page', 1, type=int)
    
    # Query com joins para pegar dados relacionados
    sightings = db.session.query(Sighting, KnownFace, Camera, Establishment).join(
        KnownFace, Sighting.face_id == KnownFace.id
    ).join(
        Camera, Sighting.camera_id == Camera.id
    ).join(
        Establishment, Camera.establishment_id == Establishment.id
    ).filter(
        KnownFace.user_id == current_user.id
    ).order_by(
        Sighting.timestamp.desc()
    ).paginate(per_page=20, page=page, error_out=False)
    
    return render_template('sightings.html', sightings=sightings)

# --- SOCKET.IO ---
@socketio.on('connect')
def handle_connect(auth):
    """Cliente se conectou"""
    if current_user.is_authenticated:
        join_room(f"user_{current_user.id}")
        print(f'Cliente {current_user.username} conectado (Session: {request.sid})!')
        
        # Inicializa engine de reconhecimento se não existir
        if current_user.id not in face_engines:
            face_engines[current_user.id] = FaceRecognitionEngine(current_user.id, app)
        
        # Envia estatísticas iniciais
        stats = face_engines[current_user.id].get_statistics()
        emit('stats_update', stats)

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente se desconectou"""
    if current_user.is_authenticated:
        leave_room(f"user_{current_user.id}")
        print(f'Cliente {current_user.username} desconectado (Session: {request.sid})!')
        
        # Remove câmeras ativas deste usuário
        cameras_to_remove = [cam_id for cam_id, cam_info in active_cameras.items() 
                           if cam_info.get('user_id') == current_user.id and 
                              cam_info.get('session_id') == request.sid]
        
        for cam_id in cameras_to_remove:
            del active_cameras[cam_id]

@socketio.on('stream')
def handle_stream(data):
    """Processa stream de vídeo"""
    if not current_user.is_authenticated:
        emit('error', {'message': 'Usuário não autenticado'})
        return
    
    image_data = data.get('image')
    camera_id = data.get('camera_id')
    
    if not image_data or not camera_id:
        emit('error', {'message': 'Dados inválidos'})
        return
    
    # Verifica se a câmera pertence ao usuário
    camera = Camera.query.join(Establishment).filter(
        Camera.id == camera_id,
        Establishment.user_id == current_user.id
    ).first()
    
    if not camera:
        emit('error', {'message': 'Câmera não autorizada'})
        return
    
    # Garante que o engine está carregado
    if current_user.id not in face_engines:
        face_engines[current_user.id] = FaceRecognitionEngine(current_user.id, app)
    
    engine = face_engines[current_user.id]
    
    try:
        # Decodifica imagem
        header, encoded = image_data.split(",", 1)
        decoded_image = base64.b64decode(encoded)
        frame = cv2.imdecode(np.frombuffer(decoded_image, np.uint8), 1)
        
        if frame is None:
            emit('error', {'message': 'Frame inválido'})
            return
        
        # Processa frame
        processed_frame, face_names, face_ids = engine.process_frame(frame, camera_id)
        
        # Codifica frame processado com qualidade otimizada
        _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        processed_image_data = base64.b64encode(buffer).decode('utf-8')
        
        # Atualiza info da câmera ativa
        active_cameras[camera_id] = {
            'user_id': current_user.id,
            'session_id': request.sid,
            'last_update': datetime.utcnow(),
            'face_count': len(face_names)
        }
        
        # Envia de volta para o cliente
        emit('processed_frame', {
            'camera_id': camera_id,
            'image': processed_image_data,
            'faces': face_names,
            'face_count': len(face_names),
            'timestamp': datetime.utcnow().isoformat()
        }, room=f"user_{current_user.id}")
        
        # Se rostos foram detectados, emite notificação
        if face_names:
            emit('face_detected', {
                'camera_id': camera_id,
                'camera_name': camera.name,
                'establishment_name': camera.establishment.name,
                'faces': face_names,
                'timestamp': datetime.utcnow().isoformat()
            }, room=f"user_{current_user.id}")
        
    except Exception as e:
        print(f"Erro no processamento do stream: {e}")
        emit('error', {'message': f'Erro no processamento: {str(e)}'})

@socketio.on('start_camera')
def handle_start_camera(data):
    """Inicia stream de uma câmera específica"""
    if not current_user.is_authenticated:
        return
    
    camera_id = data.get('camera_id')
    camera = Camera.query.join(Establishment).filter(
        Camera.id == camera_id,
        Establishment.user_id == current_user.id
    ).first()
    
    if camera:
        join_room(f"camera_{camera_id}")
        active_cameras[camera_id] = {
            'user_id': current_user.id,
            'session_id': request.sid,
            'last_update': datetime.utcnow(),
            'face_count': 0
        }
        
        # Inicia thread de streaming se não estiver já rodando
        if camera_id not in camera_threads:
            camera_threads[camera_id] = {'stop': False}
            thread = threading.Thread(target=stream_camera, args=(camera_id, current_user.id), daemon=True)
            thread.start()
        
        emit('camera_started', {
            'camera_id': camera_id, 
            'camera_name': camera.name,
            'message': f'Câmera {camera.name} iniciada'
        })
        print(f"Câmera {camera_id} ({camera.name}) iniciada pelo usuário {current_user.username}")

@socketio.on('stop_camera')
def handle_stop_camera(data):
    """Para stream de uma câmera específica"""
    camera_id = data.get('camera_id')
    
    if camera_id in active_cameras:
        del active_cameras[camera_id]
    
    # Para a thread de streaming
    if camera_id in camera_threads:
        camera_threads[camera_id]['stop'] = True
        del camera_threads[camera_id]
    
    leave_room(f"camera_{camera_id}")
    emit('camera_stopped', {
        'camera_id': camera_id,
        'message': f'Câmera {camera_id} parada'
    })
    print(f"Câmera {camera_id} parada pelo usuário {current_user.username if current_user.is_authenticated else 'Anônimo'}")

@socketio.on('get_active_cameras')
def handle_get_active_cameras():
    """Retorna lista de câmeras ativas do usuário"""
    if not current_user.is_authenticated:
        return
    
    user_active_cameras = [
        {
            'camera_id': cam_id,
            'last_update': cam_info['last_update'].isoformat(),
            'face_count': cam_info['face_count']
        }
        for cam_id, cam_info in active_cameras.items()
        if cam_info.get('user_id') == current_user.id
    ]
    
    emit('active_cameras_list', {'cameras': user_active_cameras})

# Task periódica para limpar câmeras inativas
def cleanup_inactive_cameras():
    """Remove câmeras que não enviaram dados há mais de 1 minuto"""
    with app.app_context():  # Contexto da aplicação para thread
        cutoff_time = datetime.utcnow() - timedelta(minutes=1)
        cameras_to_remove = [
            cam_id for cam_id, cam_info in active_cameras.items()
            if cam_info['last_update'] < cutoff_time
        ]
        
        for cam_id in cameras_to_remove:
            del active_cameras[cam_id]
            # Para também a thread de streaming se existir
            if cam_id in camera_threads:
                camera_threads[cam_id]['stop'] = True
                del camera_threads[cam_id]
            print(f"Câmera {cam_id} removida por inatividade")

def stream_camera(camera_id, user_id):
    """Thread function para streaming contínuo de uma câmera"""
    with app.app_context():  # IMPORTANTE: Contexto da aplicação para threads
        cap = None
        try:
            camera = Camera.query.get(camera_id)
            if not camera:
                print(f"Câmera {camera_id} não encontrada")
                return
            
            # Configura a fonte da câmera
            try:
                source = int(camera.camera_source)
            except ValueError:
                source = camera.camera_source
            
            # Se a URL não tem formato completo, adiciona /video
            if isinstance(source, str) and source.startswith('http') and not source.endswith('/video'):
                if not source.endswith('/'):
                    source += '/'
                source += 'video'
            
            print(f"Tentando conectar à câmera: {source}")
            
            # Configurações otimizadas para OpenCV
            cap = cv2.VideoCapture(source)
            
            # Configurações específicas para streams HTTP/MJPEG
            if isinstance(source, str) and source.startswith('http'):
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo para reduzir latência
                cap.set(cv2.CAP_PROP_FPS, 25)  # 25 FPS para streams HTTP (mais estável)
            else:
                # Configurações para câmeras locais
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo também para locais
            
            if not cap.isOpened():
                print(f"Erro: Não foi possível abrir a câmera {source}")
                return
            
            # Configura a câmera com resolução otimizada para fluidez
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Resolução equilibrada
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Resolução equilibrada
            cap.set(cv2.CAP_PROP_FPS, 25)
            
            # Obtém engine de reconhecimento facial
            if user_id not in face_engines:
                face_engines[user_id] = FaceRecognitionEngine(user_id, app)
            
            engine = face_engines[user_id]
            frame_count = 0
            consecutive_failures = 0
            max_failures = 3
            
            # Sistema de threading para processamento paralelo
            latest_frame = None
            latest_detections = {'faces': [], 'ids': [], 'locations': []}
            frame_lock = threading.Lock()
            processing_active = True
            
            def face_detection_worker():
                """Worker thread para processar detecção de rostos em paralelo"""
                nonlocal latest_frame, latest_detections, processing_active
                
                while processing_active and camera_id in active_cameras:
                    try:
                        with frame_lock:
                            current_frame = latest_frame.copy() if latest_frame is not None else None
                        
                        if current_frame is not None:
                            # Usa o engine diretamente para processar o frame
                            # Isso garante que toda a lógica de identificação funcione
                            processed_frame, face_names, face_ids = engine.process_frame(current_frame, camera_id)
                            
                            # Extrai as localizações dos rostos se disponível
                            face_locations = []
                            if hasattr(engine, 'last_face_locations') and engine.last_face_locations:
                                face_locations = engine.last_face_locations.copy()
                            else:
                                # Fallback: detecta localizações básicas
                                small_frame = cv2.resize(current_frame, (0, 0), fx=0.25, fy=0.25)
                                rgb_small_frame = small_frame[:, :, ::-1]
                                locations = face_recognition.face_locations(rgb_small_frame)
                                # Escala de volta para tamanho original
                                face_locations = [(top*4, right*4, bottom*4, left*4) 
                                                for top, right, bottom, left in locations]
                            
                            # Atualiza detecções thread-safe
                            with frame_lock:
                                latest_detections['faces'] = face_names.copy()
                                latest_detections['ids'] = face_ids.copy()
                                latest_detections['locations'] = face_locations.copy()
                        
                        time.sleep(0.15)  # Processa detecção a cada 150ms (mais estável)
                    except Exception as e:
                        print(f"Erro no worker de detecção: {e}")
                        time.sleep(0.5)
            
            # Inicia thread de detecção em paralelo
            detection_thread = threading.Thread(target=face_detection_worker, daemon=True)
            detection_thread.start()
            
            print(f"Streaming iniciado para câmera {camera_id}")
            
            while camera_id in active_cameras and not camera_threads.get(camera_id, {}).get('stop', False):
                # Verifica se foi solicitada parada temporária (ex: durante captura)
                camera_key = f"{user_id}_{camera_id}"
                if camera_key in active_cameras and active_cameras[camera_key].get('stop_requested', False):
                    print(f"⏸️ Pausa temporária solicitada para câmera {camera_id}")
                    time.sleep(1)
                    continue
                
                ret, frame = cap.read()
                if not ret:
                    consecutive_failures += 1
                    print(f"Erro na captura do frame da câmera {camera_id} (falhas: {consecutive_failures})")
                    
                    if consecutive_failures >= max_failures:
                        print(f"Muitas falhas consecutivas na câmera {camera_id}, tentando reconectar...")
                        cap.release()
                        time.sleep(1)
                        
                        # Tenta reconectar
                        cap = cv2.VideoCapture(source)
                        if isinstance(source, str) and source.startswith('http'):
                            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            cap.set(cv2.CAP_PROP_FPS, 25)  # 25 FPS para reconexão HTTP
                        else:
                            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        if cap.isOpened():
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            cap.set(cv2.CAP_PROP_FPS, 25)
                            consecutive_failures = 0
                            print(f"Reconexão bem-sucedida para câmera {camera_id}")
                        else:
                            print(f"Falha na reconexão da câmera {camera_id}")
                            break
                    
                    time.sleep(0.1)  # Sleep reduzido para falhas
                    continue
                
                consecutive_failures = 0
                
                try:
                    # Atualiza frame para thread de detecção
                    with frame_lock:
                        latest_frame = frame.copy()
                        # Pega as últimas detecções disponíveis
                        current_faces = latest_detections['faces'].copy()
                        current_ids = latest_detections['ids'].copy()
                        current_locations = latest_detections['locations'].copy()
                    
                    # SEMPRE envia o frame atual (stream contínua)
                    # Mas desenha as detecções mais recentes sobre ele
                    display_frame = frame.copy()
                    
                    # Se há detecções, desenha os contornos no frame atual
                    if len(current_faces) > 0 and len(current_locations) > 0:
                        # Desenha retângulos e nomes para cada rosto detectado
                        for i, (name, location) in enumerate(zip(current_faces, current_locations)):
                            if i < len(current_locations):
                                top, right, bottom, left = location
                                
                                # Define cor baseada no nome: verde para conhecidos, vermelho para desconhecidos
                                if name == "Desconhecido" or name.startswith("Desconhecido"):
                                    color = (0, 0, 255)  # Vermelho para desconhecidos
                                    confidence_text = "Novo"
                                else:
                                    color = (0, 255, 0)  # Verde para conhecidos
                                    confidence_text = "Conhecido"
                                
                                # Desenha retângulo ao redor do rosto
                                cv2.rectangle(display_frame, (left, top), (right, bottom), color, 2)
                                
                                # Desenha fundo para o texto
                                cv2.rectangle(display_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                                
                                # Desenha o nome
                                font = cv2.FONT_HERSHEY_DUPLEX
                                cv2.putText(display_frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
                                
                                # Desenha status no canto superior da caixa
                                cv2.rectangle(display_frame, (left, top - 20), (left + 80, top), color, cv2.FILLED)
                                cv2.putText(display_frame, confidence_text, (left + 2, top - 5), font, 0.4, (255, 255, 255), 1)
                    
                    # Converte frame para base64 - frame com contornos
                    _, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Atualiza informações da câmera ativa
                    if camera_id in active_cameras:
                        active_cameras[camera_id]['last_update'] = datetime.utcnow()
                        active_cameras[camera_id]['face_count'] = len(current_faces)
                    
                    # Envia frame via Socket.IO com detecções mais recentes
                    socketio.emit('processed_frame', {
                        'camera_id': camera_id,
                        'image': frame_base64,
                        'faces': current_faces,
                        'face_count': len(current_faces)
                    }, room=f"camera_{camera_id}")
                    
                    frame_count += 1
                    time.sleep(0.025)  # ~40 FPS para máxima fluidez
                    
                except Exception as e:
                    print(f"Erro no processamento do frame da câmera {camera_id}: {e}")
                    time.sleep(0.5)
            
            print(f"Streaming parado para câmera {camera_id}")
            
        except Exception as e:
            print(f"Erro na thread de streaming da câmera {camera_id}: {e}")
        finally:
            # Para thread de detecção
            processing_active = False
            if 'detection_thread' in locals():
                detection_thread.join(timeout=1)
            
            # Limpa recursos
            if cap:
                cap.release()
            if camera_id in camera_threads:
                del camera_threads[camera_id]

# Executa limpeza a cada 2 minutos
def start_cleanup_thread():
    def cleanup_loop():
        while True:
            time.sleep(120)  # 2 minutos
            cleanup_inactive_cameras()
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    print("Thread de limpeza de câmeras iniciada")

# --- INICIALIZAÇÃO ---
def create_tables():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    start_cleanup_thread()  # Inicia thread de limpeza
    print("🚀 Iniciando Sistema de Reconhecimento Facial...")
    print("📊 Dashboard: http://localhost:5000")
    print("⚠️  Para usar câmeras, execute também o camera_client.py")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)