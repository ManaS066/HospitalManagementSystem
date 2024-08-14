from flask import Flask, render_template, request, redirect
import os
from pymongo import MongoClient

app = Flask(__name__)

# Configure the MongoDB client
client = MongoClient(os.environ.get('mongodb+srv://manasranjanpradhan2004:root@hms.m7j9t.mongodb.net/?retryWrites=true&w=majority&appName=HMS'))
db = client['HMS']
patients_collection = db['patients']
doctors_collection = db['doctors']
users_collection = db['users']
admin_collection = db['admin']
appointment_collection = db['appointment']
contact_collection = db['contact']

@app.route('hmsproject.vercel.app/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        comment = request.form['comment']
        contact_data = {
            'name': name,
            'email': email,
            'number': number,
            'comment': comment
        }
        contact_collection.insert_one(contact_data)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_user = users_collection.find_one({'username': username})
        if login_user and login_user['password'] == password:
            return render_template('index.html')
        else:
            return 'Wrong username or password'
    return render_template('user_login.html')

@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = users_collection.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user:
            return 'Username or email already exists'
        
        # Insert user data into MongoDB
        user_data = {
            'username': username,
            'email': email,
            'password': password
        }
        users_collection.insert_one(user_data)
        return render_template('user_login.html')
    return render_template('registration.html')

@app.route('/user')
def user():
    return render_template('user_app.html')

@app.route('/doctor', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        doctor = doctors_collection.find_one({'username': username, 'password': password})
        if doctor:
            name = doctor['name']
            email = doctor['email']
            spec = doctor['specialization']
            phone = doctor['phone']
            data = (name, email, spec, phone)
            appointments_data = list(appointment_collection.find({'disease': spec}))
            return render_template('doctor_app.html', data=data, appointments_data=appointments_data)
        else:
            return 'Invalid credentials'
    return render_template('doctor_login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_admin = admin_collection.find_one({'username': username})
        if login_admin and login_admin['password'] == password:
            total_app = appointment_collection.count_documents({})
            total_doc = doctors_collection.count_documents({})
            total_patient = patients_collection.count_documents({})
            total_contact = contact_collection.count_documents({})
            return render_template('admin_dashboard.html', appointment=total_app, doc=total_doc, patient=total_patient, contact=total_contact)
        else:
            return 'Invalid credentials'
    return render_template('admin_pass.html')

@app.route('/admin/appointments')
def admin_appointments():
    appointments = list(appointment_collection.find())
    return render_template('admin_appointments.html', appointments=appointments)

@app.route('/admin/contact-us')
def admin_contact_us():
    contacts = list(contact_collection.find())
    return render_template('admin_contact_us.html', contacts=contacts)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['patient_name']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        phone = request.form['phone']
        patients_data = {
            'name': name,
            'gender': gender,
            'dob': dob,
            'address': address,
            'phone': phone
        }
        patients_collection.insert_one(patients_data)
    return render_template('add_patient.html')

@app.route('/add_doc', methods=['GET', 'POST'])
def add_doc():
    if request.method == 'POST':
        doc_name = request.form['doctor_name']
        specialization = request.form['specialization']
        qualification = request.form['qualification']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        doctor_data = {
            'name': doc_name,
            'specialization': specialization,
            'qualification': qualification,
            'email': email,
            'phone': phone,
            'username': username,
            'password': password
        }
        doctors_collection.insert_one(doctor_data)
    return render_template('add_doc.html')

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        name = request.form['name']
        number = request.form['number']
        email = request.form['email']
        address = request.form['Address']
        date = request.form['dat']
        disease = request.form['diseaseInput']
        description = request.form['diseaseDescription']
        data = {
            'name': name,
            'email': email,
            'number': number,
            'address': address,
            'date': date,
            'disease': disease,
            'description': description
        }
        appointment_collection.insert_one(data)
        return redirect('/')
    return render_template('appointment.html')

@app.post('/approve')
def approve():
    name = request.form['docName']
    patEmail = request.form['patEmail']
    appointment = appointment_collection.find_one({'email': patEmail})

    if appointment:
        appointment_collection.update_one({'email': patEmail}, {'$set': {'doc_appoint': name}})
        return redirect('/doctor')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run( port=port)
