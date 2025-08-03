from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError
from models import User, Establishment, Camera

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Cadastrar')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Escolha outro.')

class EstablishmentForm(FlaskForm):
    name = StringField('Nome do Estabelecimento', validators=[DataRequired(), Length(min=2, max=120)])
    submit = SubmitField('Salvar')

class CameraForm(FlaskForm):
    name = StringField('Nome da Câmera', validators=[DataRequired(), Length(min=2, max=120)])
    camera_source = StringField('Fonte da Câmera', validators=[DataRequired()], 
                               render_kw={"placeholder": "Ex: 0 para webcam, ou URL do stream"})
    establishment_id = SelectField('Estabelecimento', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Salvar')
    
    def __init__(self, user_id, *args, **kwargs):
        super(CameraForm, self).__init__(*args, **kwargs)
        self.establishment_id.choices = [(e.id, e.name) for e in 
                                       Establishment.query.filter_by(user_id=user_id).all()]

class FaceRegisterForm(FlaskForm):
    name = StringField('Nome da Pessoa', validators=[DataRequired(), Length(min=2, max=120)])
    camera_id = SelectField('Câmera para Captura', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Cadastrar Rosto')
    
    def __init__(self, user_id, *args, **kwargs):
        super(FaceRegisterForm, self).__init__(*args, **kwargs)
        # Busca todas as câmeras dos estabelecimentos do usuário
        user_establishments = Establishment.query.filter_by(user_id=user_id).all()
        cameras = []
        for est in user_establishments:
            for camera in est.cameras:
                cameras.append((camera.id, f"{est.name} - {camera.name}"))
        self.camera_id.choices = cameras
