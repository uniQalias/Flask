import pandas as pd
import json
import plotly
import plotly.express as px
import requests
import time
import datetime
import os


dir = os.path.dirname(__file__)
jsonPath = os.path.join(dir, "static/datasetInfo.json")

def jsonChecker():
     """This process checks whether the json exists and whether it is up to date. If these two conditions are not fulfilled,
     it will run jsonUpdater() to update the json. If jsonUpdater() returns an error, it will also return that error, as well
     as the date when the dataset was last updated."""

     errorCodeIfAny = ""

     # Creates file if it doesnt exist
     if not os.path.exists(jsonPath):
          print("JSON does not exist, Creating!")
          e = open(jsonPath, "w")
          e.write("{\"lastUpdate\": \"Never\"}")
          e.close

     # Load datasetInfo.json into dictionary
     dictionary = {}
     with open(jsonPath, "r") as e:
          dictionary = json.load(e)

     # If "lastUpdate" key does not match current day, run jsonUpdater()
     if dictionary["lastUpdate"] != str(datetime.date.today()):
          print("JSON Updating!")
          # If jsonUpdater() returns an error, record it
          errorCodeIfAny = jsonUpdater()
     else:
          print("JSON Up to Date!")

     # Returns error code if error thrown
     if errorCodeIfAny:
          return errorCodeIfAny  + " (this dataset's latest date: " + dictionary["lastUpdate"] + ")"


def jsonUpdater():
     """This process queries the API to create a dictionary where each key is the name of the data, 
     and the value is the RAW data. If it succeeds in doing this, it will write the dictionary to 
     datasetInfo.json. In the event any error is thrown, it will break out of the process and not
     change datasetInfo.json, so the outdated data can still be used. It will also return the error.
     (If facing 429 Error, wait for cooldown about 1 to 2 mins and try again, usually works)"""

     #category
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
     # setting delay to prevent IP softban from 429: Too many request
          time.sleep(4)
          # setting NASDEQ datalink API URL, adding catagory and datacode
          url = "https://data.nasdaq.com/api/v3/datasets/"
          url = url + category + "/" + dataCode + "/"

          # setting standard filters / API Key
          querystring={
          "access_key":"8c5eBM5zY6Yw8DdsBpek",
          "start_date":"1950-01-01",
          "end_date":str(datetime.date.today()),
          }

          # executing requests
          payload={}
          headers={}
          response = requests.request("GET", url, headers=headers, data=payload, params=querystring)
          if response.ok:
               print("Status: OK")
               time.sleep(1)
               # request is good, converting to json
               data = response.json()
               # returning json data
               return data

          else:
               #catching error
               status = str(response.status_code)
               reason = str(response.reason)
               print("REQUEST ERROR: " + status + " " + reason)
               time.sleep(1)
               # returning a list with 2 values: status and reason
               return [status, reason]

     # MAIN Section to Call REQUEST function for all required DATA
     datas = {}
     errorCodeIfAny = ""

     for category in categories:
          # if error code exists, break out of loop
          if errorCodeIfAny:
               break

          if category == "FRED":
               for code in FREDCode:
                    name = category + code + " Data"
                    print(name)
                    retrievedValue = retreiveData(category, code)
                    # if retrievedValue is a string, its a proper dataset, load into dictionary
                    # if retrievedValue is a list, its an error code, store error code and break out of loop
                    if type(retrievedValue) is not list: 
                         datas[name] = retrievedValue
                    else:
                         errorCodeIfAny = retrievedValue[0] + " " + retrievedValue[1]
                         break
          elif category == "USTREASURY":
               for code in USTREASURYCode:
                    name = category + code + " Data"
                    print(name)
                    retrievedValue = retreiveData(category, code)
                    if type(retrievedValue) is not list: 
                         datas[name] = retrievedValue
                    else:
                         errorCodeIfAny = retrievedValue[0] + " " + retrievedValue[1]
                         break
          elif category == "YALE":
               for code in YALECode:
                    name = category + code + " Data"
                    print(name)
                    retrievedValue = retreiveData(category, code)
                    if type(retrievedValue) is not list: 
                         datas[name] = retrievedValue
                    else:
                         errorCodeIfAny = retrievedValue[0] + " " + retrievedValue[1]
                         break
          elif category == "MULTPL":
               for code in MULTPLCode:
                    name = category + code + " Data"
                    print(name)
                    retrievedValue = retreiveData(category, code)
                    if type(retrievedValue) is not list: 
                         datas[name] = retrievedValue
                    else:
                         errorCodeIfAny = retrievedValue[0] + " " + retrievedValue[1]
                         break
          else:
               print("Skipped a category")

     # if no error code, write contents of dictionary and new updated date to datasetInfo.json
     # if error code exists, don't change datasetInfo.json and return error code
     if not errorCodeIfAny:
          datas["lastUpdate"] = str(datetime.date.today())
          with open(jsonPath, "w") as e:
               json.dump(datas, e)
     else:
          return errorCodeIfAny


def dataframeGen(dataset, start_date, end_date, historic):
     """This method prepares dataframes which is used to render graphs. It takes in a dataset, the start and end 
     date, as well as whether it is intended to be displayed in the historical section. It then returns a json object
     based on these inputs. If the data is to be displayed in the historical section, it will render recession
     periods and not include date requested in the title. If for any reason the dataset is not found in the 
     dictionary, it returns an empty string."""

     # If not historic, populates dateIndicator which will be used in dataframe titles
     dateIndicator=""
     if historic == False:
          dateIndicator = " [" + start_date + " to " + end_date + "]"

     # Recession periods
     recessionPeriods = {
        1: ["2001-03-01", "2001-11-01"],     # dotcom Bubble
        2: ["2007-03-01", "2009-11-01"],     # Great Recession
        3: ["2020-02-01", "2020-04-01"]      # COVID-19 Recession
     }
     
     # opens datasetInfo.json, load to dictionary
     dictionary = {}
     with open(jsonPath, "r") as e:
          dictionary = json.load(e)

     # dataset exists as key in dictionary
     try:
          if dataset == "DFF":
               # reads corresponding key in dictionary, places data into dataframe
               DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDDFF Data"]["dataset"]["data"])
               # narrow dataframe to within specified dates
               DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
               # convert dataframe to plotly data
               fig = px.line(DATAFRAME, x=0, y=1, title="Federal Interest Rate" + dateIndicator, labels={"0": "Date", "1": "Interest Rate"})

          if dataset == "DPRIME":
               DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDDPRIME Data"]["dataset"]["data"])
               DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
               fig = px.line(DATAFRAME, x=0, y=1, title="Bank Prime Loan Rate" + dateIndicator, labels={"0": "Date", "1": "Loan Rate"})

          if dataset == "UNRATE":
               DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDUNRATE Data"]["dataset"]["data"])
               DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
               fig = px.line(DATAFRAME, x=0, y=1, title="Unemployment Rate" + dateIndicator, labels={"0": "Date", "1": "Unemployment Rate"})

          if dataset == "YIELD":
               fig = px.line(title="US Treasury Curve Rate" + dateIndicator)
               fig.update_xaxes(title_text='Dates')
               fig.update_yaxes(title_text='Curve Rate')
               DATAFRAME = pd.DataFrame.from_dict(dictionary["USTREASURYYIELD Data"]["dataset"]["data"])
               DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
               fig.add_scatter(x=DATAFRAME[0], y=DATAFRAME[1],mode='lines', name="1 Month Rate")
               fig.add_scatter(x=DATAFRAME[0], y=DATAFRAME[5],mode='lines', name="1 Year Rate")
          
          if dataset == "GDPGR":
               DATAFRAME = pd.DataFrame.from_dict(dictionary["FREDY695RY2A224NBEA Data"]["dataset"]["data"])
               DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
               fig = px.line(DATAFRAME, x=0, y=1, title="GDP Growth Rate" + dateIndicator, labels={"0": "Date", "1": "Growth Rate"})

          if dataset == "SPCOMP":
               DATAFRAME = pd.DataFrame.from_dict(dictionary["YALESPCOMP Data"]["dataset"]["data"])
               DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
               fig = px.line(DATAFRAME, x=0, y=1, title="S&P 500 Price" + dateIndicator, labels={"0": "Date", "1": "Value"})

          if dataset == "PERATIO":
               DATAFRAME = pd.DataFrame.from_dict(dictionary["MULTPLSP500_PE_RATIO_MONTH Data"]["dataset"]["data"])
               DATAFRAME = DATAFRAME[(DATAFRAME[0] >= start_date) & (DATAFRAME[0] <= end_date)]
               fig = px.line(DATAFRAME, x=0, y=1, title="S&P 500 PE Ratio" + dateIndicator, labels={"0": "Date", "1": "Value"})

          # if historic, draw regions of recession periods
          if historic == True:
               for i in recessionPeriods:
                    fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)

          # convert plotly data to json, return this json
          return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

     # key not found in dictionary
     except KeyError:
          return ""


def allDataframes(start_date, end_date, historic = False):
     """This method is called by the main flask application whenever it needs graph information.
     Firstly, it runs jsonChecker() to ensure datasetInfo.json is up to date. Then, It returns a 
     dictionary with datasets as keys and plotly data as corresponding values. Additionally, if 
     any error code is present, it also adds it to this dictionary as a separate key-value pair."""

     errorCodeIfAny = ""
     # If jsonChecker() returns error, record it
     errorCodeIfAny = jsonChecker()

     preparedJSON = {}
     allDatasets = ["DFF", "DPRIME", "UNRATE", "YIELD", "GDPGR", "SPCOMP", "PERATIO"]

     # Populate preparedJSON with dataset key(dataset)-value(plotly json) pairs
     for dataset in allDatasets:
          preparedJSON[dataset] = dataframeGen(dataset, start_date, end_date, historic)

     # If there was an error updating datasetInfo.json, add error code to preparedJSON as another key-value pair
     if errorCodeIfAny:
          preparedJSON["errorCode"] = errorCodeIfAny
          
     return preparedJSON

def allPredictedDataframes():
     """This method is called by the main flask application whenever it needs the prediction
     graph data. It reads each prediction json file, creates a key(dataset)-value(plotly data) 
     pair for each one, and places these pairs in a dictionary and returns it."""

     jsonFiles=[
          "static/predict_datasetsjson/FREDDFF Data.json",
          "static/predict_datasetsjson/FREDDPRIME Data.json",
          "static/predict_datasetsjson/FREDUNRATE Data.json",
          "static/predict_datasetsjson/MULTPLSP500_PE_RATIO_MONTH Data.json",
          "static/predict_datasetsjson/USTREASURYYIELD 1 Month Data.json",
          "static/predict_datasetsjson/USTREASURYYIELD 1 Year Data.json",
          "static/predict_datasetsjson/YALESPCOMP Data.json"
          ]

     dictionary = {}
     preparedJSON = {}

     # Runs for each file listed in jsonFiles
     for file in jsonFiles:

          # Opens dataset, load to dictionary
          with open(os.path.join(dir, file), "r") as e:
               dictionary = json.load(e)

          # Obtain dataset name by trimming file name
          datasetName = file
          datasetName = datasetName.replace("static/predict_datasetsjson/", "")
          datasetName = datasetName.replace(".json", "")

          # reads corresponding key in dictionary, places data into dataframe
          DATAFRAME = pd.DataFrame.from_dict(dictionary["data"])
          # trims unnecessary text in date
          DATAFRAME["0"] = DATAFRAME["0"].str.replace("T00:00:00.000Z", "", regex=True)
          fig = px.line(title=datasetName)
          fig.update_xaxes(title_text='Data')
          fig.update_yaxes(title_text='Values')
          fig.add_scatter(x=DATAFRAME["0"], y=DATAFRAME["Value"],mode='lines', name="Actual Value")
          fig.add_scatter(x=DATAFRAME["0"], y=DATAFRAME["Predictions"],mode='lines', name="Predicted Value")
          # convert dataframe to plotly data, load into preparedJSON with key being datasetName and value being plotly data
          preparedJSON[datasetName] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

     return preparedJSON