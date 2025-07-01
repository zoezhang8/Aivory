from flask import Flask, request, render_template, redirect, url_for
import os
import json

from vision import recognize_image  
from db import search_inventory    

app = Flask(__name__)
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Gather all image paths including the uploaded one
        all_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) 
                     for f in os.listdir(app.config['UPLOAD_FOLDER'])]

        # Run recognition and get similarity scores
        matches = search_inventory(recognize_image(filepath, all_paths))

        # Check if any OTHER image is similar enough (exclude uploaded file)
        other_matches = [
            (path, score) for path, score in matches
            if os.path.basename(path) != filename and score >= 0.9
        ]

        if other_matches:
            # Show matches including uploaded image
            return render_template('results.html', matches=matches, uploaded=filename)
        else:
            # Redirect to add item if no similar existing items
            return redirect(url_for('add_item', image=filename))

    return render_template('index.html')


@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        tags = request.form.get('tags')
        image_filename = request.form.get('image')

        inventory_path = 'inventory.json'
        if os.path.exists(inventory_path):
            with open(inventory_path, 'r') as f:
                inventory = json.load(f)
        else:
            inventory = []

        inventory.append({
            'name': name,
            'price': price,
            'tags': tags,
            'image': image_filename
        })

        with open(inventory_path, 'w') as f:
            json.dump(inventory, f, indent=4)

        return redirect(url_for('upload_image'))

    image_filename = request.args.get('image')
    return render_template('add_item.html', image=image_filename)


if __name__ == '__main__':
    app.run(debug=True)
