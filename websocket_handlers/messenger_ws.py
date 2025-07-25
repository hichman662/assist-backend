from flask_socketio import SocketIO, emit, join_room
from flask import request

socketio = SocketIO(cors_allowed_origins="*")

# Dictionary to keep track of user_id → room
user_rooms = {}

@socketio.on('join')
def handle_join(data):
    user_id = data.get("user_id")
    if user_id:
        room = f"user_{user_id}"
        join_room(room)
        user_rooms[user_id] = room
        print(f"[Messenger] User {user_id} joined room {room}")
    else:
        print("[Messenger] Invalid join data:", data)

@socketio.on('send_message')
def handle_send_message(data):
    receiver_id = data.get("receiver_id")
    room = user_rooms.get(receiver_id)
    if room:
        emit("receive_message", data, room=room)
        print(f"[Messenger] Sent message to {room}")
    else:
        print(f"[Messenger] No room found for receiver_id {receiver_id}")
