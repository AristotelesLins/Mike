import cv2
import socketio
import base64
import time
import argparse
import sys

# --- CONFIGURAÇÃO ---
sio = socketio.Client()
# Conecte ao seu servidor Flask-SocketIO
SERVER_ADDR = "http://localhost:5000"
FPS = 10 # Frames por segundo para enviar ao servidor

@sio.event
def connect():
    print('Conectado ao servidor!')

@sio.event
def disconnect():
    print('Desconectado do servidor.')

@sio.event
def connect_error(data):
    print(f'Erro na conexão: {data}')

def stream_video(camera_id, video_source):
    """Captura vídeo e envia frames para o servidor."""
    try:
        # Tenta converter para int (webcam) ou usar como string (URL)
        try:
            source = int(video_source)
        except ValueError:
            source = video_source
        
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"Erro: Não foi possível abrir a fonte de vídeo {video_source}")
            return

        print(f"Iniciando stream da câmera {camera_id} (fonte: {video_source})")
        
        # Inicia a câmera no servidor
        sio.emit('start_camera', {'camera_id': camera_id})
        
        frame_count = 0
        try:
            while True:
                success, frame = cap.read()
                if not success:
                    print("Fim do stream ou erro na captura.")
                    break

                # Codifica a imagem para JPG e depois para Base64
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                image_data = base64.b64encode(buffer).decode('utf-8')

                # Envia o frame para o servidor com o ID da câmera
                sio.emit('stream', {
                    'image': f"data:image/jpeg;base64,{image_data}",
                    'camera_id': camera_id
                })

                frame_count += 1
                if frame_count % (FPS * 10) == 0:  # Log a cada 10 segundos
                    print(f"Frames enviados: {frame_count}")

                # Controla o FPS
                time.sleep(1/FPS)
        except KeyboardInterrupt:
            print("\nParando stream...")
        finally:
            # Para a câmera no servidor
            sio.emit('stop_camera', {'camera_id': camera_id})
            cap.release()
            
    except Exception as e:
        print(f"Erro no stream: {e}")

def main():
    parser = argparse.ArgumentParser(description='Cliente de câmera para sistema de reconhecimento facial')
    parser.add_argument('--camera-id', type=int, required=True, 
                       help='ID da câmera no banco de dados')
    parser.add_argument('--source', required=True,
                       help='Fonte da câmera: 0 para webcam, ou URL de stream')
    parser.add_argument('--server', default=SERVER_ADDR,
                       help=f'Endereço do servidor (padrão: {SERVER_ADDR})')
    parser.add_argument('--fps', type=int, default=FPS,
                       help=f'Frames por segundo (padrão: {FPS})')
    
    args = parser.parse_args()
    
    global SERVER_ADDR, FPS
    SERVER_ADDR = args.server
    FPS = args.fps
    
    print(f"Conectando ao servidor: {SERVER_ADDR}")
    print(f"Câmera ID: {args.camera_id}")
    print(f"Fonte: {args.source}")
    print(f"FPS: {FPS}")
    
    try:
        sio.connect(SERVER_ADDR)
        stream_video(args.camera_id, args.source)
    except Exception as e:
        print(f"Não foi possível conectar ao servidor: {e}")
    finally:
        sio.disconnect()

if __name__ == '__main__':
    main()