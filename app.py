from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'classified_agency_key_9988'
socketio = SocketIO(app, cors_allowed_origins="*")

ACTIVE_ROOMS = {
    "PHANTOM-7": {"password": "jule@7816", "agents": 0},
    "HELIX-9": {"password": "#89@rookville", "agents": 0},
    "TWINBRO-PEACE": {"password": "9/11*2001", "agents": 0},
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('verify_room')
def handle_verify_room(data):
    room = data.get('room', '').strip().upper()
    password = data.get('password', '').strip()
    agent_name = data.get('agent', '').strip()

    if not room or not password or not agent_name:
        emit('auth_response', {'success': False, 'error': 'ALL FIELDS REQUIRED FOR CLEARANCE.'})
        return

    if room not in ACTIVE_ROOMS:
        ACTIVE_ROOMS[room] = {'password': password, 'agents': 0}

    if ACTIVE_ROOMS[room]['password'] == password:
        emit('auth_response', {'success': True, 'room': room, 'agent': agent_name})
    else:
        emit('auth_response', {'success': False, 'error': 'ACCESS DENIED: INVALID CREDENTIALS.'})

@socketio.on('join_secure_chat')
def handle_join(data):
    room = data['room']
    agent = data['agent']
    join_room(room)
    ACTIVE_ROOMS[room]['agents'] += 1
    
    emit('message', {
        'sender': 'SYSTEM', 
        'text': f'AGENT {agent} HAS ESTABLISHED SECURE CONNECTION.',
        'timestamp': 'JUST NOW',
        'system': True
    }, to=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    sender = data['agent']
    text = data['text']
    
    emit('message', {
        'sender': sender,
        'text': text,
        'system': False
    }, to=room)

@socketio.on('disconnect_agent')
def handle_disconnect(data):
    room = data.get('room')
    agent = data.get('agent')
    if room and room in ACTIVE_ROOMS:
        leave_room(room)
        ACTIVE_ROOMS[room]['agents'] = max(0, ACTIVE_ROOMS[room]['agents'] - 1)
        emit('message', {
            'sender': 'SYSTEM',
            'text': f'AGENT {agent} WENT DARK (DISCONNECTED).',
            'system': True
        }, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
