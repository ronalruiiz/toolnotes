from datetime import date, datetime
from flask import Flask, render_template,request,redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import json
import uuid
from Models.AESCipher import AESCipher

auth = HTTPBasicAuth()

app = Flask(__name__)

user = 'ronal'
pw = 'Admin123456789.'
users = {
    user: generate_password_hash(pw)
}

#@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@app.route('/')
#@auth.login_required
def home():
    with open('Data/notes.json', "r") as file:
        notes = json.load(file)

    return render_template('index.html',data=notes)

@app.route('/decrypt/<uuid>',methods=['POST',"GET"])
def decrypt(uuid):
    with open('Data/notes.json', "r") as file:
        notes = json.load(file)
    for item in notes:
        if(item.get("uuid") == uuid):
            note = item
    
    if request.method == 'POST':
        msg = note.get("msg")
        password = request.form["password"]
        aes_cipher = AESCipher(password)
        msg = aes_cipher.decrypt(msg.encode("utf-8"))
        return render_template('decrypt.html',data={"note":item,"decrypt":msg})

    return render_template('decrypt.html',data={"note":item,"decrypt":""})

@app.route('/save-data',methods=['POST'])
def savedata():
    password = request.form["password"]
    msg = request.form["note"]
    encrypt = False
    if len(password) == 16 or len(password) == 32 :
        aes_cipher = AESCipher(password)
        msg = aes_cipher.encrypt(msg).decode('utf-8')
        encrypt = True
    data = {
        "uuid":str(uuid.uuid1()),
        "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "msg": msg,
        "encrypt":encrypt
    }

    with open('Data/notes.json', "r") as file:
        notes = json.load(file)

    notes.append(data)

    with open('Data/notes.json', 'w') as f:
        print(f)
        json.dump(notes, f)

    return redirect("/")



@app.route('/delete-data',methods=['POST'])
def deletedata():
    uuid = request.form["uuid"]
    with open('Data/notes.json', "r") as file:
        notes = json.load(file)
    
    notes = [x for x in notes if x.get("uuid") != uuid]

    with open('Data/notes.json', 'w') as f:
        print(f)
        json.dump(notes, f)

    return redirect("/")    
