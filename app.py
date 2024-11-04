
from flask import Flask,render_template,request,redirect,session,flash,url_for,jsonify,send_file
import os
import pymysql
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'healthcare',
}

def connect():
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # connect to the PostgreSQL server
            #self.log.info('Connecting to the PostgreSQL database...')
            conn = pymysql.connect(**db_config)
        except (Exception) as error:
            #self.log.error(error)
            raise error
        return conn



def single_insert(insert_req):
        """ Execute a single INSERT request """
        conn = None
        cursor = None
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(insert_req)
            conn.commit()
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def execute(req_query):
        """ Execute a single request """
        """ for Update/Delete request """
        conn = None
        cursor = None
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(req_query)
            conn.commit()
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def executeAndReturnId( req_query):
        """ Execute a single request and return id"""
        """ for insert request """
        conn = None
        cursor = None
        try:
            conn =connect()
            cursor = conn.cursor()
            cursor.execute(req_query)
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            last_inserted_id = cursor.fetchone()[0]
            return last_inserted_id
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def fetchone( get_req):
        conn=None
        cur=None
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute(get_req)
            data = cur.fetchone()
            return data
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            raise error
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
def fetchall(get_req):
        conn = None
        cur = None
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute(get_req)
            data = cur.fetchall()
            return data
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            raise error
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()



@app.route("/")
def index():
    return render_template("index.html")

def authenticate(username, password):
    """ Authenticate user """
    print(username)
    print(username)
    query="SELECT * FROM `login` WHERE `email`='{}' AND `password`='{}'"
    
    user = fetchone(query.format(username, password))
    
    print(user)
    return user



@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    print(password)
    user = authenticate(username, password)
    print("user",user)
    if user:
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        if user[3] == 'admin':
            return redirect(url_for('admin_home'))
        elif user[3] == 'user':
            return redirect(url_for('user_home'))
        elif user[3] == 'staff':
            return redirect(url_for('staff_home'))
        elif user[3] == 'Dietician':
            return redirect(url_for('dietician_home'))
    else:
        flash('Invalid Username or Password')
        error="Invalid Username or Password"
        return render_template('index.html',error=error)
    

@app.route('/register', methods=['POST'])
def register():
    name = request.form['username']
    email = request.form['email']
    password = request.form['password']
    category = 'user'

    try:
        # Attempt to insert the new user into the database
        insert_query = "INSERT INTO login (email, password, category, name) VALUES ('{}', '{}', '{}', '{}')".format(email, password, category, name)
        datain = single_insert(insert_query)
        return redirect(url_for('index'))
    except pymysql.err.IntegrityError as e:
        # If there's an IntegrityError (e.g., duplicate entry error), display it as an alert
        error_message = "Duplicate Password"
        return render_template('index.html', error=error_message)

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect to the index page
    return redirect(url_for('index'))

@app.route("/admin")
def admin_home():
    # Add admin home logic here
    return render_template("Admin/add-caretaker.html")

@app.route("/user")
def user_home():
    # Add user home logic here
    print("JIIi")
    return render_template("User/index.html")

@app.route("/staff")
def staff_home():
    # login_id = session.get('user_id')
    # print("login_id",login_id) 
    # query="SELECT * FROM `medicine` WHERE `staff_id`='{}'"
    # medicine_data = fetchall(query.format(login_id))
    # Add staff home logic here
    return render_template("Staff/index.html")

@app.route("/dietician")
def dietician_home():
    Uid_dietician = session.get('user_id')  # Assuming you have a session object
    print(Uid_dietician)
    # Query to fetch place data
    place_query = "SELECT login.name FROM medical_report INNER JOIN login ON medical_report.user_id = login.id AND medical_report.dietician_id = '{}'"
    place_results = fetchall(place_query.format(Uid_dietician))
    print("place_result", place_results)
    # Extracting the first element of each tuple
    place_data = [row[0] for row in place_results]

    # Query to fetch message data
    message_query = "SELECT * FROM `diet` WHERE `dietician_id` = '{}' AND `type` = 'user_to_dietician'"
    message_results = fetchall(message_query.format(Uid_dietician))
    # Extracting the 'message' column from each tuple
    message_data = [row[2] for row in message_results]
    print("message_data", message_data)
    
    return render_template("Dietician/index.html", place_data=place_data, message_data=message_data)



        
        
        
        
@app.route('/add-caretaker', methods=['GET', 'POST'])
def add_caretaker():
    if request.method == 'POST':
        # Handle form submission
        name = request.form['username']
        email = request.form['email']
        address = request.form['address']
        qualification = request.form['qualification']
        caretaker_type = request.form['type']
        zip_code = request.form['zip']

        if request.form.get('hid')!= 'None':
            # If hid is present, it means it's an update operation
            hid = request.form['hid']
            print("ffff")
            print("hid",hid)
            query = "UPDATE caretaker SET name='{}', email='{}', address='{}', qualification='{}', type='{}', zip='{}' WHERE id='{}'"
            execute(query.format(name, email, address, qualification, caretaker_type, zip_code, hid))
            
           
            return redirect(url_for('caretaker_data'))
        else:
            print("hhh")
            query = "INSERT INTO caretaker (name, email, address, qualification, type, zip) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')"
            datain=single_insert(query.format(name, email, address, qualification, caretaker_type, zip_code))
            #execute(sql, (name, email, address, qualification, type, zip))


            return redirect(url_for('caretaker_data'))
    else:
      
       if request.method == 'GET':
            up_id = request.args.get('up_id')
            row = None
            #u_name = u_email = u_address = u_qualification = u_type = u_zip = ''

            if up_id:
                query = "SELECT * FROM caretaker WHERE id='{}'"
           
           
                row=fetchone( query.format (up_id))
                print("row",row)
                #if row:
                    #u_name, u_email, u_address, u_qualification, u_type, u_zip = row

            return render_template('Admin/add-caretaker.html', caretaker=row)
    return render_template('Admin/add-caretaker.html', caretaker=row)
        
        
        



@app.route('/caretaker-data')
def caretaker_data():
    
   
    query = "SELECT * FROM caretaker"
    caretakers =fetchall(query.format())
    print("caretakers",caretakers)
    return render_template('Admin/caretaker-data.html', caretakers=caretakers)



@app.route('/delete-caretaker/<int:id>')
def delete_caretaker(id):
    print("id",id)
    query="DELETE FROM caretaker WHERE id = '{}'"
    data=execute(query.format(id))
    print("deletedata",data)
    return redirect(url_for('caretaker_data'))


@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        
        print("post insert")
        name = request.form['username']
        email = request.form['email']
        address = request.form['address']
        qualification = request.form['qualification']
        password=request.form['password']
        zip_code = request.form['zip']
        category='staff'
       

        # Check if it's an update operation
        if request.form.get('hid') != 'None':
            print("post update ")
            print("post update ",type(request.form.get('hid')))
            hid = request.form['hid']
            # Perform update operation
            query = "UPDATE staff SET name='{}', email='{}',address='{}',qualification='{}',password='{}',zip='{}' WHERE id='{}'"
            execute(query.format(name, email,address,qualification,password,zip_code, hid))
            return redirect(url_for('staff_data'))
        else:
            # Perform insert operation
            print("post insert second")
            
            query = "INSERT INTO staff (name, email,address,qualification,password,zip) VALUES ('{}','{}','{}', '{}', '{}', '{}')"
            datain=single_insert(query.format(name, email,address,qualification,password,zip_code))

            print("datain",datain)
            query2 = "INSERT INTO login (name, email, password, category) VALUES ('{}', '{}', '{}','{}' )"
            single_insert(query2.format(name, email, password,category))
            return redirect(url_for('staff_data'))
    else:
        # Handle GET request
        up_id = request.args.get('up_id')
        row = None
        if up_id:
            query = "SELECT * FROM staff WHERE id='{}'"
            row = fetchone(query.format(up_id))
        return render_template('Admin/add_staff.html', staff=row)
    


@app.route('/staff_data')
def staff_data():
    # Retrieve staff data from database
    query = "SELECT * FROM staff"
    staff_data = fetchall(query)
    return render_template('Admin/staff_data.html', staff_data=staff_data)


@app.route('/delete_staff/<int:id>')
def delete_staff(id):
    query = "DELETE FROM staff WHERE id = '{}'"
    execute(query.format(id))
    return redirect(url_for('staff_data'))


# @app.route('/add_Staff', methods=['GET', 'POST'])
# def add_Staff():
#     if request.method == 'POST':
#         name = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         address = request.form['address']
#         qualification = request.form['qualification']
#         zip_code = request.form['zip']

#         if request.form.get('hid') != 'None':
#             hid = request.form['hid']
#             query = "UPDATE staff SET name='{}', email='{}', password='{}', address='{}', qualification='{}', zip='{}' WHERE id='{}'"
#             execute(query.format(name, email, password, address, qualification, zip_code, hid))
#             return redirect(url_for('staff_data'))
#         else:
#             login_id = session.get('user_id') 
#             print("login_id",login_id)
#             query = "INSERT INTO staff (login_id,name, email, password, address, qualification, zip) VALUES ('{}','{}', '{}', '{}', '{}', '{}', '{}')"
#             execute(query.format(login_id,name, email, password, address, qualification, zip_code))
#             return redirect(url_for('staff_data'))

@app.route('/add_dietician', methods=['GET', 'POST'])
def add_dietician():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        qualification = request.form['qualification']
        zip_code = request.form['zip']
        category='Dietician'

        if request.form.get('hid') != 'None':
            hid = request.form['hid']
            query = "UPDATE dietician SET name='{}', email='{}', password='{}', address='{}', qualification='{}', zip='{}' WHERE id='{}'"
            execute(query.format(name, email, password, address, qualification, zip_code, hid))
            return redirect(url_for('dietician_data'))
        else:
            
            query = "INSERT INTO dietician (name, email, password, address, qualification, zip) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')"
            execute(query.format(name, email, password, address, qualification, zip_code))

            query2 = "INSERT INTO login (name, email, password, category) VALUES ('{}', '{}', '{}','{}' )"
            execute(query2.format(name, email, password,category))

            return redirect(url_for('dietician_data'))
    else:
        up_id = request.args.get('up_id')
        row = None

        if up_id:
            query = "SELECT * FROM dietician WHERE id='{}'"
            row = fetchone(query.format(up_id))

        return render_template('Admin/add-dietician.html', dietician=row)

@app.route('/dietician_data')
def dietician_data():
    query = "SELECT * FROM dietician"
    dieticians = fetchall(query.format())
    return render_template('Admin/dietician-data.html', dieticians=dieticians)


@app.route('/delete_dietician/<int:id>')
def delete_dietician(id):
    print("id",id)
    query="DELETE FROM dietician WHERE id = '{}'"
    data=execute(query.format(id))
    print("deletedata",data)
    return redirect(url_for('dietician_data'))



@app.route('/add_hospital', methods=['GET', 'POST'])
def add_hospital():
    if request.method == 'POST':
        name = request.form['hospitalname']
        place = request.form['place']
        location = request.form['location']
        contact=request.form['Contact']
        

        if request.form.get('hid') != 'None':
            hid = request.form['hid']
            query = "UPDATE hospital SET name='{}', place='{}', Location='{}' , contact='{}' WHERE id='{}'"
            execute(query.format(name, place, location,contact,hid))
            return redirect(url_for('hospital_data'))
        else:
            #login_id = session.get('user_id') 
            #print("login_id",login_id)
            query = "INSERT INTO hospital (name,place, Location,contact) VALUES ('{}', '{}', '{}','{}')"
            execute(query.format(name, place, location,contact))
            return redirect(url_for('hospital_data'))
    else:
        up_id = request.args.get('up_id')
        row = None

        if up_id:
            query = "SELECT * FROM hospital WHERE id='{}'"
            row = fetchone(query.format(up_id))

        return render_template('Admin/add-hospital.html', hospital=row)

@app.route('/hospital_data')
def hospital_data():
    query = "SELECT * FROM hospital"
    hospitals = fetchall(query.format())
    return render_template('Admin/hospital-data.html', hospitals=hospitals)


@app.route('/delete_hospital/<int:id>')
def delete_hospital(id):
    print("id",id)
    query="DELETE FROM hospital WHERE id = '{}'"
    data=execute(query.format(id))
    print("deletedata",data)
    return redirect(url_for('hospital_data'))

@app.route("/medicalreport_data")
def medical_report_data():
    query = """
    SELECT medical_report.id, medical_report.report, login.name
    , login.id FROM medical_report
    INNER JOIN login ON medical_report.user_id = login.id
    """
    medical_reports = fetchall(query)
    print("medical report",medical_reports)
    query = "SELECT * FROM `login` WHERE `category`='Dietician'"
    dieticians = fetchall(query.format())
    print("dieticians",dieticians)
    return render_template("Admin/medicalreport-data.html", medical_reports=medical_reports, dieticians=dieticians)

@app.route("/user_data")
def user_data():
    query = "SELECT * FROM `login` WHERE `category`='user'"
    users = fetchall(query.format())
    return render_template("Admin/user-data.html", users=users)



# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if request.method == 'GET':
#         up_id = request.args.get('up_id')
#         #u_name = u_email = u_password = ''

#         if up_id:
            
#             query = "SELECT * FROM `login` WHERE `id`='{}'"
            
#             user =fetchone(query.format(up_id))
#             print("userdaa",user)
#             # if user:
                
#             #     u_name = user[1]
#             #     u_email = user[2]
#             #     u_password = user[3]
            

#         return render_template('Admin/profile.html', users=user)
#     elif request.method == 'POST':
#         # Handle form submission for updating profile
        
#         #up_id = request.form.get('hid')
#         u_name = request.form.get('fullName')
#         u_email = request.form.get('email')
#         u_password = request.form.get('password')
#         if request.form.get('hid') != 'None':
#             hid = request.form['hid']
#             query = "UPDATE login SET name='{}', email='{}', password='{}' WHERE id='{}'"
#             execute(query.format(u_name, u_email, u_password,hid))
#             return redirect(url_for('profile'))




@app.route('/submit_diet', methods=['POST'])
def submit_diet():
    if request.method == 'POST' :
        message = request.form['message']
        type = 'dietician_to_user'
        dietician_id = session.get('user_id')

        query = "SELECT * FROM `medical_report` WHERE `dietician_id` = '{}'"
        row = fetchone(query.format(dietician_id))
        print(row,"row")
        
        if row:
            user_id = row[1]
            print("user_id",user_id)
            query = "INSERT INTO `diet`(`user_id`, `message`, `dietician_id`, `type`) VALUES ('{}', '{}', '{}', '{}')"
            datain=single_insert(query.format(user_id, message, dietician_id, type))
           
            return redirect(url_for('dietician_home'))
        else:
            return "Error: No medical report found for this dietician"

@app.route('/patient_data')
def patient_data():
    
    user_id=session.get('user_id')
    query = "SELECT medical_report.report, login.name FROM medical_report INNER JOIN login ON medical_report.user_id = login.id WHERE medical_report.dietician_id = '{}'"
    
    place_data =fetchall(query.format (user_id))
    print("place_data",place_data)

    if place_data:
        return render_template('Dietician/patient-data.html', place_data=place_data)
    else:
        return render_template('Dietician/patient-data.html', place_data=None)


UPLOAD_FOLDER = 'templates/User/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/medicine_action',  methods=['GET', 'POST'])
def medicine_action():
    if request.method == 'POST':
        medicinename = request.form['medicinename']
        rate = request.form['rate']
        stock = request.form['stock']
        brand = request.form['brand']
        # staff_id = session['uid']  # Assuming you store user id in session
        staff_id = session.get('user_id')
        print("medicinename")

        if request.form.get('hid'):
            hid = request.form['hid']
            print("HID",hid)
            query = "UPDATE medicine SET name='{}', rate='{}', stock='{}', brand='{}' WHERE id='{}'"
            execute(query.format(medicinename, rate, stock, brand, hid))

            flash('Medicine updated successfully')
            return redirect(url_for('medicine_data'))

        else:
            query = "INSERT INTO medicine (name, rate, stock, brand, staff_id) VALUES ('{}', '{}', '{}', '{}', '{}')"
            datain = single_insert(query.format(medicinename, rate, stock, brand, staff_id))

            flash('Medicine added successfully')
            return redirect(url_for('medicine_data'))
    else:
      
       if request.method == 'GET':
            up_id = request.args.get('up_id')
            row = None
            print(up_id)
            

            if up_id:
                query = "SELECT * FROM medicine WHERE id='{}'"
                print(query)
                row=fetchone(query.format('10'))
                print("row",row[1])
                

            return render_template('Staff/index.html', medicine=row)
    return redirect(url_for('medicine_data'))


@app.route('/medicine_data')
def medicine_data():
    login_id = session.get('user_id')
    print(login_id)
    query = "SELECT * FROM `medicine` "
    medicine_data = fetchall(query.format(login_id))
    print("medicine_data", medicine_data)
    return render_template("Staff/medicine-data.html", medicine_data=medicine_data)


@app.route('/delete_medicine/<int:id>')
def delete_medicine(id):
    query="DELETE FROM `medicine` WHERE `id`='{}'"
    data=execute(query.format(id))
    return redirect(url_for('medicine_data'))

@app.route('/hospitals')
def hospital():
    query = "SELECT * FROM `hospital`"
    hospitals = fetchall(query.format())
    selected_location = request.form.get('location', '')  # Get the selected location from the URL query parameter
    return render_template('User/hospitals.html', hospitals=hospitals, selected_location=selected_location)


@app.route('/get_hospitals', methods=['POST'])
def get_hospitals():
    location = request.form.get('location')
    
    if location:
        query = "SELECT * FROM hospital WHERE Location = '{}'"
        hospitals = fetchall(query.format(location))
    else:
        query = "SELECT * FROM hospital"
        hospitals = fetchall(query)

    # Convert each tuple to a dictionary
    hospitals_dict = [{'id': hospital[0], 'name': hospital[1], 'address': hospital[2], 'location': hospital[3], 'other_info': hospital[4]} for hospital in hospitals]

    print(hospitals_dict)
    return jsonify(hospitals_dict)





@app.route('/medical_report')
def medical_report():
    
    
    user_id  = session.get('user_id')
    print("user_id",user_id)
    
    query="SELECT login.id AS dietician_id, login.name AS dietician_name FROM medical_report INNER JOIN login ON medical_report.dietician_id = login.id WHERE medical_report.user_id = '{}';"
   
    result = fetchone(query.format(user_id))
    if result:
        print(result,"result")
        dietician_name = result[1]
        dietician_id = result[0]
        return render_template('User/medical_report.html', dietician_name=dietician_name,dietician_id=dietician_id)
    return render_template('User/medical_report.html')



@app.route('/submit_medical_report', methods=['POST'])
def submit_medical_report():
   

    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['pdf_file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        user_id  = session.get('user_id')
        query = "INSERT INTO medical_report (user_id, report) VALUES ('{}', '{}')"
        execute(query.format(user_id, filename))
        

        return redirect(url_for('medical_report'))
    
## Chat with dietician
@app.route('/dietician_chat')
def dietician():
    return render_template("User/Chat.html")


@app.route('/store_message', methods=['POST'])
def store_message():
    try:
        # Get message and dietician_id from the request
        data = request.json
        message = data.get('message')
        dietician_id = data.get('dietician_id')
        user_id  = session.get('user_id')

        print(message,dietician_id,user_id)

        query = "INSERT INTO diet (user_id, message, dietician_id,type) VALUES ('{}', '{}', '{}','{}')"
        execute(query.format(user_id, message, dietician_id,'user_to_dietician'))
        

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Route to get messages
@app.route('/get_messages', methods=['GET'])
def get_messages():
    try:
        # Extract parameters from the request URL
        user_id = session.get('user_id')
        dietician_id = request.args.get('dietician_id')

        print("User ID:", user_id)
        print("Dietician ID:", dietician_id)

        # Query to select messages from the database
        sql = "SELECT * FROM diet WHERE (user_id = '{}' AND dietician_id ='{}') OR (user_id ='{}' AND dietician_id = '{}') ORDER BY date ASC"
        print("SQL Query:", sql)
    
        messages = fetchall(sql.format(user_id, dietician_id, dietician_id, user_id))
        print("Fetched Messages:", messages)

        messages_list = []
        for message in messages:
            message_dict = {
                'id': message[0],
                'user_id': message[1],
                'message': message[2],
                'dietician_id': message[3],
                'type': message[4],
                'date': message[5].strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
            }
            messages_list.append(message_dict)

        return jsonify(messages_list)
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500






@app.route('/caretaker')
def caretaker():
    # Get the user ID from the session
    user_id = session.get('user_id')
    
    
    if user_id is None:
        return "User ID not found in session."
    
    # Execute the SQL query to retrieve the caretaker information
    query = "SELECT caretaker.name, caretaker.type FROM caretaker INNER JOIN login ON login.caretaker_id = caretaker.id WHERE login.id = '{}'"
    result = fetchone(query.format(user_id))
   
   
    if result:
        caretaker_name, caretaker_type = result
        caretaker_info =  {"name": caretaker_name, "type": caretaker_type}
        print("caretaker_info",caretaker_info)
        
    else:
        caretaker_info = "No caretaker found"
    
    sql = "SELECT * FROM caretaker"
    caretaker_details = fetchall(sql.format())

    return render_template('User/caretaker.html', caretaker_info=caretaker_info,caretaker_details=caretaker_details)




# Medicine Routes

##showing Medicines

@app.route("/get_medicines", methods=["GET", "POST"])
def purchase_medicines():
    if request.method == "POST":
        # Handle form submission here
        address = request.form.get('address')
        items = request.form.getlist('items[]')
        quantities = request.form.getlist('quantity[]')

        print(quantities)

        # Process the form data (e.g., save to database)

        return "Form submitted successfully!"  # You can redirect or render a different template here after processing the form
    else:
        # Fetch medicine data from the database
        query = "SELECT * FROM medicine"  # Adjust SQL query as needed
        medicine_data = fetchall(query)
       
        print(medicine_data)

        # Render the template with medicine data
        return render_template("User/medicine_list.html", items=medicine_data)


@app.route("/get_unit_price", methods=["POST"])
def get_unit_price():
    if request.method == "POST":
        # Get the item ID from the request
        item_id = request.json.get('item_id')

        # Fetch the unit price and available stock quantity of the medicine from the database
        query = "SELECT rate, stock FROM medicine WHERE id = '{}'"  # Adjust SQL query as needed
        result = fetchone(query.format(item_id))

        # Return the unit price and stock quantity as a JSON response
        if result:
            unit_price, stock_quantity = result
            return jsonify({'unit_price': unit_price, 'stock_quantity': stock_quantity})
        else:
            return jsonify({'error': 'Medicine not found'}), 404




@app.route('/add_medpurchase', methods=['POST'])
def add_medpurchase():
    if request.method == 'POST':
        address = request.form['address']
        total_amount = float(request.form['total_amount'])
        purchased_medicines = request.form.getlist('med[]')
        quantities = request.form.getlist('qty[]')
        

        # Get user ID from session
        user_id = session.get('user_id')

        if user_id:
            try:
                # Insert data into medpurchase_head table
                query_head = "INSERT INTO medpurchase_head (user_id, address, total) VALUES ('{}','{}','{}')"
                execute(query_head.format(user_id, address, total_amount))

                # Update stock quantity of purchased medicines
                for med_id, quantity in zip(purchased_medicines, quantities):
                    query_update_stock = "UPDATE medicine SET stock = stock - '{}' WHERE id = '{}'"
                    execute(query_update_stock.format(quantity, med_id))

                # Store purchase details in session variables
                session['purchased_medicines'] = purchased_medicines
                session['quantities'] = quantities
                session['total_amount'] = total_amount
                return redirect(url_for('purchase_success'))
            except Exception as e:
                print(f"Error occurred while adding purchase details: {str(e)}")
                return "Failed to add purchase details. Please try again later."
        else:
            return "User session not found. Please login and try again."

@app.route('/purchase_success')
def purchase_success():
    # Retrieve purchase details from session variables
    purchased_medicine_ids = session.get('purchased_medicines')
    total_amount = session.get('total_amount')
    quantities = session.get('quantities')
    # Fetch medicine information from the database based on IDs
    quantities = [int(quantity) for quantity in quantities]
    purchased_medicines = []
    for medicine_id, quantity in zip(purchased_medicine_ids, quantities):
        # Fetch medicine information from the database based on medicine_id
        query = "SELECT `name`, `rate`, `stock` FROM `medicine` WHERE `id` = '{}'"
        execute(query.format(medicine_id))
        medicine_info = fetchone(query.format(medicine_id))
        purchased_medicines.append({
            'id': medicine_id,
            'name': medicine_info[0],
            'rate': medicine_info[1],
            'quantity': quantity
            
        })

    # Render the template with the purchase details
    return render_template('User/purchase_success.html', purchased_medicines=purchased_medicines, total_amount=total_amount,quantities=quantities)

@app.route('/download_bill')
def download_bill():
    # Retrieve purchase details from session variables
    purchased_medicines = session.get('purchased_medicines')
    quantities = session.get('quantities')
    total_amount = session.get('total_amount')
    quantities = [int(quantity) for quantity in quantities]

    # Generate and return the bill file
    # For demonstration, let's create a simple text file
    with open('bill.txt', 'w') as f:
        f.write('Bill Information:\n\n')
        f.write('Medicine Name\tQuantity\tUnit Price\n')
        for medicine, quantity in zip(purchased_medicines, quantities):
            f.write(f"{medicine}\t{quantity}\n")
        f.write(f"\nTotal Amount: {total_amount}")

    # Provide the bill file for download
    return send_file('bill.txt', as_attachment=True)


@app.route('/dietician-assign', methods=['POST'])
def assign_dietician():
    print("hii")
    # Extract data from the request
    selected_dietician_id = request.form['selectedValue']
    row_id = request.form['rowId']
    
    print(row_id)

    try:
        # Update medical_report table with the dietician ID
        query = "UPDATE medical_report SET dietician_id = '{}' WHERE id = '{}'"
        execute(query.format(selected_dietician_id, row_id))


        
        return jsonify({'success': True, 'message': 'Dietician assigned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})




@app.route('/caretaker-selection', methods=['POST'])
def caretaker_selection():
    print("hii")
    # Extract data from the request

    id = request.form['rowId']
    user_id = session.get('user_id')
    

    try:
        # Update medical_report table with the dietician ID
        query = "UPDATE login SET caretaker_id = '{}' WHERE id = '{}'"
        execute(query.format(id,user_id))


        
        return jsonify({'success': True, 'message': 'Dietician assigned successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)