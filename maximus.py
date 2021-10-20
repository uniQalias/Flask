import pandas as pd
import json
import plotly
import plotly.express as px

def theJSONS():

    preparedJSON = {}

    recessionPeriods={
        1: ["2001-03-01", "2001-11-01"],
        2: ["2007-03-01", "2009-11-01"],
        3: ["2020-02-01", "2020-04-01"]
        }

    historicDictionary = {}
    with open("historicInfo.json", "r") as e:
        historicDictionary = json.load(e)

    #DFF = Effective Federal Fund Rate - Federal Reserve interest rate
    DFF = pd.DataFrame.from_dict(historicDictionary["FREDDFF Data"]["dataset"]["data"])
    fig = px.line(DFF,x=0, y=1, title="Federal Interest Rate", labels={"0":"Date", "1":"Interest Rate"})
    for i in recessionPeriods:
         fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
    preparedJSON["DFF"] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #DPRIME = Bank Prime Loan Rate - Rate at which banks lend to their client
    DPRIME = pd.DataFrame.from_dict(historicDictionary["FREDDPRIME Data"]["dataset"]["data"])
    fig = px.line(DPRIME,x=0, y=1, title="Bank Prime Loan Rate", labels={"0":"Date", "1":"Loan Rate"})
    for i in recessionPeriods:
         fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
    preparedJSON["DPRIME"] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #UNRATE = Civilian Unemployment Rate - Represents the number of unemployed as percentage of labour force
    UNRATE = pd.DataFrame.from_dict(historicDictionary["FREDUNRATE Data"]["dataset"]["data"])
    fig = px.line(UNRATE,x=0, y=1, title="Unemployment Rate", labels={"0":"Date", "1":"Unemployment Rate"})
    for i in recessionPeriods:
         fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
    preparedJSON["UNRATE"] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #GDPGR = GDP growth rate of US market
    GDPGR = pd.DataFrame.from_dict(historicDictionary["FREDY695RY2A224NBEA Data"]["dataset"]["data"])
    fig = px.line(GDPGR,x=0, y=1, title="GDP Growth Rate", labels={"0":"Date", "1":"Growth Rate"})
    for i in recessionPeriods:
         fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
    preparedJSON["GDPGR"] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #YIELD = US Treasury Yield Curve Rate
    YIELD = pd.DataFrame.from_dict(historicDictionary["USTREASURYYIELD Data"]["dataset"]["data"])
    fig = px.line(title="US Treasury Curve Rate")
    fig.add_scatter(x=YIELD[0], y=YIELD[1], mode='lines',name="1 Month Rate")
    fig.add_scatter(x=YIELD[0], y=YIELD[5], mode='lines',name="1 Year Rate")
    fig.update_xaxes(title_text='Dates')
    fig.update_yaxes(title_text='Curve Rate')
    for i in recessionPeriods:
         fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
    preparedJSON["YIELD"] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #SPCOMP = S&P500 Price
    #SP500_PE_RATIO_MONTH = S&P500 PE Ratio
    SPCOMP = pd.DataFrame.from_dict(historicDictionary["YALESPCOMP Data"]["dataset"]["data"])
    PERATIO = pd.DataFrame.from_dict(historicDictionary["MULTPLSP500_PE_RATIO_MONTH Data"]["dataset"]["data"])
    fig = px.line(title="S&P 500", log_y=True)
    fig.add_scatter(x=SPCOMP[0], y=SPCOMP[1], mode='lines',name=historicDictionary["YALESPCOMP Data"]['dataset']['column_names'][1])  
    fig.add_scatter(x=PERATIO[0], y=PERATIO[1], mode='lines', name=historicDictionary['MULTPLSP500_PE_RATIO_MONTH Data']['dataset']['name'])
    fig.update_xaxes(title_text='Dates')
    fig.update_yaxes(title_text='Values')
    for i in recessionPeriods:
         fig.add_vrect(x0=recessionPeriods[i][0], x1=recessionPeriods[i][1], fillcolor="LightSalmon", opacity=0.5, layer="below", line_width=0)
    preparedJSON["SP_PE"] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return preparedJSON