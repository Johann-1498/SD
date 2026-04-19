import logging
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app.api.models.user import User
from app import db
import uuid

auth_blueprint = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_blueprint.route('/register', methods=['POST'])
def register():
    post_data = request.get_json()
    if not post_data:
        return jsonify({'message': 'Invalid payload.'}), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    
    try:
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if not user:
            new_user = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Generate auth token
            auth_token = new_user.encode_auth_token()
            return jsonify({
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode() if isinstance(auth_token, bytes) else auth_token
            }), 201
        else:
            return jsonify({'message': 'Sorry. That user already exists.'}), 400
    except Exception as e:
        print(f"Exception during register: {e}")
        db.session.rollback()
        import traceback
        trace = traceback.format_exc()
        return jsonify({'message': 'Try again.', 'error': str(e), 'trace': trace}), 500

@auth_blueprint.route('/login', methods=['POST'])
def login():
    post_data = request.get_json()
    if not post_data:
        return jsonify({'message': 'Invalid payload.'}), 400
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            auth_token = user.encode_auth_token()
            return jsonify({
                'message': 'Successfully logged in.',
                'auth_token': auth_token.decode() if isinstance(auth_token, bytes) else auth_token
            }), 200
        else:
            return jsonify({'message': 'User does not exist or wrong password.'}), 404
    except Exception as e:
        return jsonify({'message': 'Try again.'}), 500

@auth_blueprint.route('/forgot-password', methods=['POST'])
def forgot_password():
    post_data = request.get_json()
    email = post_data.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
        reset_token = str(uuid.uuid4())
        user.reset_token = reset_token
        db.session.commit()
        from flask import current_app
        from app import mail
        from flask_mail import Message
        
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        msg = Message('UNSA Portal - Recuperar cuenta', sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])
        msg.body = f"Has solicitado recuperar tu cuenta. Ingresa al siguiente enlace para generar una nueva contraseña:\n\n{reset_link}"
        msg.html = f"<p>Has solicitado recuperar tu cuenta. Haz clic en el enlace de abajo para restablecerla:</p><p><a href='{reset_link}'>{reset_link}</a></p>"
        
        try:
            mail.send(msg)
            current_app.logger.warning(f"PASSWORD RESET EMAIL SENT TO {email}: {reset_link}")
            return jsonify({'message': 'Se ha enviado el enlace mágico a tu correo.'}), 200
        except Exception as e:
            current_app.logger.error(f"Error sending email: {e}")
            return jsonify({'message': 'Error enviando el correo. Verifica las credenciales SMTP en el panel de configuración.'}), 500
    return jsonify({'message': 'User not found.'}), 404

@auth_blueprint.route('/reset-password', methods=['POST'])
def reset_password():
    post_data = request.get_json()
    token = post_data.get('token')
    new_password = post_data.get('password')
    if not token or not new_password:
         return jsonify({'message': 'Token and new password required.'}), 400
         
    user = User.query.filter_by(reset_token=token).first()
    if user:
        user.password_hash = User(username='tmp', email='tmp', password=new_password).password_hash
        user.reset_token = None
        db.session.commit()
        return jsonify({'message': 'Password successfully updated.'}), 200
    return jsonify({'message': 'Invalid token.'}), 400

@auth_blueprint.route('/me', methods=['GET'])
def get_user_status():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            user = User.query.filter_by(id=resp).first()
            return jsonify({
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username
                }
            }), 200
        return jsonify({'message': resp}), 401
    else:
        return jsonify({'message': 'Provide a valid auth token.'}), 401
