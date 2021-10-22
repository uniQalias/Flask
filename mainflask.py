from flask import Flask, render_template, request
import maximus

app = Flask(__name__)

@app.route("/")
def home():
   return render_template('home.html')

@app.route("/graphs.html")
def graphs():
   # Ensure dataset was selected
   if request.args.get("dataset") is not None:
      # Dataset selected by user
      type = request.args.get("dataset")

      # Get dataset plotly json information, store in dictionary
      # Start and end date is read from form submission, passed into method
      input = maximus.allDataframes(request.args.get("start_date"), request.args.get("end_date"))

      # Since input is a dictionary with all datasets, pass input[type] passes only the specified dataset's value to the HTML
      # If an error code was produced when getting information, also pass this to the HTML
      if "errorCode" in input:
         return render_template('graphs.html', input=input[type], errorCode=input["errorCode"])
      else:
         return render_template('graphs.html', input=input[type])
   # Dataset was not selected
   else:
      return render_template('graphs.html')

@app.route("/historicGraphsAll.html")
def historicGraphsAll():
   # Get dataset plotly json information, store in dictionary
   # Date range is hardcoded
   input = maximus.allDataframes('2000-01-01', '2021-01-01', historic = True)

   # Pass dictionary with all datasets to the HTML
   # If an error code was produced when getting information, also pass this to the HTML
   if "errorCode" in input:
      return render_template('historicGraphsAll.html', input=input, errorCode=input["errorCode"])
   else:
      return render_template('historicGraphsAll.html', input=input)
