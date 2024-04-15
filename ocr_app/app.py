# # app.py

# from flask import Flask, render_template, request, redirect
# from werkzeug.utils import secure_filename
# import os
# import mysql.connector

# app = Flask(__name__)

# # Connect to MySQL database
# def connect_to_database():
#     try:
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             passwd="",
#             database="ocr_database"
#         )
#         print("Connected to MySQL database")
#         return connection
#     except mysql.connector.Error as err:
#         print(f"Error connecting to MySQL database: {err}")
#         exit(1)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':
#         f = request.files['file']
#         if f:
#             filename = secure_filename(f.filename)
#             file_path = os.path.join('uploads', filename)
#             f.save(file_path)

#             # Perform OCR
#             connection = connect_to_database()
#             cursor = connection.cursor()
#             try:
#                 ext = os.path.splitext(file_path)[-1].lower()
#                 if ext in ('.png', '.jpg', '.jpeg', '.pdf'):
#                     cursor.execute("INSERT INTO ocr_text (file_path) VALUES (%s)", (file_path,))
#                     connection.commit()
#                     cursor.close()
#                     connection.close()
#                     return redirect('/')
#                 else:
#                     return "Unsupported file format"
#             except Exception as e:
#                 print(f"Error processing {file_path}: {e}")
#                 return "Error processing file"
#         else:
#             return "No file uploaded"

# if __name__ == '__main__':
#     app.run(debug=True)



# app.py

from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
import mysql.connector
import pytesseract
from pdf2image import convert_from_path

app = Flask(__name__)

# Connect to MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ocr_database"
        )
        print("Connected to MySQL database")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database: {err}")
        exit(1)

# Perform OCR on a single file
def perform_ocr(file_path):
    try:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == ".pdf":
            pages = convert_from_path(file_path, 500)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page)
        elif ext in ('.png', '.jpg', '.jpeg'):
            text = pytesseract.image_to_string(file_path)
        else:
            print("Unsupported file format")
            return None
        
        return text.strip()
    except Exception as e:
        print(f"Error performing OCR for {file_path}: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f:
            filename = secure_filename(f.filename)
            file_path = os.path.join('uploads', filename)
            f.save(file_path)

            # Perform OCR
            extracted_text = perform_ocr(file_path)
            if extracted_text is not None:
                # Connect to MySQL database
                connection = connect_to_database()
                cursor = connection.cursor()
                try:
                    cursor.execute("INSERT INTO ocr_text (file_path, extracted_text) VALUES (%s, %s)", (file_path, extracted_text))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    return redirect('/')
                except mysql.connector.Error as err:
                    print(f"Error inserting into database: {err}")
                    return "Error inserting into database"
            else:
                return "Error processing file"
        else:
            return "No file uploaded"

if __name__ == '__main__':
    app.run(debug=True)
