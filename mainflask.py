from flask import Flask, render_template, request
import maximus

app = Flask(__name__)

@app.route("/")
def home():
   return render_template('home.html')

@app.route("/graphs.html")
def historicGraphs():
   type = request.args.get("dataset")

   if request.args.get("dataset") is not None:
      input = maximus.allDataframes(request.args.get("start_date"), request.args.get("end_date"))[type]
      return render_template('graphs.html', input=input)
   else:
      return render_template('graphs.html')

@app.route("/historicGraphsAll.html")
def historicGraphsAll():
   input = maximus.allDataframes('2000-01-01', '2021-01-01', historic = True)
   return render_template('historicGraphsAll.html', input=input)
