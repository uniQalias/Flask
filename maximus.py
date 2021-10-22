import pandas as pd
import json
import plotly
import plotly.express as px
import requests
import time
import datetime
import os

jsonPath = "static/historicInfo.json"

def jsonChecker():
     if not os.path.exists(jsonPath):
          print("JSON does not exist, Updating!")
          jsonUpdater()

     dictionary = {}
     with open(jsonPath, "r") as e:
          dictionary = json.load(e)

     if dictionary["lastUpdate"] != str(datetime.date.today()):
          print("JSON Updating!")
          jsonUpdater()
     else:
          print("JSON Up to Date!")

def jsonUpdater():
     #catogory
     #FRED = US Federal Reserve
     #USTREASURY = US Treasury
     #YALE = Yale department of Econ, Check SNP500 Price, Market confidence index
     #MULTPL = S&P500 Ratios
     categories = ["FRED", "USTREASURY", "YALE", "MULTPL"]

     #indicator / datatype code
     #DFF = Effective Federal Fund Rate - Federal Reserve interest rate
     #DPRIME = Bank Prime Loan Rate - Rate at which banks lend to their client
     #UNRATE = Civilian Unemployment Rate - Represents the number of unemployed as percentage of labour force
     #YIELD = US Treasury Yield Curve Rate
     #SPCOMP = S&P500 Price
     #SP500_PE_RATIO_MONTH = S&P500 PE Ratio
     #Y695RY2A224NBEA = GDP Growth Rate in USA
     FREDCode = ["DFF", "DPRIME", "UNRATE", "Y695RY2A224NBEA"]
     USTREASURYCode = ["YIELD"]
     YALECode = ["SPCOMP"]
     MULTPLCode = ["SP500_PE_RATIO_MONTH"]

     def retreiveData(category, dataCode):
     #setting delay to prevent IP softban from 429: Too many request
          time.sleep(4)
          #setting NASDEQ datalink API URL, adding catagory and datacode
          url = "https://data.nasdaq.com/api/v3/datasets/"
          url = url + category + "/" + dataCode + "/"

          #setting standard filters / API Key
          querystring={
          "access_key":"8c5eBM5zY6Yw8DdsBpek",
          "start_date":"1950-01-01",
          "end_date":str(datetime.date.today()),
          }

          #executing requests
          payload={}
          headers={}
          response = requests.request("GET", url, headers=headers, data=payload, params=querystring)
          if response.ok:
               print("Status: OK")
               time.sleep(1)
               #request is good, converting to json
               data = response.json()
               #returning json data
               return data

          else:
               #catching error
               status = response.status_code
               reason = response.reason
               print("REQUEST ERROR: ", status, reason)
               time.sleep(1)
               exit()


     #MAIN Section Calling REQUEST function for all required DATA
     datas = {}
     for category in categories:
          if category == "FRED":
               for code in FREDCode:
                    name = category + code + " Data"
                    print(name)
                    datas[name] = retreiveData(category, code)
          elif category == "USTREASURY":
               for code in USTREASURYCode:
                    name = category + code + " Data"
                    print(name)
                    datas[name] = retreiveData(category, code)
          elif category == "YALE":
               for code in YALECode:
                    name = category + code + " Data"
                    print(name)
                    datas[name] = retreiveData(category, code)
          elif category == "MULTPL":
               for code in MULTPLCode:
                    name = category + code + " Data"
                    print(name)
                    datas[name] = retreiveData(category, code)
          else:
               print("Skipped a category")

     datas["lastUpdate"] = str(datetime.date.today())
     
     with open(jsonPath, "w") as e:
          json.dump(datas, e)

     #if facing 429 Error, wait for cooldown about 1 to 2 mins and try again
     #datas is a nested dictionary, with each key being the name of the data, and the value being the RAW data in dictionary format


def dataframeGen(dictionary, dataset, start_date, end_date, historic):

     recessionPeriods = {
        1: ["2001-03-01", "2001-11-01"],
        2: ["2007-03-01", "2009-11-01"],
        3: ["2020-02-01", "2020-04-01"]
     }

     if dataset == "DFF":
          DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDDFF Data"]["dataset"]["data"])
          DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
          fig = px.line(DATAFRAME, x=0, y=1, title="Federal Interest Rate",labels={"0": "Date", "1": "Interest Rate"})

     if dataset == "DPRIME":
          DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDDPRIME Data"]["dataset"]["data"])
          DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
          fig = px.line(DATAFRAME, x=0, y=1, title="Bank Prime Loan Rate",labels={"0": "Date", "1": "Loan Rate"})

     if dataset == "UNRATE":
          DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDUNRATE Data"]["dataset"]["data"])
          DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
          fig = px.line(DATAFRAME, x=0, y=1, title="Unemployment Rate",labels={"0": "Date", "1": "Unemployment Rate"})

     if dataset == "YIELD":
          fig = px.line(title="US Treasury Curve Rate")
          fig.update_xaxes(title_text='Dates')
          fig.update_yaxes(title_text='Curve Rate')
          DATAFRAME = pd.DataFrame.from_dict(dictionary["USTREASURYYIELD Data"]["dataset"]["data"])
          DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
          fig.add_scatter(x=DATAFRAME[0], y=DATAFRAME[1],mode='lines', name="1 Month Rate")
          fig.add_scatter(x=DATAFRAME[0], y=DATAFRAME[5],mode='lines', name="1 Year Rate")
     
     if dataset == "GDPGR":
          DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDY695RY2A224NBEA Data"]["dataset"]["data"])
          DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
          fig = px.line(DATAFRAME, x=0, y=1, title="GDP Growth Rate",labels={"0": "Date", "1": "Growth Rate"})

     if dataset == "SPCOMP":
          DATAFRAME = pd.DataFrame.from_dict(dictionary["YALESPCOMP Data"]["dataset"]["data"])
          DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
          fig = px.line(DATAFRAME, x=0, y=1, title="S&P 500 Price",labels={"0": "Date", "1": "Value"})

     if dataset == "PERATIO":
          DATAFRAME = pd.DataFrame.from_dict(dictionary["MULTPLSP500_PE_RATIO_MONTH Data"]["dataset"]["data"])
          DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
          fig = px.line(DATAFRAME, x=0, y=1, title="S&P 500 PE Ratio",labels={"0": "Date", "1": "Value"})

     if historic == True:
          for i in recessionPeriods:
               fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)

     return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def allDataframes(start_date, end_date, historic = False):
     jsonChecker()

     preparedJSON = {}
     datasets = ["DFF", "DPRIME", "UNRATE", "YIELD", "GDPGR", "SPCOMP", "PERATIO"]

     dictionary = {}
     with open(jsonPath, "r") as e:
          dictionary = json.load(e)

     for i in datasets:
          preparedJSON[i] = dataframeGen(dictionary, i, start_date, end_date, historic)

     return preparedJSON
