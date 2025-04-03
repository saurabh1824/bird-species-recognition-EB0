# bird-species-recognition-EB0

# Bird Species Recognition using Deep Learning

## Project Overview
This project is a deep learning-based web application for bird species recognition. It utilizes a trained model to identify bird species from images uploaded by users. The application is built using Python and includes machine learning components, a web interface, and a database to store user information and detection history.

## Features
- Detect bird species from uploaded images using a deep learning model.
- Web-based interface for users to upload images and view results.
- Stores detection history in a MySQL database.

## Software Modules

### 1. **Model Training and Prediction**
- The deep learning model is trained using TensorFlow and Keras.
- The `predict.py` script loads the trained model and performs inference on uploaded bird images.
- The `detect_bird.py` script integrates the `ultralytics` module for additional image processing and detection.

### 2. **Web Application**
- Built using Flask, handling user requests and routing.
- `app.py` is the main entry point, managing API endpoints and database connections.
- Users can interact with the application through a web browser.

### 3. **Database Management**
- Uses MySQL to store user details and bird detection history.
- The `database` folder contains `db_script.sql`, which initializes required tables.
- The `get_db_connection()` function in `app.py` manages database connections.

### 4. **Frontend Interface**
- HTML, CSS, and JavaScript are used for the user interface.
- Users can register, log in, and upload bird images.
- Results are displayed in a user-friendly manner.

## Installation and Setup

### Running the Project for the First Time

#### Install Dependencies
- Install all required dependencies mentioned in `predict.py`, including TensorFlow.
- Install the `ultralytics` module, which is required in `detect_bird.py`.
- Run the following command to install all required dependencies:
  
  ```sh
  pip install -r requirements.txt
  ```
  *(requirements.txt includes all necessary dependencies.)*

#### Database Setup
- Run the SQL script (`db_script.sql`) provided in the `database` folder using MySQL Workbench to initialize the database and tables.
- Modify MySQL Connection Details:
  - Open `app.py` and navigate to the `get_db_connection()` function under the helper functions section.
  - Set your MySQL username and password accordingly.

#### Run the Application
- Navigate to the root directory of the project.
- Run the following command to start the application:
  
  ```sh
  python app.py
  ```

## Usage
- Open a web browser and go to `http://localhost:5000`.
- Register or log in to access the application.
- Upload an image of a bird to receive species detection results.
- View your detection history and related information under the profile tab.
