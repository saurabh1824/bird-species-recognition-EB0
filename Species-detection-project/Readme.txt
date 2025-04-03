
Installation and Setup

Running the Project for the First Time

Install Dependencies

    Install all required dependencies mentioned in predict.py, including TensorFlow.
    Install the ultralytics module, which is required in detect_bird.py.

    Run the following command to install all required dependencies:

        pip install -r requirements.txt

    (requirements.txt includes all necessary dependencies.)

Database Setup

    Run the SQL script (db_script.sql) provided in the database folder using MySQL Workbench to initialize the database and tables.

    Modify MySQL Connection Details :
        Open app.py and navigate to the get_db_connection() function under the helper functions section.
        Set your MySQL username and password accordingly.


Run the Application

    Navigate to the root directory of the project.
    Run the following command to start the application:

        python app.py

Usage

    Open a web browser and go to http://localhost:5000.

    Register or log in to access the application.
    Upload an image of a bird to receive species detection results.
    View your detection history and related information under profile tab.