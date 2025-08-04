import cv2
import face_recognition
import numpy as np
from models import KnownFace, Sighting, Camera
from datetime import datetime, timedelta
import base64
import threading
import time

class FaceRecognitionEngine:
    def __init__(self, user_id, app=None):
        self.user_id = user_id
        self.app = app  # Referência ao app Flask
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        self.last_detection_times = {}  # Para evitar detecções duplicadas
        self.last_face_locations = []  # Para armazenar localizações dos rostos
        self.lock = threading.Lock()  # Para thread safety
        if app:
            with app.app_context():
                self.load_known_faces()
        else:
            self.load_known_faces()
    
    def load_known_faces(self):
        """Carrega os rostos conhecidos do usuário do banco de dados"""
        with self.lock:
            faces = KnownFace.query.filter_by(user_id=self.user_id).all()
            self.known_face_encodings = []
            self.known_face_names = []
            self.known_face_ids = []
            
            for face in faces:
                try:
                    encoding = face.get_face_encoding()
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(face.name)
                    self.known_face_ids.append(face.id)
                except Exception as e:
                    print(f"Erro ao carregar rosto {face.id}: {e}")
            
            print(f"Carregados {len(self.known_face_names)} rostos conhecidos para usuário {self.user_id}")
    
    def process_frame(self, frame, camera_id):
        """Processa um frame e retorna o frame com as detecções"""
        from models import db
        
        # Redimensiona para processamento mais rápido
        scale_factor = 0.5  # Melhor escala para manter precisão
        small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Encontra rostos
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        # Escala localizações de volta para tamanho original
        scaled_locations = []
        for top, right, bottom, left in face_locations:
            scaled_locations.append((
                int(top / scale_factor),
                int(right / scale_factor), 
                int(bottom / scale_factor),
                int(left / scale_factor)
            ))
        
        # Armazena localizações para uso em threads
        self.last_face_locations = scaled_locations.copy()
        
        face_names = []
        detected_face_ids = []
        
        current_time = datetime.utcnow()
        
        for face_encoding in face_encodings:
            name = "Desconhecido"
            face_id = None
            
            with self.lock:
                if len(self.known_face_encodings) > 0:
                    # Calcula distâncias
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    # Verifica se a melhor correspondência está dentro do limite
                    if face_distances[best_match_index] < 0.6:  # Limite mais flexível para melhor detecção
                        name = self.known_face_names[best_match_index]
                        face_id = self.known_face_ids[best_match_index]
                        
                        # Calcula confiança (1 - distância, normalizado para 0-1)
                        confidence = max(0.0, 1.0 - face_distances[best_match_index])
                        
                        # Registra o avistamento com sessão inteligente
                        self.register_sighting_with_session(face_id, camera_id, current_time, confidence)
            
            face_names.append(name)
            detected_face_ids.append(face_id)
        
        # Não desenha mais aqui - será feito no app.py para controle total das cores
        return frame, face_names, detected_face_ids
    
    def draw_detections(self, frame, face_locations, face_names, scale_factor):
        """Desenha as caixas e nomes dos rostos no frame"""
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Escala de volta para o tamanho original
            top = int(top / scale_factor)
            right = int(right / scale_factor)
            bottom = int(bottom / scale_factor)
            left = int(left / scale_factor)
            
            # Cor da caixa: verde para conhecidos, vermelho para desconhecidos
            if name.startswith("Desconhecido"):
                color = (0, 0, 255)  # Vermelho
                confidence_text = "Novo"
            else:
                color = (0, 255, 0)  # Verde
                confidence_text = "Conhecido"
            
            # Desenha retângulo
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Desenha fundo do texto
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Desenha o nome
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
            
            # Desenha status no canto superior da caixa
            cv2.rectangle(frame, (left, top - 20), (left + 80, top), color, cv2.FILLED)
            cv2.putText(frame, confidence_text, (left + 2, top - 5), font, 0.4, (255, 255, 255), 1)
    
    def register_sighting_throttled(self, face_id, camera_id, current_time):
        """Registra um avistamento com sistema de sessões inteligente para evitar spam"""
        # Registra o avistamento usando o novo sistema de sessões
        self.register_sighting_with_session(face_id, camera_id, current_time)
    
    def register_sighting_with_session(self, face_id, camera_id, timestamp=None, confidence=0.95):
        """Registra um avistamento usando sistema de sessões para evitar spam"""
        from models import db
        
        def _register_with_session():
            try:
                current_timestamp = timestamp if timestamp is not None else datetime.utcnow()
                
                # Procura por uma sessão ativa (últimos 5 minutos sem session_end)
                active_session = Sighting.query.filter(
                    Sighting.face_id == face_id,
                    Sighting.camera_id == camera_id,
                    Sighting.session_end.is_(None),
                    Sighting.session_start >= current_timestamp - timedelta(minutes=5)
                ).first()
                
                if active_session:
                    # Atualiza sessão existente
                    active_session.detection_count += 1
                    active_session.timestamp = current_timestamp  # Última detecção
                    
                    # Atualiza confiança média
                    total_confidence = (active_session.confidence_avg * (active_session.detection_count - 1)) + confidence
                    active_session.confidence_avg = total_confidence / active_session.detection_count
                    
                    # Se passou mais de 2 minutos desde a última detecção, encerra a sessão anterior
                    if (current_timestamp - active_session.timestamp).total_seconds() > 120:
                        active_session.session_end = active_session.timestamp
                        
                        # Cria nova sessão
                        return self._create_new_session(face_id, camera_id, current_timestamp, confidence)
                    
                    db.session.commit()
                    return True
                else:
                    # Cria nova sessão
                    return self._create_new_session(face_id, camera_id, current_timestamp, confidence)
                    
            except Exception as e:
                print(f"Erro ao registrar avistamento com sessão: {e}")
                db.session.rollback()
                return False
        
        if self.app:
            with self.app.app_context():
                return _register_with_session()
        else:
            return _register_with_session()
    
    def _create_new_session(self, face_id, camera_id, timestamp, confidence):
        """Cria uma nova sessão de avistamento"""
        from models import db
        
        try:
            # Verifica se é um rosto conhecido ou desconhecido
            face = KnownFace.query.get(face_id)
            is_unknown = face and face.name.startswith('Desconhecido_')
            
            sighting = Sighting(
                face_id=face_id,
                camera_id=camera_id,
                timestamp=timestamp,
                session_start=timestamp,
                session_end=None,  # Sessão ativa
                detection_count=1,
                confidence_avg=confidence,
                is_unknown=is_unknown
            )
            
            db.session.add(sighting)
            db.session.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao criar nova sessão: {e}")
            db.session.rollback()
            return False
    
    def create_unknown_face(self, face_encoding):
        """Cria um novo rosto desconhecido no banco"""
        from models import db
        
        def _create_unknown():
            try:
                # Verifica se já existe um rosto muito similar
                with self.lock:
                    for known_encoding in self.known_face_encodings:
                        distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                        if distance < 0.5:
                            return None  # Já existe um rosto similar
                
                # Conta quantos desconhecidos já existem
                unknown_count = KnownFace.query.filter(
                    KnownFace.user_id == self.user_id,
                    KnownFace.name.like('Desconhecido_%')
                ).count()
                
                new_face = KnownFace(
                    name=f"Desconhecido_{unknown_count + 1}",
                    user_id=self.user_id
                )
                new_face.set_face_encoding(face_encoding)
                
                db.session.add(new_face)
                db.session.commit()
                
                # Atualiza a lista local
                self.load_known_faces()
                
                print(f"Novo rosto desconhecido criado: {new_face.name} (ID: {new_face.id})")
                return new_face.id
            except Exception as e:
                print(f"Erro ao criar rosto desconhecido: {e}")
                db.session.rollback()
                return None
        
        if self.app:
            with self.app.app_context():
                return _create_unknown()
        else:
            return _create_unknown()
    
    def register_sighting(self, face_id, camera_id, timestamp=None):
        """Registra um avistamento no banco de dados"""
        from models import db
        
        def _register_sighting():
            try:
                if timestamp is None:
                    timestamp = datetime.utcnow()
                
                sighting = Sighting(
                    face_id=face_id,
                    camera_id=camera_id,
                    timestamp=timestamp
                )
                db.session.add(sighting)
                db.session.commit()
                
                return True
            except Exception as e:
                print(f"Erro ao registrar avistamento: {e}")
                db.session.rollback()
                return False
        
        if self.app:
            with self.app.app_context():
                return _register_sighting()
        else:
            return _register_sighting()
    
    def capture_face_from_camera(self, camera_id):
        """Captura um rosto de uma câmera específica para cadastro"""
        def _capture_face():
            camera = Camera.query.get(camera_id)
            if not camera:
                return None, "Câmera não encontrada"
            
            try:
                print(f"🎥 Iniciando captura da câmera {camera_id}: {camera.camera_source}")
                
                # Tenta converter camera_source para int (webcam) ou usar como string (URL)
                try:
                    source = int(camera.camera_source)
                    print(f"📹 Usando webcam local: {source}")
                except ValueError:
                    source = camera.camera_source
                    # Para câmeras IP, adiciona /video se não estiver presente (mesmo que o streaming)
                    if isinstance(source, str) and source.startswith('http') and not source.endswith('/video'):
                        if not source.endswith('/'):
                            source += '/'
                        source += 'video'
                    print(f"🌐 Usando câmera IP: {source}")
                
                cap = cv2.VideoCapture(source)
                
                # Configurações específicas para câmeras IP
                if isinstance(source, str) and source.startswith('http'):
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    cap.set(cv2.CAP_PROP_FPS, 10)
                    # Timeout para câmeras IP
                    cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 10000)  # 10 segundos
                    cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 10000)  # 10 segundos
                
                if not cap.isOpened():
                    print(f"❌ Primeira tentativa falhou. Tentando novamente...")
                    # Tenta novamente com configurações diferentes
                    cap = cv2.VideoCapture(source)
                    if isinstance(source, str) and source.startswith('http'):
                        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                        cap.set(cv2.CAP_PROP_FPS, 5)
                    
                    if not cap.isOpened():
                        print(f"❌ Falha ao abrir a câmera após 2 tentativas: {source}")
                        return None, "Não foi possível abrir a câmera. Verifique se ela está disponível e funcionando corretamente."
                
                print(f"✅ Câmera aberta com sucesso!")
                
                # Configura qualidade da captura
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                print("📷 Capturando frames para estabilizar...")
                # Captura alguns frames para estabilizar
                stable_frame = None
                for i in range(10):  # Reduzido para ser mais rápido
                    ret, frame = cap.read()
                    if not ret:
                        cap.release()
                        print(f"❌ Erro na captura do frame {i+1}/10")
                        return None, f"Erro na captura do frame {i+1}/10"
                    stable_frame = frame
                    time.sleep(0.1)
                
                print("🔍 Processando detecção de rosto...")
                
                # Processa o frame para encontrar rostos
                rgb_frame = cv2.cvtColor(stable_frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame, model="hog")
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                cap.release()
                print("📸 Câmera liberada após captura")
                
                if len(face_encodings) == 0:
                    print("⚠️ Nenhum rosto detectado")
                    return None, "Nenhum rosto detectado. Certifique-se de estar bem posicionado na frente da câmera com boa iluminação."
                
                if len(face_encodings) > 1:
                    print(f"⚠️ Múltiplos rostos detectados: {len(face_encodings)}")
                    return None, "Múltiplos rostos detectados. Certifique-se de que apenas uma pessoa esteja na frente da câmera."
                
                # Verifica se o rosto já está cadastrado
                face_encoding = face_encodings[0]
                with self.lock:
                    for i, known_encoding in enumerate(self.known_face_encodings):
                        distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                        if distance < 0.5:
                            print(f"⚠️ Rosto já cadastrado: {self.known_face_names[i]}")
                            return None, f"Este rosto já está cadastrado como: {self.known_face_names[i]}"
                
                print("✅ Novo rosto detectado, processando...")
                
                # Desenha uma caixa ao redor do rosto detectado
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(stable_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(stable_frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(stable_frame, "Rosto Detectado", (left + 6, bottom - 6), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                # Converte frame para base64 para enviar ao frontend
                _, buffer = cv2.imencode('.jpg', stable_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_b64 = base64.b64encode(buffer).decode('utf-8')
                
                print("✅ Rosto capturado com sucesso!")
                
                return {
                    'encoding': face_encoding,
                    'frame': frame_b64,
                    'location': face_locations[0]
                }, "Rosto capturado com sucesso! Agora digite um nome para cadastrá-lo."
                
            except Exception as e:
                print(f"❌ Erro detalhado na captura: {str(e)}")
                import traceback
                traceback.print_exc()
                return None, f"Erro ao capturar rosto: {str(e)}"
        
        if self.app:
            with self.app.app_context():
                return _capture_face()
        else:
            return _capture_face()
    
    def register_new_face(self, name, face_data):
        """Registra um novo rosto conhecido"""
        from models import db
        
        def _register_new_face():
            try:
                # Verifica se o nome já existe
                existing_face = KnownFace.query.filter_by(
                    name=name, user_id=self.user_id
                ).first()
                
                if existing_face:
                    return False, "Já existe uma pessoa cadastrada com este nome"
                
                new_face = KnownFace(
                    name=name,
                    user_id=self.user_id
                )
                new_face.set_face_encoding(face_data['encoding'])
                
                db.session.add(new_face)
                db.session.commit()
                
                # Atualiza a lista local
                self.load_known_faces()
                
                print(f"Novo rosto cadastrado: {name} (ID: {new_face.id})")
                return True, f"Rosto de {name} cadastrado com sucesso!"
            except Exception as e:
                db.session.rollback()
                return False, f"Erro ao cadastrar rosto: {str(e)}"
        
        if self.app:
            with self.app.app_context():
                return _register_new_face()
        else:
            return _register_new_face()
    
    def get_statistics(self):
        """Retorna estatísticas do sistema"""
        total_faces = len(self.known_face_names)
        unknown_faces = len([name for name in self.known_face_names if name.startswith('Desconhecido_')])
        known_faces = total_faces - unknown_faces
        
        # Avistamentos das últimas 24 horas
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_sightings = Sighting.query.join(KnownFace).filter(
            KnownFace.user_id == self.user_id,
            Sighting.timestamp >= yesterday
        ).count()
        
        return {
            'total_faces': total_faces,
            'known_faces': known_faces,
            'unknown_faces': unknown_faces,
            'recent_sightings': recent_sightings
        }
