from flask import Flask, request, render_template, redirect, url_for
import os
import json

from vision import recognize_image  
from db import search_inventory    

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
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

        return render_template('results.html', matches=matches, uploaded=filename)


    return render_template('index.html')


@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        sku = request.form.get('sku')  # NEW
        description = request.form.get('description')  # NEW
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
            'sku': sku,  # NEW
            'description': description,  # NEW
            'tags': tags,
            'image': image_filename
        })

        with open(inventory_path, 'w') as f:
            json.dump(inventory, f, indent=4)

        return redirect(url_for('upload_image'))


    image_filename = request.args.get('image')
    return render_template('add_item.html', image=image_filename)


@app.route('/item/<image>')
def view_item(image):
    inventory_path = 'inventory.json'
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r') as f:
            inventory = json.load(f)
            for item in inventory:
                if item['image'] == image:
                    return render_template('item_detail.html', item=item)
    return "Item not found", 404


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/results/<uploaded>')
def results(uploaded):
    uploaded_path = os.path.join('static', uploaded)
    
    # Compare uploaded image to all others in /static
    matches = []
    for filename in os.listdir('static'):
        if filename == uploaded:
            continue
        path = os.path.join('static', filename)
        score = compute_similarity(uploaded_path, path)
        matches.append((filename, score))
    
    # Sort and set a threshold
    matches.sort(key=lambda x: x[1], reverse=True)
    SIMILARITY_THRESHOLD = 0.75
    show_add_button = all(score < SIMILARITY_THRESHOLD for _, score in matches[:3])

    return render_template(
        'results.html',
        uploaded=uploaded,
        matches=matches,
        show_add_button=show_add_button
    )
