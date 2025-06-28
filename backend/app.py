from flask import Flask, request, render_template, redirect, url_for
import os
from vision import recognize_image  # You’ll write this
from db import search_inventory    # You’ll write this

app = Flask(__name__)
UPLOAD_FOLDER = 'test_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # This gathers all image paths to compare to
            all_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in os.listdir(app.config['UPLOAD_FOLDER']) if f != file.filename]
            item_vector = recognize_image(filepath, all_paths)

            result = search_inventory(item_vector)   # Compare to inventory

            return render_template('results.html', result=result)

    return render_template('index.html')
