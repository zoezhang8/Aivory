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
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # This gathers all image paths to compare to
            all_paths = [os.path.join(app.config['UPLOAD_FOLDER'], f) for f in os.listdir(app.config['UPLOAD_FOLDER'])]
            item_vector = recognize_image(filepath, all_paths)

            matches = search_inventory(item_vector)
            if not matches or matches[0][1] < 0.5:  # You can adjust the threshold
                return redirect(f"/add-item?image={file.filename}")

            return render_template('results.html', matches=matches)

    return render_template('index.html')


#SHOW FORM AND SAVE NEW PRODUCT INFO
@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        tags = request.form.get('tags')
        image_filename = request.form.get('image')

        # Save to JSON file
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



#run the app with debugging
if __name__ == '__main__':
    app.run(debug=True)
