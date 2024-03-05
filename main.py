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


def validate_email(email):
    email_regex = r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
    return bool(re.match(email_regex, email, re.IGNORECASE))

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    if not email or not password:
        return JSONResponse(content={'error': "Missing Fields"}, status_code=422)

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return JSONResponse(content={'error': "Invalid username or password"}, status_code=401)

    stored_password = user[3]
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return JSONResponse(content={'error': "Invalid username or password"}, status_code=401)
    user_id = user[0]
    print(user_id)
    return JSONResponse(content={'user_id': user_id}, status_code=200)

def connect_to_mqtt(user_id, ipAddress, port):
    mqtt_clients[user_id] = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    mqtt_clients[user_id].connect(ipAddress, port, 60)
    mqtt_clients[user_id].loop_start()
    print(f"{user_id} connected to {ipAddress} on port no. {port}")

@app.post("/connect")
async def connect(user_id : str = Form(...)):
    try:
        connect_to_mqtt(user_id, "192.168.1.94", 1883)
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
        mqtt_clients[user_id].publish(topic, message)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Error: ", traceback_str)

@app.post("/switch")
async def switch(user_id : str = Form(...), switchNum : int = Form(...), message : str=Form(...)):
    try:
        send_message(user_id, f'prism/board1/switch{switchNum}',message)
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


