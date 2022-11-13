from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from colorthief import ColorThief
import datetime
import os

UPLOAD_FOLDER = str(os.environ.get('my_folder'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
COLORS = []
filename = None
color_count = None
repeat = False

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('my_app')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

files_list = os.listdir('static')
for i in files_list:
    if i == 'styles.css':
        pass
    else:
        os.remove(f'static/{i}')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    global COLORS
    return render_template("index.html")


@app.route("/k", methods=["GET", "POST"])
def result():
    global COLORS, filename, color_count, repeat

    COLORS = []
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('home'))
        file = request.files['file']
        col_count = request.form.get("color_count")

        if col_count == "":
            color_count = 10
        else:
            color_count = int(col_count)

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('home'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            ct = ColorThief(file_path)
            the_pallete = ct.get_palette(color_count=int(color_count+1))
            first_colors = []
            for color in the_pallete:
                first_colors.append(f"#{color[0]:02x}{color[1] :02x}{color[2]:02x}")

            for q in first_colors:
                if q not in COLORS:
                    COLORS.append(q)

            if len(COLORS) != len(first_colors):
                repeat = True
            else:
                repeat = False

            return redirect(url_for('pallete'))


@app.route("/pallete", methods=["GET", "POST"])
def pallete():
    return render_template("pallete.html", colors=COLORS, file_path=filename, date=datetime.date.today().year,
                           len_of_col=len(COLORS), repeat=repeat)


if __name__ == "__main__":
    app.run(debug=True)
