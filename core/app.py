from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import cast, UUID
from pydub import AudioSegment
import uuid
import os

if not os.path.isdir('audio'):
    os.mkdir('audio')

app: Flask = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@db:5432/my_database'
db: SQLAlchemy = SQLAlchemy(app)

class User(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    user_identifier: str = db.Column(db.String(36), unique=True, nullable=False)
    access_token: str = db.Column(db.String(36), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f'<User {self.username}>'


class Audio(db.Model):
    id: uuid.UUID = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename: str = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f'<Audio {self.id}>'


@app.before_request
def create_tables() -> None:
    db.create_all()


@app.route('/upload_audio', methods=['POST'])
def upload_audio() -> dict:
    user_identifier: str = request.form.get('user_identifier')
    access_token: str = request.form.get('access_token')
    audio_file = request.files.get('audio')
    if not user_identifier or not access_token or not audio_file:
        return {'error': 'User identifier, access token, and audio file are required.'}, 400
    user = User.query.filter_by(user_identifier=user_identifier, access_token=access_token).first()
    if not user:
        return {'error': 'Invalid user credentials.'}, 401
    audio_id: uuid.UUID = uuid.uuid4()
    filename: str = f'{audio_id}.mp3'
    filepath: str = os.path.join('audio', filename)
    audio = AudioSegment.from_file(audio_file, format='wav')
    audio.export(filepath, format='mp3')
    audio_record = Audio(id=audio_id, user_id=user.id, filename=filename) 
    db.session.add(audio_record)
    db.session.commit()
    download_url: str = f'http://localhost:5100/record?id={audio_id}&user={user.id}'
    return {'message': 'Audio uploaded successfully.', 'download_url': download_url}, 200


@app.route('/create_user', methods=['POST'])
def create_user() -> dict:
    username: str = request.json.get('username')
    if not username:
        return jsonify({'error': 'Username is required.'}), 400
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists. Please choose a different username.'}), 409


    user_identifier: str = str(uuid.uuid4())
    access_token: str = str(uuid.uuid4())
    user = User(username=username, user_identifier=user_identifier, access_token=access_token)
    db.session.add(user)
    db.session.commit()
    return jsonify({'user_identifier': user_identifier, 'access_token': access_token}), 200


@app.route('/record', methods=['GET'])
def download_record() -> dict:
    audio_id: str = request.args.get('id')
    user_id: str = request.args.get('user')
    try:
        audio_id: uuid.UUID = uuid.UUID(audio_id)
    except ValueError:
        return {'error': 'Invalid audio ID.'}, 400
    try:
        user_id: int = int(user_id)
    except ValueError:
        return {'error': 'Invalid user ID.'}, 400
    audio_record = Audio.query.filter_by(id=cast(audio_id, UUID), user_id=user_id).first()
    if not audio_record:
        return {'error': 'Audio record not found.'}, 404
    filepath: str = os.path.join('audio', audio_record.filename)
    if not os.path.isfile(filepath):
        return {'error': 'File not found.'}, 404
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
