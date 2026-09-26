from flask import Flask,render_template,request
from flask_socketio import SocketIO,join_room,leave_room,emit

app=Flask(__name__)
app.config['SECRET_KEY']='classified_agency_key_9988'
socketio=SocketIO(app,cors_allowed_origins="*")

ACTIVE_ROOMS={
"PHANTOM-7":{"password":"jule@7816","agents":0},
"HELIX-9":{"password":"#89@rookville","agents":0},
"TWINBRO-PEACE":{"password":"9/11*2001","agents":0}
}

CONNECTED={}

@app.route('/')
def index():
 return render_template('index.html')

@socketio.on('verify_room')
def verify(d):
 r=d.get('room','').strip().upper()
 p=d.get('password','').strip()
 a=d.get('agent','').strip()

 if not r or not p or not a:
  emit('auth_response',{
   'success':False,
   'error':'ALL FIELDS REQUIRED FOR CLEARANCE.'
  })
  return

 if r not in ACTIVE_ROOMS:
  ACTIVE_ROOMS[r]={'password':p,'agents':0}

 if ACTIVE_ROOMS[r]['password']==p:
  emit('auth_response',{
   'success':True,
   'room':r,
   'agent':a
  })
 else:
  emit('auth_response',{
   'success':False,
   'error':'ACCESS DENIED: INVALID CREDENTIALS.'
  })

def users(r):
 return [x['agent'] for x in CONNECTED.values() if x['room']==r]

def update(r):
 emit('room_user_count',{
  'count':ACTIVE_ROOMS[r]['agents'],
  'users':users(r)
 },to=r)

@socketio.on('join_secure_chat')
def join_chat(d):
 r=d.get('room')
 a=d.get('agent')

 if not r or not a or r not in ACTIVE_ROOMS:return
 if request.sid in CONNECTED:return

 join_room(r)

 CONNECTED[request.sid]={
  'room':r,
  'agent':a
 }

 ACTIVE_ROOMS[r]['agents']+=1

 emit('message',{
  'sender':'SYSTEM',
  'text':f'AGENT {a} HAS ESTABLISHED SECURE CONNECTION.',
  'system':True
 },to=r)

 update(r)

@socketio.on('send_message')
def message(d):
 r=d.get('room')
 a=d.get('agent')
 t=d.get('text','').strip()
 c=CONNECTED.get(request.sid)

 if not r or not a or not t or not c or c['room']!=r:return

 emit('message',{
  'sender':a,
  'text':t,
  'system':False
 },to=r)

def remove_agent():
 c=CONNECTED.pop(request.sid,None)

 if not c:return

 r=c['room']
 a=c['agent']

 leave_room(r)

 if r not in ACTIVE_ROOMS:return

 ACTIVE_ROOMS[r]['agents']=max(0,ACTIVE_ROOMS[r]['agents']-1)

 emit('message',{
  'sender':'SYSTEM',
  'text':f'AGENT {a} WENT DARK (DISCONNECTED).',
  'system':True
 },to=r)

 update(r)

@socketio.on('disconnect_agent')
def manual_disconnect(d):
 remove_agent()

@socketio.on('disconnect')
def disconnect():
 remove_agent()

if __name__=='__main__':
 socketio.run(app,debug=True,port=5000)
