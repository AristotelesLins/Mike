"""
Sistema de Gerenciamento de Câmeras
Este script permite iniciar múltiplas câmeras simultaneamente
"""

import subprocess
import sys
import time
import json
import os
from threading import Thread

class CameraManager:
    def __init__(self):
        self.processes = {}
        self.config_file = "cameras_config.json"
    
    def load_config(self):
        """Carrega configuração de câmeras do arquivo JSON"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config):
        """Salva configuração de câmeras no arquivo JSON"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def start_camera(self, camera_id, source, server="http://localhost:5000"):
        """Inicia uma câmera específica"""
        if camera_id in self.processes:
            print(f"Câmera {camera_id} já está rodando!")
            return False
        
        cmd = [
            sys.executable, "camera_client.py",
            "--camera-id", str(camera_id),
            "--source", str(source),
            "--server", server
        ]
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.processes[camera_id] = process
            print(f"✓ Câmera {camera_id} iniciada (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar câmera {camera_id}: {e}")
            return False
    
    def stop_camera(self, camera_id):
        """Para uma câmera específica"""
        if camera_id not in self.processes:
            print(f"Câmera {camera_id} não está rodando!")
            return False
        
        process = self.processes[camera_id]
        process.terminate()
        process.wait()
        del self.processes[camera_id]
        print(f"✓ Câmera {camera_id} parada")
        return True
    
    def stop_all(self):
        """Para todas as câmeras"""
        for camera_id in list(self.processes.keys()):
            self.stop_camera(camera_id)
    
    def list_cameras(self):
        """Lista câmeras ativas"""
        if not self.processes:
            print("Nenhuma câmera ativa")
            return
        
        print("Câmeras ativas:")
        for camera_id, process in self.processes.items():
            status = "Rodando" if process.poll() is None else "Parada"
            print(f"  - Câmera {camera_id}: {status} (PID: {process.pid})")
    
    def start_from_config(self):
        """Inicia todas as câmeras da configuração"""
        config = self.load_config()
        if not config.get('cameras'):
            print("Nenhuma câmera configurada")
            return
        
        for camera in config['cameras']:
            self.start_camera(
                camera['id'], 
                camera['source'], 
                config.get('server', 'http://localhost:5000')
            )

def main():
    manager = CameraManager()
    
    if len(sys.argv) < 2:
        print("Sistema de Gerenciamento de Câmeras")
        print()
        print("Uso:")
        print("  python camera_manager.py start <camera_id> <source>  # Inicia uma câmera")
        print("  python camera_manager.py stop <camera_id>            # Para uma câmera")
        print("  python camera_manager.py start-all                   # Inicia todas (config)")
        print("  python camera_manager.py stop-all                    # Para todas")
        print("  python camera_manager.py list                        # Lista câmeras ativas")
        print("  python camera_manager.py config                      # Configura câmeras")
        print()
        print("Exemplos:")
        print("  python camera_manager.py start 1 0                   # Webcam padrão")
        print("  python camera_manager.py start 2 1                   # Segunda webcam")
        print("  python camera_manager.py start 3 'http://ip:port'    # Câmera IP")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "start" and len(sys.argv) >= 4:
            camera_id = int(sys.argv[2])
            source = sys.argv[3]
            manager.start_camera(camera_id, source)
        
        elif command == "stop" and len(sys.argv) >= 3:
            camera_id = int(sys.argv[2])
            manager.stop_camera(camera_id)
        
        elif command == "start-all":
            manager.start_from_config()
        
        elif command == "stop-all":
            manager.stop_all()
        
        elif command == "list":
            manager.list_cameras()
        
        elif command == "config":
            print("Configurador de Câmeras")
            cameras = []
            
            while True:
                try:
                    camera_id = input("ID da câmera (ou 'q' para sair): ")
                    if camera_id.lower() == 'q':
                        break
                    
                    camera_id = int(camera_id)
                    source = input("Fonte (0 para webcam, URL para IP): ")
                    
                    cameras.append({"id": camera_id, "source": source})
                    print(f"✓ Câmera {camera_id} adicionada")
                    
                except KeyboardInterrupt:
                    break
                except ValueError:
                    print("ID inválido!")
            
            if cameras:
                config = {
                    "server": "http://localhost:5000",
                    "cameras": cameras
                }
                manager.save_config(config)
                print(f"✓ Configuração salva com {len(cameras)} câmeras")
        
        else:
            print("Comando inválido!")
    
    except KeyboardInterrupt:
        print("\nParando todas as câmeras...")
        manager.stop_all()

if __name__ == "__main__":
    main()
