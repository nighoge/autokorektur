import os
from flask import Flask, request, send_from_directory, jsonify
from main import main

app = Flask(__name__)

UPLOAD_FOLDER = 'images/inputImages'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DOWNLOAD_FOLDER = 'images/outputImages'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No image part'

    image = request.files['image']

    if image.filename == '':
        return 'No selected file'

    if image:
        inputImage = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(inputImage)
        #os.system(f'python main.py {inputImage}')
        main(inputImage)
        return jsonify({"message": "Image uploaded successfully and main.py executed"}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

@app.route('/')
def index():
    # Load the HTML page
    with open('index.html', 'r') as f:
        html_content = f.read()
    return html_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
