# from fastapi import FastAPI, Form, UploadFile, File, Request, Response, HTTPException
# import mysql.connector
# from starlette.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# import traceback
# import re
# import bcrypt
# import paho.mqtt.client as mqtt

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# mysql_config = {
#     'host': '127.0.0.1',
#     'user': 'root',
#     'password': '',
#     'database': 'electrivity_server'
# }

# mqtt_clients={}

# connection = mysql.connector.connect(**mysql_config)
# print(connection)


# client = None

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

# @app.post("/register")
# async def register(email: str = Form(...), username: str = Form(...),password: str = Form(...), confirmpassword: str = Form(...)):
#     print("Received form data:")
#     print("Email:", email)
#     print("Username:", username)
#     print("Password:", password)
#     print("Confirm Password:", confirmpassword)
#     if not email or not username or not password or not confirmpassword:
#         return JSONResponse(content={'error': "Missing Fields"}, status_code=422)

#     if not validate_email(email):
#         return JSONResponse(content={'error': "Please Enter Correct Email"}, status_code=422)

#     if len(password) < 8:
#         return JSONResponse(content={'error': "Password length should be more than 8"}, status_code=422)

#     if password != confirmpassword:
#         return JSONResponse(content={'error': "Password not matched"}, status_code=422)
#     print("Check")
#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     user_exists = cursor.fetchone()
#     cursor.close()
#     if user_exists:
#         return JSONResponse(content={'error': "User already exists"}, status_code=500)
    
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     cursor = connection.cursor()
#     cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, hashed_password))
#     connection.commit()
#     cursor.close()

#     return JSONResponse(content={'message': "Successfully Registered"}, status_code=200)


# def validate_email(email):
#     email_regex = r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
#     return bool(re.match(email_regex, email, re.IGNORECASE))

# @app.post("/login")
# async def login(email: str = Form(...), password: str = Form(...)):
#     if not email or not password:
#         return JSONResponse(content={'error': "Missing Fields"}, status_code=422)

#     cursor = connection.cursor()
#     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#     user = cursor.fetchone()
#     cursor.close()

#     if not user:
#         return JSONResponse(content={'error': "Invalid username or password"}, status_code=401)

#     stored_password = user[3]
#     if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
#         return JSONResponse(content={'error': "Invalid username or password"}, status_code=401)
#     user_id = user[0]
#     print(user_id)
#     return JSONResponse(content={'user_id': user_id}, status_code=200)

# def connect_to_mqtt(user_id, ipAddress, port):
#     mqtt_clients[user_id] = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
#     mqtt_clients[user_id].connect(ipAddress, port, 60)
#     mqtt_clients[user_id].loop_start()
#     print(f"{user_id} connected to {ipAddress} on port no. {port}")

# @app.post("/connect")
# async def connect(user_id : str = Form(...)):
#     try:
#         connect_to_mqtt(user_id, "192.168.1.94", 1883)
#         return JSONResponse(content={'message': "Connected"}, status_code=200)
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         print("Error: ", traceback_str)
#         return JSONResponse(content={'error': str(e)}, status_code=500)
    
# @app.post("/disconnect")
# async def disconnect(user_id : str = Form(...)):
#     try:
#         if mqtt_clients[user_id]:
#             mqtt_clients[user_id].disconnect()
#             mqtt_clients[user_id].loop_stop()
#             return JSONResponse(content={'message': "Disconnected"}, status_code=200)
#         else:
#             return JSONResponse(content={'error': "Not connected to MQTT"}, status_code=500)
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         print("Error: ", traceback_str)
#         return JSONResponse(content={'error': str(e)}, status_code=500)

# def send_message(user_id, topic, message):
#     print(topic)
#     try:
#         mqtt_clients[user_id].publish(topic, message)
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         print("Error: ", traceback_str)

# @app.post("/switch")
# async def switch(user_id : str = Form(...), switchNum : int = Form(...), message : str=Form(...)):
#     try:
#         send_message(user_id, f'prism/board1/switch{switchNum}',message)
#         return JSONResponse(content={'message': "Topic Executed"}, status_code=200)
   
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         print("Error: ", traceback_str)
#         return JSONResponse(content={'error': str(e)}, status_code=500)
    
# def on_message(client, userdata, message):
#     try:
#         payload = message.payload.decode("utf-8")
#         print(f"Received message: {message.topic} {payload}")
#         if message.topic == "prism/board1/touch1":
#             print(str(message.payload))
#     except Exception as e:
#         traceback.print_exc()
    
# @app.get("/touch")
# async def touch():
#     try:
#         if client:
#             client.on_message = on_message
#             return JSONResponse(content={'message': "Touch API executed"}, status_code=200)
#         else:
#             return JSONResponse(content={'error': "Not connected to MQTT"}, status_code=500)
#     except Exception as e:
#         traceback_str = traceback.format_exc()
#         print("Error: ", traceback_str)
#         return JSONResponse(content={'error': str(e)}, status_code=500)

from fastapi import FastAPI, Form, UploadFile, File, Request, Response, HTTPException
import mysql.connector
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback
import re
import bcrypt
import paho.mqtt.client as mqtt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mysql_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'electrivity_server'
}

mqtt_clients={}

connection = mysql.connector.connect(**mysql_config)
print(connection)


client = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/register")
async def register(email: str = Form(...), username: str = Form(...),password: str = Form(...), confirmpassword: str = Form(...)):
    try:
        print("Received form data:")
        print("Email:", email)
        print("Username:", username)
        print("Password:", password)
        print("Confirm Password:", confirmpassword)
        if not email or not username or not password or not confirmpassword:
            return JSONResponse(content={'error': "Missing Fields"}, status_code=422)

        if not validate_email(email):
            return JSONResponse(content={'error': "Please Enter Correct Email"}, status_code=422)

        if len(password) < 8:
            return JSONResponse(content={'error': "Password length should be more than 8"}, status_code=422)

        if password != confirmpassword:
            return JSONResponse(content={'error': "Password not matched"}, status_code=422)
        print("Check")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_exists = cursor.fetchone()
        cursor.close()
        if user_exists:
            return JSONResponse(content={'error': "User already exists"}, status_code=500)
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, hashed_password))
        connection.commit()
        cursor.close()

        return JSONResponse(content={'message': "Successfully Registered"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)


def validate_email(email):
    email_regex = r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
    return bool(re.match(email_regex, email, re.IGNORECASE))

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        print("Email:", email)
        print("Password:", password)
        if not email or not password:
            return JSONResponse(content={'error': "Missing Fields"}, status_code=422)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return JSONResponse(content={'error': "Invalid username or password"}, status_code=401)

        stored_password = user[3]
        if bcrypt.checkpw(password.encode('utf-8') , stored_password.encode('utf-8')):
            return JSONResponse(content={'user_id': user[0], 'username':user[2]}, status_code=200)
        else:
            return JSONResponse(content={'error': "Password not matched"}, status_code=500)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

def connect_to_mqtt(user_id, ipAddress, port):

    mqtt_clients[user_id] = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    print(mqtt_clients)
    mqtt_clients[user_id].connect(ipAddress, port, 60)
    mqtt_clients[user_id].loop_start()
    print(f"{user_id} connected to {ipAddress} on port no. {port}")

@app.post("/connect")
async def connect(user_id : str = Form(...)):

    try:
        connect_to_mqtt(user_id, "192.168.1.80", 1883)
        return JSONResponse(content={'message': "Connected"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
@app.post("/disconnect")
async def disconnect(user_id : str = Form(...)):
    try:
        if mqtt_clients[user_id]:
            mqtt_clients[user_id].disconnect()
            mqtt_clients[user_id].loop_stop()
            return JSONResponse(content={'message': "Disconnected"}, status_code=200)
        else:
            return JSONResponse(content={'error': "Not connected to MQTT"}, status_code=500)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

def send_message(user_id, topic, message):
    print(topic)
    try:
        if str(user_id) not in mqtt_clients:
            raise KeyError(f"User ID {user_id} not found in MQTT clients")
        else:
            mqtt_clients[str(user_id)].publish(topic, message)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/switch")
async def switch(user_id : int = Form(...), switchNum : int = Form(...), switchId : int = Form(...), message : str=Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT switches.id, switches.state, boards.boardname, boards.id FROM switches INNER JOIN boards ON switches.boardid = boards.id WHERE switches.id = %s AND switches.switchId = %s", (switchNum, switchId))
        switch = cursor.fetchone()

        new_state = not switch[1]
        cursor.execute("UPDATE switches SET state = %s WHERE id = %s", (new_state, switchNum))
        connection.commit()
        cursor.close()
        print(switch[2])
        prefix = switch[2]+'/switch'
        send_message(user_id, f'{prefix}/{str(switchId)}',message)
        return JSONResponse(content={'message': "Topic Executed"}, status_code=200)
   
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)
    
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        print(f"Received message: {message.topic} {payload}")
        if message.topic == "prism/board1/touch1":
            print(str(message.payload))
    except Exception as e:
        traceback.print_exc()
    
@app.get("/touch")
async def touch():
    try:
        if client:
            client.on_message = on_message
            return JSONResponse(content={'message': "Touch API executed"}, status_code=200)
        else:
            return JSONResponse(content={'error': "Not connected to MQTT"}, status_code=500)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)
    




@app.get("/getBoards")
async def get_boards():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM boards")
    boards = cursor.fetchall()
    cursor.close()

    boards_list = [{"id": board[0], "boardname": board[1], "size": board[2], "available": board[3]} for board in boards]

    return JSONResponse(content={'boards': boards_list}, status_code=200)



@app.post("/roomused")
async def register_roomused(roomname: str = Form(...), boardid: int = Form(...)):
    print("Received form data:")
    print("Room Name:", roomname)
    print("Board ID:", boardid)

    cursor = connection.cursor()
    cursor.execute("INSERT INTO roomused (roomname, boardid) VALUES (%s, %s)", (roomname, boardid))
    connection.commit()
    cursor.close()

    return JSONResponse(content={'message': "Successfully Registered Room and Board"}, status_code=200)

@app.get("/getRooms")
async def get_rooms():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT rooms.id, rooms.roomname, boards.noOfAvailableSwitches,  boards.noOfSwitches, boards.id FROM rooms INNER JOIN boards ON rooms.boardid = boards.id")
        rooms = cursor.fetchall()
        cursor.close()
        print(rooms[0][3]-rooms[0][2])

        rooms_list = [{"id": room[0],"roomname": room[1], "switches": (room[3]-room[2]), "boardid": room[4]} for room in rooms]
        if not rooms:
            return JSONResponse(content={'error': "No rooms added"}, status_code=500)
        return JSONResponse(content={'rooms': rooms_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)



@app.post("/getSwitches")
async def get_switches(boardId: int = Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, switchId, name, state FROM switches WHERE boardid = %s", (boardId,))
        switches = cursor.fetchall()
        cursor.close()

        switches_list = [{"id": switch[0], "switchId": switch[1],"name": switch[2], "state": switch[3]} for switch in switches]
        if not switches:
            return JSONResponse(content={'error': "No switches added"}, status_code=500)
        return JSONResponse(content={'switches': switches_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/getAvailableBoards")
async def get_available_boards():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT boards.id, boards.boardname FROM boards LEFT JOIN rooms ON boards.id = rooms.boardid WHERE rooms.boardid IS NULL")
        available_boards = cursor.fetchall()
        cursor.close()

        available_boards_list = [{"id": board[0], "boardname": board[1]} for board in available_boards]

        return JSONResponse(content={'boards': available_boards_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/insertRoom")
async def insert_room(roomname: str = Form(...), boardid: int = Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO rooms (roomname, boardid) VALUES (%s, %s)", (roomname, boardid))
        connection.commit()
        cursor.close()
        
        return JSONResponse(content={'message': "Room inserted successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Error while adding room"}, status_code=500)

# @app.post("/getAvailableSwitches")
# async def get_switches(boardId: int = Form(...)):
#     cursor = connection.cursor()
#     cursor.execute("SELECT id, noOfAvailableSwitches FROM boards WHERE id = %s", (boardId,))
#     switch = cursor.fetchone()
#     cursor.close()

#     switches_list = [{"id": switch[0],"noOfSwitches": switch[1]}]

#     return JSONResponse(content={'switches': switches_list}, status_code=200)

@app.post("/getAvailableSwitches")
async def get_switches(boardId: int = Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, noOfSwitches, noOfAvailableSwitches FROM boards WHERE id = %s", (boardId,))
        switch = cursor.fetchone()
        cursor.close()

        print(switch)

        switches_list = [{"id": switch[0],"noOfSwitches": switch[1], "noOfAvailableSwitches": switch[2]}]
        if not switch:
            return JSONResponse(content={'error': "No Switches Available"}, status_code=500)
        return JSONResponse(content={'switches': switches_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/insertSwitch")
async def insert_switch(switchId: int = Form(...), name: str = Form(...), boardId: int = Form(...)):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO switches (switchId, state, boardid, name) VALUES (%s, %s, %s, %s)", (switchId, 0, boardId, name))
        cursor.execute("UPDATE boards SET noOfAvailableSwitches = noOfAvailableSwitches - 1 WHERE id = %s", (boardId,))
        connection.commit()
        cursor.close()
        
        return JSONResponse(content={'message': "Switch inserted successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Getting error while adding switch"}, status_code=500)


@app.post("/removeSwitch")
async def remove_switch(switchId: int = Form(...), boardId: int = Form(...)):
    print(switchId)
    print(boardId)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM switches WHERE switchId = %s AND boardid = %s", (switchId, boardId))
        connection.commit()
        cursor.execute("UPDATE boards SET noOfAvailableSwitches = noOfAvailableSwitches + 1 WHERE id = %s", (boardId,))
        connection.commit()
        cursor.close()
        return JSONResponse(content={'message': "Switch removed successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Getting error while removing switch"}, status_code=500)

@app.get("/fetchAllSwitchesStatistics")
async def fetch_all_switches_statistics():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT rooms.id, rooms.boardid, rooms.roomname, switches.name, switches.state FROM rooms INNER JOIN switches ON rooms.boardid = switches.boardid")
        switches_statistics = cursor.fetchall()
        cursor.close()

        switches_statistics_list = [{"id": row[0], "boardid": row[1], "roomname": row[2], "switch_name": row[3], "state": row[4]} for row in switches_statistics]
        if not switches_statistics:
            return JSONResponse(content={'error': "No rooms and switches added"}, status_code=500)
        return JSONResponse(content={'switches_statistics': switches_statistics_list}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.post("/deleteRoom")
async def delete_room(roomId: int = Form(...), boardId: int = Form(...)):
    print(roomId)
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM switches WHERE boardid = (SELECT boardid FROM rooms WHERE id = %s)", (roomId,))
        connection.commit()
        cursor.execute("DELETE FROM rooms WHERE id = %s", (roomId,))
        connection.commit()
        cursor.execute("UPDATE boards SET noOfAvailableSwitches = 4 WHERE id = %s", (boardId,))
        connection.commit()
        cursor.close()
        
        return JSONResponse(content={'message': "Room and associated switches deleted successfully"}, status_code=200)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)
        return JSONResponse(content={'error': "Getting error while deleting room"}, status_code=500)






    

