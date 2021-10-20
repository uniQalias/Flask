from flask import Flask, render_template, request
import maximus

app = Flask(__name__)

@app.route("/")
def home():
   return render_template('home.html')

@app.route("/historicGraphs.html")
def historicGraphs():
   type = request.args.get("graph")

   if request.args.get("graph") is not None:
      return render_template('historicGraphs.html', graphJSON=maximus.theJSONS()[type])
   else:
      return render_template('historicGraphs.html')

@app.route("/historicGraphsAll.html")
def historicGraphsAll():
   input = maximus.theJSONS()
   return render_template('historicGraphsAll.html', input=input)