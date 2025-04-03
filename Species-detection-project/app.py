import base64
import datetime
import io
import os
import random
from flask import Flask, request, jsonify, render_template,url_for, Request, redirect, session, flash
from flask_cors import CORS
import mysql.connector
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime

from detect_bird import detect_bird
from preprocessing import preprocess_image
from predict import predict_pipeline

import MySQLdb
from MySQLdb.cursors import DictCursor


app = Flask(__name__,template_folder='templates')
CORS(app)
app.secret_key = "c16"




#########################################################33333333333333333333333333#########################################################  App Configuration ##################



# Directory to save uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)




########################################################################################################################################################################################  Helper Functions

# fun to check allowed files 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# func to connect to database with database name
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",    # put your mysql user name
        password="root", # put your mysql user password
        database = "species_detection_db"
    )

# Query execution function
def query_db(query, values=None, fetchone=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, values)
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

# TO Fetch multiple data eg.History
def query_multiple_db(query, values=None, fetchone=False):
    conn = get_db_connection()
    cursor = conn.cursor(DictCursor)
    cursor.execute(query, values)
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

# To exectue delete query (here used to delete img data if no bird detected)
def query_delete_db(query, values=None):
    """Executes a DELETE query and commits the changes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()  # Ensure the deletion is applied
    cursor.close()
    conn.close()


# insertion query (used in User Registration )
def insert_db(query, values=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, values)

        # Check if the query is an INSERT
        if query.strip().lower().startswith("insert"):
            conn.commit()
            cursor.close()
            conn.close()
            return True  # Success

        cursor.close()
        conn.close()
        return False  # If not an INSERT, return False

    except Exception as e:
        print("Database Error:", e)  # Log the error for debugging
        return False  # Return False on failure


#img encoding
def encode_image(image_path):
    """Convert an image to Base64 encoding."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def read_blob(image_blob):
    pillow_img = Image.open(io.BytesIO(image_blob))
    img_io = io.BytesIO()
    pillow_img.save(img_io, format="JPEG")
    img_bytes = img_io.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


############################################################################################################
#######  Flask App Routing


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html',logged_in=session.get("logged_in", False))


@app.route('/about')
def about():
    return render_template('about.html',logged_in=session.get("logged_in", False))


@app.route('/404', methods=['GET','POST'])
def error():
    msg = request.args.get('msg', 'Unknown Error')
    return render_template('404.html',msg = msg, logged_in=session.get("logged_in", False))


@app.route('/feedback', methods=['POST'])
def feedback():
    return redirect(url_for('error'))


@app.route('/model')
def model():
    return render_template('model.html',logged_in=session.get("logged_in", False))


@app.route('/monitor')
def monitor():
    return render_template('monitor.html')






'''
request form index page form action as post method
Function Performs:
1 - Check file type if not (jpg,jpeg,png) redirect to error page
2 - Generates random numeric ID for image file within the int range
3 - get user details that whcich user is uploading img
4 - saves data to images table also saves the img as mediumblob(max size = 16Mb)
5 - After successfull saving redirect to uploaded_file with the img id
'''
@app.route('/upload', methods=['GET','POST'])
def upload():
    ''' Endpoint for uploading images '''
    if 'file' not in request.files:
        return redirect(url_for('error', msg="No File Selected"))

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('error',msg="File Type Not Allowed"))

    # ID = random.getrandbits(32)  # Unique ID for the image
    ID = random.randint(1, 2147483647) #unique id within int range
    filename = secure_filename(file.filename)
    blob = file.read()

    # get the user detaiils
    user_id = session.get('details', {}).get('user_id')
    try:
        query = "INSERT INTO images (image_id, user_id, name, image_blob) VALUES (%s, %s, %s, %s)"
        query_db(query, (ID, user_id, filename, blob))
    except Exception as err:
        return redirect(url_for('error',msg='Can Not Upload Image (Probably DB problem) p;ease try again'))
    
    # redirect to uploaded_file for prediction
    return redirect(url_for('uploaded_file', ID=ID))



'''
request form upload with img id as parameter
Function :
1 - Get img data from images table which is saved in upload function
2 - also retrive the image as blob data
3 - dave the img in upload folder
4 - first check if there is any bird in image or not. if bird not found then delete the data from database and upload folder and redirect to error page
5 - if bird detected then only predict the species using predict.py
6 - after prediction saves the data in predictions table
7 - redirect to result page with id
'''

@app.route('/uploads/<int:ID>')
def uploaded_file(ID):
    ''' Retrieve image, predict, and redirect to results page '''
    try:
        query = "SELECT name, image_blob FROM images WHERE image_id = %s"
        result = query_db(query, (ID,), fetchone=True)
    except Exception as err:
        return redirect(url_for('error', msg="Can Not Fetch Data from Database"))

    if not result:
        return redirect(url_for('error', msg="Data not Found in Database"))

    # Get file extension
    extension = result['name'].rsplit('.', 1)[1]

    # Save image in folder uploads
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{ID}.{extension}")
    with open(image_path, 'wb') as f:
        f.write(result['image_blob'])

    ''' first check whethere there is any bird in the image or not using yolo. 
    If bird detected then only predict the species else delete the image form upload folder and db''' 
    if detect_bird(image_path):
        # if want to prepeocess the img
        preprocess_image(image_path)
        try:
            with open(image_path, "rb") as img_file:
                processed_img = img_file.read()
            update_img = "UPDATE images SET image_blob = %s where image_id = %s"
            query_db(update_img, (processed_img, ID,))
        except Exception as e:
            return redirect(url_for('error',msg="can not store processed img in db"))
        # Process the image using `predict.py`
        prediction, accuracy = predict_pipeline(image_path)
    else:
        # delete img from upload folder
        os.remove(image_path)
        # delete from database
        try:
            del_query = "DELETE FROM images WHERE image_id = %s"
            query_delete_db(del_query, (ID,))
        except Exception as err:
            return redirect(url_for('error', msg="Can Not Delete form database"))
        # redirect to error
        return redirect(url_for('error',msg="Unable to Detect Bird"))
    

    try:
        pred_query = "INSERT INTO predictions (image_id, prediction, accuracy) VALUES (%s, %s, %s)"
        query_db(pred_query, (ID, prediction, accuracy))
    except Exception as err:
        return redirect(url_for('error', msg="Could Not Save Pediction"))

    return redirect(url_for('results', ID=ID))


'''
request from uploaded_file func
and also from profile page when clicked on history_entry
Function Performs:
1 - accepts image id in url
2 - Retrive the result data for that perticular ID from database
3 - Retrive bird details(scientific-name and description) for the predicted species
4 - render the result page with all metadata and img
'''
@app.route('/results')
def results():
    ID = request.args.get('ID')

    # get result details from database
    try:
        query = "SELECT images.name, predictions.prediction, predictions.accuracy FROM predictions JOIN images ON predictions.image_id=images.image_id WHERE predictions.image_id = %s"
        result = query_db(query, (ID,), fetchone=True)
    except Exception as err:
        return redirect(url_for('error', msg="Result Details Not Found"))

    # get extension
    extension = result['name'].rsplit('.', 1)[1]
    filename=f"{ID}.{extension}"
    prediction = result['prediction']
    accuray = result['accuracy']

    if not ID or not filename or not prediction:
        return redirect(url_for('error', msg="No filename in Result"))


    # get image path from upload folder
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # # retrive img from uploads folder
    # if not os.path.exists(file_path):
    #     return redirect(url_for('error', msg="Result image File Not Found"))
    # # Encode image as Base64
    # encoded_img = encode_image(file_path)


    # retrive img from db instead of upload folder
    try:
        img_query = "SELECT image_blob FROM images WHERE image_id = %s"
        img_query_result = query_db(img_query, (ID,), fetchone=True)
    except Exception as err:
        return redirect(url_for('error',msg="can not retrive result img from db"))
    
    if img_query_result :
        pillow_img = Image.open(io.BytesIO(img_query_result['image_blob']))
        img_io = io.BytesIO()
        pillow_img.save(img_io, format="JPEG")
        img_bytes = img_io.getvalue()
        encoded_db_img = base64.b64encode(img_bytes).decode('utf-8')
    else :
        encoded_db_img = ""

    #if image is retrived from db then remove it from upload folder if exist there
    if os.path.exists(file_path):
        os.remove(file_path)


    # get bird species details
    try:
        bird_detail_query = "SELECT scientific_name, description FROM birds where name = %s"
        bird_detail = query_db(bird_detail_query,(prediction,), fetchone=True)
    except Exception as err:
        return redirect(url_for('error',msg="Cant Fetch Bird Details"))
    if bird_detail:
        scientific_name = bird_detail['scientific_name']
        description = bird_detail['description']
    else :
        scientific_name = "Unknown"
        description = "Unknown"

    try:
        more_result_query = "SELECT e.image_blob, p.image_id ,p.prediction FROM predictions p join images e on p.image_id=e.image_id where p.prediction = %s limit 9"
        more_result = query_multiple_db(more_result_query,(prediction,))
    except Exception as err:
        return redirect(url_for('error',msg="Cant Fetch More Result Details"))
    if more_result and scientific_name!='Unknown':
        more_results = [
        {"image_blob": read_blob(row[0]), "image_id": row[1], "prediction": row[2]}
        for row in more_result]
    else:
        more_results =[]

    # Metadata for display
    meta_data = {
        "ID": ID,
        "img_name": filename,
        "class" : prediction,
        "score" : accuray,
        "scientific_name": scientific_name,
        "description": description,
        "objects": [{"class": {"name": prediction}, "score": accuray}]
    }


    return render_template(
        'results.html',
        original = encoded_db_img,  # encoded image
        inferenced = 'NA',  # If there's a processed version, update this
        meta_data = meta_data,
        more_result = more_results
    )











#############################################################################################################
######User Registration and Login and profile


# Temporary login
# @app.route('/login')
# def login():
#     # session['logged_in'] = True
#     # return redirect(url_for('index'))
#     return render_template('login.html')


'''
Functions
1 - Retrive user details and history for the current user using its user id
2 - saves user history in login session 
3 - if no history found then keep history blank and profile page will show no history found
2 - Renders profile page with all data
'''
@app.route('/profile')
def profile():
    # retrive the history for the user when the page reloads
    user_id = session.get('details', {}).get('user_id')
    try:
        history_query = "select name, image_id, uploaded_at from images where user_id = %s order by uploaded_at desc;"
        history = query_multiple_db(history_query,(user_id,), fetchone=False)
        if history:
            session['history'] = [{"name": row[0],"image_id" : row[1], "time": timedifference(row[2])} for row in history]
        else:
            session['history'] =[]

    except Exception as err:
        return redirect(url_for('error',msg="Unable to Load History"))
    
    # session['history'] = []
    return render_template('profile.html')

@app.route('/timedifference')
def timedifference(db_time):
    try:
        # Get current time
        current_time = datetime.now()
        # Calculate difference
        time_diff = current_time - db_time
        seconds = int(time_diff.total_seconds())

        # Convert to human-readable format
        if seconds < 60:
            return f"{seconds} seconds ago"
        elif seconds < 3600:
            return f"{seconds // 60} minutes ago"
        elif seconds < 86400:
            return f"{seconds // 3600} hours ago"
        else:
            return f"{seconds // 86400} days ago"

    except Exception as e:
        return "Invalid timestamp"


@app.route('/delete')
def delete():
    image_id = request.args.get('ID')
    del_query = "DELETE FROM images WHERE image_id = %s"
    query_delete_db(del_query, (image_id,))
    return redirect(url_for('profile'))


'''
Deletes all data saved in the session
Redirect to index page
'''
@app.route('/logout')
def logout():
    session.pop("logged_in",None)
    session.pop("details",None)
    session.pop("history",None)
    flash('Log Out Sucessfully !', 'success')
    return redirect(url_for('index'))


#############################################

'''
Request form index page as GET - render the login page
Request form login page as POST
Function
1 - Get email and password as form data from login page
2 - check if user exist or not
3 - if exist then check password
4 - if password is correct then login sucessfull 
5 - saves user data in session and set status to logged_in
5 - redirect to index page
'''

# main user login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            query = "SELECT password FROM users WHERE email=%s"
            result = query_db(query, (email,), fetchone=True)
        except Exception as err:
            return redirect(url_for('error', msg="Can Not Fetch User Data"))
        
        if not result:
            return redirect(url_for('error', msg="Invalid Credential 1"))


        # password stored in database
        stored_password = result.get('password')


        if password == stored_password:
            session['logged_in'] = True
            query = "SELECT id, username,name,email FROM users WHERE email=%s"
            users = query_db(query, (email,), fetchone=True)

            session['details'] = {
                'user_id' : users['id'],
                'username': users['username'],
                'name': users['name'],
                'email': users['email']
            }

            
            flash('LogIn Sucessfully !', 'success')
            return redirect(url_for('index'))
        
        else:
            return redirect(url_for('error', msg="Invalid Credential"))
        

        
    return render_template('login.html')



'''
Request form login page as POST
Function
1 - Get details from login page registration form
2 - check if user exist or not
3 - if not exist then saves details in users table
4 - if registered successfully then redirect to login page
'''
# main user Registration 
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        check_query = "SELECT email FROM users WHERE email= %s"
        check_result = query_db(check_query, (email,), fetchone=True)
        if check_result:
            return redirect(url_for('error', msg="User Already Exist"))

        try:
            query = "INSERT INTO users (name, email, username, password) VALUES (%s,%s,%s,%s)"
            result = insert_db(query, (name, email, username, password)) 
            if result:
                return redirect(url_for('login'))   
            else:       
                return redirect(url_for('error', msg="Invalid Credential"))
        
        except Exception as err:
            return redirect(url_for('error', msg="Database Error (Registration Failed)"))
        
    return redirect(url_for('login'))






'''This will run the app on port no mentioned'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)


