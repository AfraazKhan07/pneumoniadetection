import json
import os
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, render_template, session, request, flash, redirect
import flask


with open("config.json", "r") as c:
    params = json.load(c)["params"]
import numpy as np

app = Flask(__name__, template_folder="template", static_folder="static")
app.secret_key = "super-secret-key"
# app.secret_key = 'super-secret-key'
# app.config['UPLOAD_FOLDER'] = params['upload_location']

Model = load_model(r"models\model.h5")


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(150, 150))
    img = image.img_to_array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img)

    if preds[0][0] > 0.5:
        return "Pneumonia", preds[0][0]

    else:
        return "Normal", preds[0][0]


@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session and session["user"] == params["admin_user"]:
        return render_template("form.html", params=params)

    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if username == params["admin_user"] and userpass == params["admin_password"]:
            # set the session variable
            session["user"] = username
            return render_template("form.html", params=params)
    return render_template("login.html", params=params)

@app.route("/uploader", methods=["GET", "POST"])
def uploader():
    if request.method == "POST":
        pname = request.form.get("pname")
        print(pname)
        age = request.form.get("age")
        print(age)
        confusion = request.form.get("confusion")
        print(confusion)
        rr = request.form.get("rr")
        print(rr)
        bp = request.form.get("bp")
        print(bp)
        uremia = request.form.get("uremia")
        print(uremia)
        f = request.files["file1"]
        basepath = os.path.dirname(__file__)
        filepath = os.path.join(basepath, "uploaded_files", secure_filename(f.filename))
        f.save(filepath)
        predict, percent = model_predict(filepath, Model)

        aflag=0
        cflag=0
        bpflag=0
        rrflag=0
        uflag=0
        if int(age)<65:
            aflag=0
        else:
            aflag=1

        if confusion == "no":
            cflag = 0
        else:
            cflag = 1

        if int(bp) > 90:
            bpflag = 0
        else:
            bpflag = 1

        if int(rr) < 30:
            rrflag = 0
        else:
            rrflag = 1

        if int(uremia) < 20:
            uflag = 0
        else:
            uflag = 1

        sscore = aflag+cflag+bpflag+rrflag+uflag
        if sscore==0:
            mortality = 0.7
            mgmt = "Treat as outpatient"
        if sscore == 1:
            mortality = 2.1
            mgmt = "Treat as outpatient"
        if sscore == 2:
            mortality = 9.2
            mgmt = "Admit to wards"
        if sscore == 3:
            mortality = 14.5
            mgmt = "ICU"
        if sscore == 4:
            mortality = 40
            mgmt = "ICU"
        if sscore == 5:
            mortality = 57
            mgmt = "ICU"
        print(mortality)
        return render_template(
            "prediction.html", prediction_text="We have predicted : {} , Confidence is ={} , Mortality is ={} and Management is ={}".format(predict, percent, mortality, mgmt)
        )

@app.route("/login", methods=["GET", "POST"])
def logout():
    session.clear()
    session.pop('user')
    return render_template("login.html",params = "params")


app.run(debug=True)
