from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import numpy as np

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Aumentado para 255 caracteres
    
    # Relacionamentos
    establishments = db.relationship('Establishment', backref='owner', lazy=True, cascade='all, delete-orphan')
    known_faces = db.relationship('KnownFace', backref='owner', lazy=True, cascade='all, delete-orphan')

class Establishment(db.Model):
    __tablename__ = 'establishments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    cameras = db.relationship('Camera', backref='establishment', lazy=True, cascade='all, delete-orphan')

class Camera(db.Model):
    __tablename__ = 'cameras'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    camera_source = db.Column(db.String(255), nullable=False)
    establishment_id = db.Column(db.Integer, db.ForeignKey('establishments.id'), nullable=False)
    
    # Relacionamentos
    sightings = db.relationship('Sighting', backref='camera', lazy=True, cascade='all, delete-orphan')

class KnownFace(db.Model):
    __tablename__ = 'known_faces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    face_encoding = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relacionamentos
    sightings = db.relationship('Sighting', backref='face', lazy=True, cascade='all, delete-orphan')
    
    def get_face_encoding(self):
        """Converte o BLOB em numpy array"""
        return np.frombuffer(self.face_encoding, dtype=np.float64)
    
    def set_face_encoding(self, encoding):
        """Converte numpy array em BLOB"""
        self.face_encoding = encoding.astype(np.float64).tobytes()

class Sighting(db.Model):
    __tablename__ = 'sightings'
    id = db.Column(db.Integer, primary_key=True)
    face_id = db.Column(db.Integer, db.ForeignKey('known_faces.id'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('cameras.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
