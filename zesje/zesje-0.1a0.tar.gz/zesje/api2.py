from flask import Blueprint, jsonify, request, redirect

from . import db

app = Blueprint(__name__, __name__)

@app.route('/students', methods=['GET'])
@db.session
def get_students():
    return jsonify([
        dict(id=s.id, first_name=s.first_name,
             last_name=s.last_name, email=s.email)
        for s in db.Student.select()
    ])


@app.route('/students', methods=['POST'])
@db.session
def upload_students():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))
