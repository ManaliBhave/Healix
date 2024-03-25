from flask import Flask, render_template, request, redirect, session, url_for, abort, jsonify, flash
from flask_bcrypt import Bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app,storage
from flask_socketio import join_room, leave_room, send, SocketIO
import uuid
from models.pneumonia.model import predict
from twilio.rest import Client
import time
from datetime import datetime, timedelta
import threading
from models.ecg.heart_failure import ecg_predict
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
from test import getData

account_sid = 'ACf516a5416e5357679749dacd9c00a19c'
auth_token = '666d276add486cb54ca969d77477ddc7'
twilio_phone_number = '+16504614077'


app = Flask(__name__)
app.secret_key = "ucucgrcgcfucf"

socketio = SocketIO(app)

cred = credentials.Certificate("./configs.json")
firebase_admin.initialize_app(cred,{"storageBucket": "semicolons-a4c15.appspot.com"})

bcrypt = Bcrypt(app)
#uri = "mongodb+srv://shree:x184UxTadWLGPG5J@cluster0.szpxxnd.mongodb.net/?retryWrites=true&w=majority"
uri = "mongodb+srv://shree:x184UxTadWLGPG5J@cluster0.zmr8g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client.test
users = db.users
chatroom = db.messages

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'semicolons_email' not in session:
            # User is not logged in, redirect to login page
            return redirect(url_for('login_register'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/user/login')
def login_register():
    return render_template('login_register.html')

@app.route('/add_reminders',methods=["GET","POST"])
def add_reminder():
    if request.method=="POST":
            data = request.form
            reminder_data = users.update_one({"email":session["semicolons_email"]},{"$push":{"reminders":{'time' : data['time'], 'date' : data['date'],'msg' : data['msg'],'type':data["med-app"]}}})
            flash("reminder added successfully","success")
            return redirect(request.referrer)
    user = users.find_one({"email":session["semicolons_email"]})
    reminders = user["reminders"]
    return render_template('add_reminder.html',reminders=reminders)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login_user = users.find_one({'email' : data['email']})
    if login_user:
        password = bcrypt.check_password_hash(login_user['password'], data['password'])
        if password:
            session['semicolons_email'] = str(data['email'])
            return jsonify({'message' : 'success'})
        else:
            return jsonify({'message' : 'Invalid Password'})
    return jsonify({'message' : 'Invalid Email'})

@app.route('/symptoms',methods=["GET","POST"])
def symp_ques():
    search_options = [
        "Continuous sneezing",
        "Chills",
        "Stomach pain",
        "Vomiting",
        "Fatigue",
        "Cold hands and feets",
        "Weight loss",
        "Cough",
        "High fever",
        "Breathlessness",
        "Sweating",
        "Dehydration",
        "Nausea",
        "Diarrhoea",
        "Malaise",
        "Phlegm",
        "Chest pain",
        "Fast heart rate",
        "Dizziness",
        "Swollen legs",
        "Rusty sputum",
        "Swelling in belly area",
        "Reduced Concentration",
        "Confusion"
    ]

    if request.method == "POST":
        selected_options = request.form.getlist('selected_options[]')
        number_of_days = request.form.getlist('number_of_days[]')
        temperature = request.form.getlist('temperature[]')

        # Create a list to store all entries
        user = users.find_one({'email' : session['semicolons_email']})
        # print(user['symptoms'][0:])
        entries = []
        # entries=entries.append(user['symptoms'][0:])
        # entries=user['']
        # entries=entries.append

        # Iterate through selected options and create a dictionary for each entry
        for i in range(len(selected_options)):
            entry = {
                'selected_option': selected_options[i],
                'number_of_days': number_of_days[i],
                'temperature': temperature[i]
            }
            # Append the dictionary to the list of entries
            entries.append(entry)
        if 'symptoms' in user:
            for entry in user['symptoms']:
                entries.append(entry)
        print("All Entries:", entries)
        reminder_data = users.update_one({"email":session["semicolons_email"]},{"$set":{"symptoms":entries}})
        flash("Entries added successfully", "success")

    
        # Your code to process the list of entries

        return render_template('symptoms_ques.html')

    return render_template('symptoms_ques.html', search_options=search_options)


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed = bcrypt.generate_password_hash(data['password'])
    curr_user = users.find_one({'email' : data['email']})
    if curr_user:
        return jsonify({'message' : 'User already exists'})
    new_user = users.insert_one({'name' : data['name'], 'email' : data['email'], 'password' : hashed,'contact':data['contact'],'address':data["address"],'age':data["age"],'gender':data["gender"]})
    if(new_user):
        return jsonify({'message' : 'success'})
    else: 
        return jsonify({'message' : 'failure'})
    
    
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/doctors")
def doctors():
    return render_template("doctors.html")


    
    
    
@app.route("/profile")
@login_required
def profile():
    user = users.find_one({'email' : session['semicolons_email']})
    df = pd.read_excel('./static/assets/datasets/filtered_dataset.xlsx')
    
    date = pd.date_range('2024-01-01', periods=10, freq='W')
    hld = list(df['High Density Lipoprotein (HDL Cholesterol)'][:10].values)
    lld = list(df['Low Density Lipoprotein (LDL Cholesterol)'][:10].values)
    glucose = list(df['Glucose (fasting)'][:10].values)
    
    fig_glucose = px.line(x=date, y=glucose, title='Glucose (fasting)', labels={'x':'Date', 'y':'Glucose (fasting)'})
    
    fig_lld = px.line(x=date, y=lld, title='Low Density Cholesterol', labels={'x':'Date', 'y':'Low Density Cholesterol'})
    
    fig_hld = px.line(x=date, y=hld, title='High Density Cholesterol', labels={'x':'Date', 'y':'High Density Cholesterol'})
    
    html_file_path_glucose = "./static/graph/glucose.html"
    html_file_path_hld = "./static/graph/lld.html"
    html_file_path_lld = "./static/graph/hld.html"

    pyo.plot(fig_glucose, filename=html_file_path_glucose, auto_open=False)
    pyo.plot(fig_lld, filename=html_file_path_hld, auto_open=False)
    pyo.plot(fig_hld, filename=html_file_path_lld, auto_open=False)

    # Read the HTML content
    with open(html_file_path_glucose, 'r', encoding='utf-8') as file:
        plot_html_glucose = file.read()
    # Read the HTML content
    with open(html_file_path_hld, 'r', encoding='utf-8') as file:
        plot_html_hld = file.read()
    # Read the HTML content
    with open(html_file_path_lld, 'r', encoding='utf-8') as file:
        plot_html_lld = file.read()
    return render_template("profile.html", username = user["name"], useremail = user['email'], usercontact = user['contact'], 
                           plot_html_glucose = plot_html_glucose, plot_html_hld = plot_html_hld,
                           plot_html_lld = plot_html_lld, useraddress = user['address'])

    
    
@app.route('/upload/report',methods=['GET','POST'])
def upload_report():
    if request.method == "POST":
         data = request.form
         title = data["title"]
         pdf_file = request.files["pdf"]
         pdf_url = upload_pdf_to_storage(pdf_file)
         report = {
              "title": title,
              "file": pdf_url
         }
         user = getuserdetails(session["semicolons_email"])
         users.update_one({'email': session['semicolons_email']}, {'$push': {'reports': report}})
    return render_template("upload_report.html")

@app.route('/reports')
def showReport():
     user = users.find_one({"email": 'shree@gmail.com'})
     reports = user["reports"]
     return render_template('report.html',reports=reports)

@app.route('/events')
def events():
     return render_template('events.html')

@app.route('/medication/view/', methods=['GET', 'POST'])
def medication_view():    
     medications = users.find_one({'email' : session['semicolons_email']})['medications']
     return render_template("medication_view.html",medications=medications)

@app.route('/medication/alt/<string:name>', methods=['GET', 'POST'])
def medication_alt(name):
     data = getData(name)
     return render_template("medication_alt.html",alts=data)

@app.route('/medication/upload',methods=['GET','POST'])
def symp_medication():
    if request.method == "POST":
        data = request.form
        dosage = data['dosage']
        medication = data['medication']
        users.update_one({'email': session['semicolons_email']}, {'$push': {'medications': {'dosage': dosage, 'medication': medication}}})
    search_options = [
    "Continuous_sneezing",
    "Chills",
    "Stomach_pain",
    "Vomiting",
    "Fatigue",
    "Cold_hands_and_feets",
    "Weight_loss",
    "Cough",
    "High_fever",
    "Breathlessness",
    "Sweating",
    "Dehydration",
    "Nausea",
    "Diarrhoea",
    "Malaise",
    "Phlegm",
    "Chest_pain",
    "Fast_heart_rate",
    "Dizziness",
    "Swollen_legs",
    "Rusty_sputum",
    "Swelling_in_belly_area",
    "Reduced Concentration",
    "Confusion"
    ]
    return render_template('medication_upload.html', search_options=search_options)

@app.route('/doctor/home', methods=['GET', 'POST'])
def doc_home():
    return render_template("doctor_home.html")

@app.route('/doctor/profile', methods=['GET', 'POST'])
def doc_profile():
    user = users.find_one({"email":session["semicolons_email"]})
    patients=user['patients']
    print(patients)
    return render_template("doctor_profile.html",patients=patients)

@app.route('/doctor/report/view', methods=['GET', 'POST'])
def doc_report():
    df = pd.read_excel('./static/assets/datasets/filtered_dataset.xlsx')
    
    date = pd.date_range('2024-01-01', periods=10, freq='W')
    hld = list(df['High Density Lipoprotein (HDL Cholesterol)'][:10].values)
    lld = list(df['Low Density Lipoprotein (LDL Cholesterol)'][:10].values)
    glucose = list(df['Glucose (fasting)'][:10].values)
    
    fig_glucose = px.line(x=date, y=glucose, title='Glucose (fasting)', labels={'x':'Date', 'y':'Glucose (fasting)'})
    
    fig_lld = px.line(x=date, y=lld, title='Low Density Cholesterol', labels={'x':'Date', 'y':'Low Density Cholesterol'})
    
    fig_hld = px.line(x=date, y=hld, title='High Density Cholesterol', labels={'x':'Date', 'y':'High Density Cholesterol'})
    
    html_file_path_glucose = "./static/graph/glucose.html"
    html_file_path_hld = "./static/graph/lld.html"
    html_file_path_lld = "./static/graph/hld.html"

    pyo.plot(fig_glucose, filename=html_file_path_glucose, auto_open=False)
    pyo.plot(fig_lld, filename=html_file_path_hld, auto_open=False)
    pyo.plot(fig_hld, filename=html_file_path_lld, auto_open=False)

    # Read the HTML content
    with open(html_file_path_glucose, 'r', encoding='utf-8') as file:
        plot_html_glucose = file.read()
    # Read the HTML content
    with open(html_file_path_hld, 'r', encoding='utf-8') as file:
        plot_html_hld = file.read()
    # Read the HTML content
    with open(html_file_path_lld, 'r', encoding='utf-8') as file:
        plot_html_lld = file.read()
    return render_template("doctor_patient_report.html", plot_html_glucose = plot_html_glucose, plot_html_hld = plot_html_hld,
                           plot_html_lld = plot_html_lld)

def getuserdetails(email):
    user = users.find_one({'email' : email})
    return user 
# Functions
def upload_image_to_storage(image):
    if image:
        # Get the image filename
        filename = f"{uuid.uuid4()}.jpg"
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Create a blob object in the storage bucket
        blob = bucket.blob(f'Images/{filename}')
        # Upload the image file to Firebase Storage
        blob.upload_from_file(image)
        # Get the URL for the uploaded image
        blob.make_public()
        image_url = blob.public_url
        return image_url

rooms = {"AAAA": {"members": 0, "messages": []}}
@socketio.on("message")
def message(data):
    room = session["code"]
    if room not in rooms:
        return 
    user = getuserdetails(session['semicolons_email'])
    content = {
        "name": session["name"],
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    chatroom.update_one({'code' : room}, {'$set' : {'members' : rooms[room]["members"], 'messages' : rooms[room]["messages"]}})

@socketio.on("connect")
def connect(auth):
    room = session["code"]
    name = session["name"]
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "is online now"}, to=room)
    rooms[room]["members"] += 1

@socketio.on("disconnect")
def disconnect():
    room = session["room"]
    name = session["name"]
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


@app.route("/meeting")
def meeting():
    default_room_id = "1111"
    room_id = request.args.get("roomID", default_room_id)
    return render_template("meeting.html", username=session["name"], room_id=room_id)


@app.route("/chat/room/<string:code>")
@login_required
def room(code):
    if code not in rooms:
        rooms[code] = {"members": 0, "messages": []}
    else:
        curr_room = chatroom.find_one({'code' : code})
        if curr_room is None:
            chatroom.insert_one({'code' : code, 'members' : 0, 'messages' : []})
            curr_room = chatroom.find_one({'code' : code})
        rooms[code]["members"] = curr_room['members']
        rooms[code]["messages"] = curr_room['messages']
    groupcode = code
    session["code"] = code
    user = getuserdetails(session['semicolons_email'])
    session["name"] = user["name"]
    if room is None or session["name"] is None or groupcode not in rooms:
        return redirect("/user/login")

    return render_template("chatroom.html", code=groupcode, messages=rooms[groupcode]["messages"])
    



 
def upload_pdf_to_storage(pdf_file):
    if pdf_file:
        # Get the PDF filename
        filename = f"{uuid.uuid4()}.pdf"
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Create a blob object in the storage bucket
        blob = bucket.blob(f'Pdfs/{filename}')
        # Set content type for PDF
        blob.content_type = 'application/pdf'
        # Upload the PDF file to Firebase Storage
        blob.upload_from_file(pdf_file, content_type='application/pdf')
        # Get the URL for the uploaded PDF
        blob.make_public()
        pdf_url = blob.public_url
        return pdf_url
    
def delete_image_from_storage(image_url):
    if image_url:
        # Extract the path from the URL
        path = image_url.split('.com/')[-1]
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Get the blob reference
        blob = bucket.blob(path)
        # Delete the blob
        blob.delete()
    
def delete_pdf_from_storage(pdf_url):
    if pdf_url:
        # Extract the path from the URL
        path = pdf_url.split('.com/')[-1]
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Get the blob reference
        blob = bucket.blob(path)
        # Delete the blob
        blob.delete()

def send_sms(to, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=to
    )
    print("Message sent successfully to", to)

# Function to remind the user
def medication_reminder():
    
    while True:
        print("loop")
        user_list = users.find()
        current_time = datetime.now().strftime("%H:%M")

        for user in user_list:
            reminders = user.get('reminders', []) 
            for reminder in reminders:
                reminder_time = reminder.get('time')  
                if reminder_time ==  current_time :
                    send_sms("+91"+user['contact'], reminder.get('msg'))
        time.sleep(60)

@app.route('/pneumonia',methods = ['POST','GET'])
def pneumonia():
    if request.method == "POST":
        image = request.files['image']
        response = predict(image)
        return jsonify({'result':response})
    return render_template('pneumonia.html')


@app.route('/logout')
def logout():
    session.pop('semicolons_email', None)
    session.pop('name', None)
    session.pop('contact', None)
    return redirect('/user/login')

@app.route('/ecg',methods = ['POST','GET'])
def ecg():
    if request.method == "POST":
        image = request.files['image']
        response = ecg_predict(image)
        return jsonify({'result':response})
    return render_template('ecg.html')

@app.route('/contact',methods = ['POST','GET'])
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    # reminder_thread = threading.Thread(target=medication_reminder)
    # reminder_thread.start()
    app.run(debug=True)
   

