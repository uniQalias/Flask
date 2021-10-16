from flask import Flask, render_template, request, redirect
import pandas as pd
import json
import plotly
import plotly.express as px

historicDictionary = {}

with open("historicInfo.json", "r") as e:
   historicDictionary = json.load(e)

app = Flask(__name__)

@app.route("/")
def home():
   return render_template('home.html')

@app.route("/historicGraphs.html")
def historicGraphs():

   type = request.args.get("graph")

   if type == "DFF":
      #DFF = Effective Federal Fund Rate - Federal Reserve interest rate
      DFF = pd.DataFrame.from_dict(historicDictionary["FREDDFF Data"]["dataset"]["data"])
      fig = px.line(DFF,x=0, y=1, title="Federal Interest Rate", labels={"0":"Date", "1":"Interest Rate"})

   if type == "DPRIME":
      #DPRIME = Bank Prime Loan Rate - Rate at which banks lend to their client
      DPRIME = pd.DataFrame.from_dict(historicDictionary["FREDDPRIME Data"]["dataset"]["data"])
      fig = px.line(DPRIME,x=0, y=1, title="Bank Prime Loan Rate", labels={"0":"Date", "1":"Loan Rate"})

   if type == "UNRATE":
      #UNRATE = Civilian Unemployment Rate - Represents the number of unemployed as percentage of labour force
      UNRATE = pd.DataFrame.from_dict(historicDictionary["FREDUNRATE Data"]["dataset"]["data"])
      fig = px.line(UNRATE,x=0, y=1, title="Unemployment Rate", labels={"0":"Date", "1":"Unemployment Rate"})

   if type == "YIELD":
      #YIELD = US Treasury Yield Curve Rate
      YIELD = pd.DataFrame.from_dict(historicDictionary["USTREASURYYIELD Data"]["dataset"]["data"])
      fig = px.line(YIELD, title="US Treasury Yield Data")
      fig.add_scatter(x=YIELD[0], y=YIELD[1], mode='lines',name="1 Month Rate")
      fig.add_scatter(x=YIELD[0], y=YIELD[5], mode='lines',name="1 Year Rate")
      fig.update_xaxes(title_text='Dates')
      fig.update_yaxes(title_text='US Treasury Yield Curve Rate')

   if type == "SP_PE":   
      #SPCOMP = S&P500 Price
      #SP500_PE_RATIO_MONTH = S&P500 PE Ratio
      SPCOMP = pd.DataFrame.from_dict(historicDictionary["YALESPCOMP Data"]["dataset"]["data"])
      PERATIO = pd.DataFrame.from_dict(historicDictionary["MULTPLSP500_PE_RATIO_MONTH Data"]["dataset"]["data"])
      fig = px.line(SPCOMP,title="S&P 500", log_y=True)
      fig.add_scatter(x=SPCOMP[0], y=SPCOMP[1], mode='lines',name=historicDictionary["YALESPCOMP Data"]['dataset']['column_names'][1])  
      fig.add_scatter(x=PERATIO[0], y=PERATIO[1], mode='lines', name=historicDictionary['MULTPLSP500_PE_RATIO_MONTH Data']['dataset']['name'])
      fig.update_xaxes(title_text='Dates')
      fig.update_yaxes(title_text='Values')

      #GDP
      # GDP = pd.DataFrame.from_dict(historicDictionary[""]["dataset"]["data"])
      # fig = px.line(GDP, x="date", y="value", title="Gross Dosmetic Product Rate" ,labels={"date": "Date", "value": "GDP Rate"})

   if request.args.get("graph") is not None:
      fig.add_vrect(x0="2001-03-01", x1="2001-11-01", fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
      fig.add_vrect(x0="2007-03-01", x1="2009-11-01", fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
      fig.add_vrect(x0="2020-02-01", x1="2020-04-01", fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
      return render_template('historicGraphs.html', graphJSON=graphJSON)   
   else:
      return render_template('historicGraphs.html')
