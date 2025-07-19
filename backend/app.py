from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
import json

from vision import recognize_image  
from db import search_inventory    

app = Flask(__name__)

# Permanent folder for saved products
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Temporary folder for uploads before confirmation
TEMP_FOLDER = os.path.join(os.path.dirname(__file__), 'temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)
app.config['TEMP_FOLDER'] = TEMP_FOLDER

# Inventory file
INVENTORY_PATH = os.path.join(os.path.dirname(__file__), 'inventory.json')


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        filename = file.filename

        # Clear the temp folder before saving the new upload
        for temp_file in os.listdir(app.config['TEMP_FOLDER']):
            os.remove(os.path.join(app.config['TEMP_FOLDER'], temp_file))

        # Save uploaded file to temp/
        temp_path = os.path.join(app.config['TEMP_FOLDER'], filename)
        file.save(temp_path)

        # Gather only inventory images from static/
        all_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) 
                     for f in os.listdir(app.config['UPLOAD_FOLDER'])]

        # Run image recognition and similarity comparison
        matches = search_inventory(recognize_image(temp_path, all_paths))

        return render_template('results.html', matches=matches, uploaded=filename)

    return render_template('index.html')


@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        sku = request.form.get('sku')
        description = request.form.get('description')
        tags = request.form.get('tags')
        image_filename = request.form.get('image')

        if not all([name, price, sku, description, tags, image_filename]):
            return "Missing fields", 400

        # Load or initialize inventory
        if os.path.exists(INVENTORY_PATH):
            with open(INVENTORY_PATH, 'r') as f:
                inventory = json.load(f)
        else:
            inventory = []

        # Append new product
        inventory.append({
            'name': name,
            'price': price,
            'sku': sku,
            'description': description,
            'tags': tags,
            'image': image_filename
        })

        # Move image from temp → static
        src_path = os.path.join(app.config['TEMP_FOLDER'], image_filename)
        dst_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        if os.path.exists(src_path):
            os.rename(src_path, dst_path)

        # Save inventory to disk
        with open(INVENTORY_PATH, 'w') as f:
            json.dump(inventory, f, indent=4)

        print(f"[INFO] Added item to inventory: {image_filename}")
        return redirect(url_for('upload_image'))

    # GET: Show form with uploaded image
    image_filename = request.args.get('image')
    return render_template('add_item.html', image=image_filename)


@app.route('/item/<image>')
def view_item(image):
    if os.path.exists(INVENTORY_PATH):
        with open(INVENTORY_PATH, 'r') as f:
            inventory = json.load(f)
            for item in inventory:
                if item['image'] == image:
                    return render_template('item_detail.html', item=item)
    return "Item not found", 404


@app.route('/temp/<filename>')
def temp_file(filename):
    return send_from_directory(app.config['TEMP_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
