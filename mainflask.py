from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home_page():
    if request.method == 'GET':
        return render_template("home.html")
    if request.method == 'POST':
        return render_template("greet.html", name = request.form.get("name", "world"))