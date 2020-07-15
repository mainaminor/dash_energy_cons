import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = ['https://codepen.io/mainaminor/pen/wvaOEmY.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, 
  meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Global Energy Consumption</title>
        <meta property="og:title" content="Global Energy Consumption">
        <meta name="image" property="og:image" content="assets/energy_cons.png">
        <meta name="description" property="og:description" content="An interactive mini-dashboard built and deployed by me in Python, giving a summary of energy use by country and type.">
        <meta name="author" content="Anthony S N Maina">
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

server = app.server

##############################
####### DATA TABLES ##########
##############################

master_cons=pd.read_csv("data/master_cons.csv")
energy_int=pd.read_csv("data/energy_int.csv")
obj=pd.read_json("data/IntEnergyCons.json")


cat=['Total energy consumption from coal',
       'Total energy consumption',
       'Total energy consumption from petroleum and other liquids',
       'Total energy consumption from natural gas',
       'Total energy consumption from nuclear, renewables, and other']

cats=[]
label=[]
country=[]

for i in obj["name"]:
    if 'Total energy consumption from nuclear, renewables, and other' in i:
        cats.append('Total energy consumption from nuclear, renewables, and other')
    else:
        for c in cat:
            if c == i.split(",")[0]:
                cats.append(c)


for c in cats:
    if c=="Total energy consumption":
        label.append("Total energy consumption")
    else:
        label.append(c.split("Total energy consumption from ")[1].capitalize())
        

for n in obj["name"]:
    if 'Total energy consumption from nuclear, renewables, and other' in n:
        country.append(n.split(', ')[3])
    else:
        country.append(n.split(", ")[1])

obj["label"]=label
obj["country"]=country

lv=[]

for i in range(len(obj["data"])):
    lv.append(obj["data"].iloc[i][-1]["value"])

obj["lastValue"]=lv

obj.drop(obj[obj["lastValue"]=="--"].index, inplace=True)


metrics=[
      {'label': 'Coal', 'value': 'Coal'},
      {'label': 'Natural gas', 'value': 'Natural gas'},
      {'label': 'Nuclear, renewables, and other', 'value': 'Nuclear, renewables, and other'},
      {'label': 'Petroleum and other liquids', 'value':  'Petroleum and other liquids'},
      {'label': 'Total energy consumption', 'value': 'Total energy consumption'},
      {'label': 'Total energy consumption per capita', 'value': 'Energy consumption per capita'},
      {'label': 'Total energy consumption per GDP', 'value': 'Energy consumption per GDP'}
  ]


countries = []
for tic in obj["country"].drop_duplicates().sort_values():
  countries.append({'label':tic, 'value':tic})

def rank_statement(label, country, metric):
    subset=master_cons[master_cons["label"]==label]
    rank=int(subset[metric].rank(method="max", ascending=False).loc[subset[subset["country"]==country].index.values[0]])
    if metric == "TBtuUSD":
        label_clean="Total energy use per GDP"
    elif metric=="MBtuPP":
        label_clean="Total energy use per capita"
    elif metric=="dependence":
        label_clean="% dependence on "+label
    else:
        label_clean=label

    if label== "Nuclear, renewables, and other" and metric=="dependence":
        label_clean="fossil fuel independence"
    
    if label== "Nuclear, renewables, and other" and metric=="FF_dependence":
        label_clean="fossil fuel dependence"
         
    return "Ranks number {} in the world for {}".format(rank, label_clean)

################################
###### LAYOUT COLORS ###########
################################

boxcolor="#F5F5F5"
background="#FFFFFF"
headercolor="#3d3d5c"


#WORLD & US MAPS
l_map=go.Layout(
    height=670,
    margin={"r":0,"t":0,"l":0,"b":0},
    geo={
    'visible': True, 
    'resolution':50, 
    'showcountries':True, 
    'countrycolor':"grey",
    'showsubunits':True, 
    'subunitcolor':"White",
    'showframe':False,
    'coastlinecolor':"slategrey",
    'countrycolor':'white',
    }
)


#WORLD BARS
l_bar_w=go.Layout(
  height=350,
  #width=90,
  margin={"r":20,"t":60,"l":40,"b":20},
  #template="plotly_white",
  plot_bgcolor=boxcolor,
  paper_bgcolor=boxcolor,
  yaxis={"tickfont":{"size":12},"gridwidth":2},
  xaxis={"tickfont":{"size":12}},
  legend={'orientation':'h','x':0.08, 'y':-0.2,'font':{'size':12}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#SIMPLE BARS
l_bar_s=go.Layout(
  height=225,
  margin={"r":10,"t":10,"l":10,"b":20},
  #template="plotly_white",
  plot_bgcolor=boxcolor,
  paper_bgcolor=boxcolor,
  yaxis={"tickfont":{"size":10}},
  xaxis={"tickfont":{"size":10},"gridwidth":2},
  font={"size":10},
  legend={'x':0.02, 'y':0.96, 'font':{'size':10}, 'itemclick': 'toggleothers'},
  dragmode=False
  )

#HIDE MODEBAR
conf = {'displayModeBar': False}



###############################
######## CHARTS ###############
###############################


def make_fig_2(country):
  geo=country
  k=obj["data"][obj["country"]==geo]

  x=[]
  y=[]
  name="Petroleum and other liquids"
  for i in range(len(k[obj["label"]==name].iloc[0])):
      x.append(pd.to_datetime(k[obj["label"]==name].iloc[0][i]["date"], unit="ms"))
      y.append(k[obj["label"]==name].iloc[0][i]["value"])

  x2=[]
  y2=[]
  name2="Coal"
  for i in range(len(k[obj["label"]==name2].iloc[0])):
      x2.append(pd.to_datetime(k[obj["label"]==name2].iloc[0][i]["date"], unit="ms"))
      y2.append(k[obj["label"]==name2].iloc[0][i]["value"])
      
  x3=[]
  y3=[]
  name3="Natural gas"
  for i in range(len(k[obj["label"]==name3].iloc[0])):
      x3.append(pd.to_datetime(k[obj["label"]==name3].iloc[0][i]["date"], unit="ms"))
      y3.append(k[obj["label"]==name3].iloc[0][i]["value"])
      
  x4=[]
  y4=[]
  name4="Nuclear, renewables, and other"
  for i in range(len(k[obj["label"]==name4].iloc[0])):
      x4.append(pd.to_datetime(k[obj["label"]==name4].iloc[0][i]["date"], unit="ms"))
      y4.append(k[obj["label"]==name4].iloc[0][i]["value"])

  fig = go.Figure()
  fig.add_trace(go.Bar(
      x=x, 
      y=y,
      hoverinfo='name+y',
      name=name
  ))
  fig.add_trace(go.Bar(
      x=x2, 
      y=y2,
      hoverinfo='name+y',
      name=name2
  ))
  fig.add_trace(go.Bar(
      x=x3, 
      y=y3,
      hoverinfo='name+y',
      name=name3
  ))
  fig.add_trace(go.Bar(
      x=x4, 
      y=y4,
      hoverinfo='name+y',
      name=name4
  ))
  fig.update_layout(barmode='stack')
  fig.update_layout(l_bar_w)
  return fig

def make_fig_3(d, label, metric):
    fig = go.Figure(go.Bar(y=d[d["label"]==label].sort_values(by=metric, ascending=True)["country"][-10:],
                          x=d[d["label"]==label].sort_values(by=metric,ascending=True)[metric][-10:],
                         orientation='h'
                        )
                 )
    fig.update_layout(l_bar_s)
    return fig



################################################
#### APP LAYOUT  ###############################
################################################

app.layout = html.Div([

  html.Div([#header
    html.Div([
      html.H3("Global Energy Consumption", style={"color": headercolor, "marginBottom": "0.2%"}),
      html.P('Data source: U.S. Energy Information Administration. Per GDP numbers are on a purchasing power parity (PPP) basis, and based on the 2015 value of the US dollar',style={'font-size': '1rem','color':'#696969',"marginBottom": "0%"}),
      ],
    className='row',
    style={'paddingTop':'1%', 'text-align':'center', "marginBottom":"1%"}
    ),
  html.Div([#body
    html.Div([#left six columns
      html.H5("Worldwide, as of 2017", style={"color": headercolor, "marginBottom": "2%"}),
      html.Div([
        dcc.Dropdown(
          id='metric-select',
          options = metrics[4:],
          value = "Total energy consumption",
          multi = False
          )
        ],
        style={'marginBottom':'2%'}
        ),
      dcc.Graph(id="world", config=conf)
      ],
      style={'background-color':boxcolor,'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'1%', 'marginBottom':'2%'},
      className='six columns flex-display'
      ),
    html.Div([#right six columns
      html.Div([#right top half row
        html.H5("By energy source", style={"color": headercolor, "marginBottom": "2%"}),
        html.Div([
          dcc.Dropdown(
          id='metric-select1b',
          options = countries,
          value = "World",
          multi = False
          )
          ],
          style={'marginBottom':'1%'}
          ),
        html.Div([
          dcc.Graph(id="country-trend", 
            figure=make_fig_2("World"), 
            config=conf, 
            className= 'nine columns flex-display'
            ),
          html.Div([
            html.P(id="ff_title", style={"marginBottom":"5%"}),
            html.Ul([
              html.Li(id="li1", style={"font-size": "1.5rem"}),
              html.Li(id="li2", style={"font-size": "1.5rem"}),
              html.Li(id="li4", style={"font-size": "1.5rem"})
              ], 
              style={"list-style-position": "outside", "marginLeft":"10%", "vertical-align":"middle"},
              ),
            ],
            className='three columns flex-display',
            style={"paddingLeft":"0%","paddingRight":"2%","marginTop":"0%"}
            )
          ],
          style={"display": "table"}
          ),
        ],
        className='row',
        style={'background-color':boxcolor, 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'2%', 'marginBottom':'1%'},
        ),
      html.Div([#right bottom half row
        html.Div([#four columns for absolute bars
          html.H6("Top 10: Energy consumption", style={"color": headercolor, "marginBottom": "2%"}),
          html.Div([
            dcc.Dropdown(
              id='metric-select2',
              options = metrics[0:5],
              value = "Total energy consumption",
              multi = False
              )
            ],
            style={'marginBottom':'4%','font-size': '1.2rem'}
            ),
          dcc.Graph(id="top-n-abs", figure=make_fig_3(master_cons.drop_duplicates(), "Total energy consumption", "lastValue"), config=conf)
          ],
          className="four columns",
          style={'background-color':boxcolor, 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey','padding':'1%','marginBottom':'2%'},
          ),
        html.Div([#four columns for dependency bars
          html.H6("Top 10: Relative dependence", style={"color": headercolor, "marginBottom": "2%"}),
          html.Div([
            dcc.Dropdown(
              id='metric-select3',
              options = metrics[0:4],
              value = "Coal",
              multi = False
              )
            ],
            style={'marginBottom':'4%','font-size': '1.2rem'}
            ),
          dcc.Graph(id="top-n-dependency", figure=make_fig_3(energy_int, "Energy consumption per GDP", "lastValue"), config=conf)
          ],
          className="four columns",
          style={'background-color':boxcolor, 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey', 'padding':'1%','marginBottom':'2%'},
          ),
        html.Div([#four columns for intensity bars
          html.H6("Top 10: Energy intensity", style={"color": headercolor, "marginBottom": "2%"}),
          html.Div([
            dcc.Dropdown(
              id='metric-select4',
              options = metrics[5:],
              value ="Energy consumption per capita",
              multi = False
              )
            ],
            style={'marginBottom':'4%','font-size': '1.2rem'}
            ),
          dcc.Graph(id="top-n-intensity", config=conf)
          ],
          className="four columns",
          style={'background-color':boxcolor, 'border-radius': '5px','box-shadow': '2px 2px 2px lightgrey', 'padding':'1%','marginBottom':'2%'},
          )
        ],
        className='row',
        )
      ],
      className='six columns flex-display'
      )
    ],
    style={'padding':'0'},
    className="row"
    ),
  html.Div([#footer
    html.A("Built by Anthony S N Maina", href='https://www.linkedin.com/in/anthonymaina/', target="_blank", style={'font-size': '1rem',"marginBottom": "0%"})
    ],
    className='row',
    style={ 'text-align':'center'}
    ),
    ], 
    style={'marginLeft':'1%','marginRight':'1%'}),

],
style={'backgroundColor': background, 'margin':0}
)


################################################
#### APP CALLBACKS  ############################
################################################


#Callback for world map
@app.callback(
  Output('world', 'figure'),
  [Input('metric-select', 'value')])
def update_chart(trend):
  if trend == "Total energy consumption":
    metric="lastValue"
    mult=10
    unit="QBtu"
  elif trend=="Energy consumption per capita":
    metric="MBtuPP"
    mult=1
    unit="MBtu per person"
  else:
    metric="TBtuUSD"
    mult=10
    unit="TBtu per USD GDP"


  table=master_cons[master_cons["country"]!="World"]
  df=table[table["label"]=="Total energy consumption"]
  df["text"]= df["country"] +'<br>' + trend + ": " + round(df[metric],2).astype('str') +" " +unit

  d = go.Figure(go.Scattergeo(
      lon=df["long"],
      lat=df["lat"],
      text = df['text'],
      hoverinfo = 'text',
      marker=dict(
          size= mult*df[metric],
          line_width=0.5,
          sizemode='area'
      )))
  fig1=go.Figure(data=d)
  fig1.update_layout(l_map)
  fig1.update_geos(projection_type="natural earth", lataxis_showgrid=False, lonaxis_showgrid=False)
  return fig1

#callback for trend over time
@app.callback(
  Output('country-trend', 'figure'),
  [Input('metric-select1b', 'value')])
def update_chart(country):
  fig2= make_fig_2(country)
  fig2.update_layout(title="Total energy consumption: "+country,yaxis_title= "QBtu")
  return fig2

#callback for fast facts
@app.callback(
  Output('ff_title', 'children'),
  [Input('metric-select1b', 'value')])
def update_text(country):
  return ""

@app.callback(
  Output('li1', 'children'),
  [Input('metric-select1b', 'value')])
def update_text(country):
  if country=="World":
    text="Total energy consumption: {} QBtu".format(int(obj["lastValue"][obj["country"]=="World"].iloc[0]))
  else: 
    text=rank_statement("Total energy consumption", country, "lastValue")
  return text


@app.callback(
  Output('li2', 'children'),
  [Input('metric-select1b', 'value')])
def update_text(country):
  if country=="World":
    text="Energy consumption per capita: {} MBtuPP".format(int(energy_int["lastValue"][energy_int["country"]=="World"].iloc[1]))
  else:
    text=rank_statement("Total energy consumption", country, "MBtuPP")
  return text

@app.callback(
  Output('li4', 'children'),
  [Input('metric-select1b', 'value')])
def update_text(country):
  if country=="World":
    text="Percentage coming from fossil fuels: {} %".format(round(100*(1-(obj["lastValue"][obj["country"]=="World"].iloc[2]/obj["lastValue"][obj["country"]=="World"].iloc[0])),1))
  else:
    text=rank_statement("Nuclear, renewables, and other", country, "dependence")
  return text


#callback for top n abs
@app.callback(
  Output('top-n-abs', 'figure'),
  [Input('metric-select2', 'value')])
def update_chart(metric):
  fig= make_fig_3(master_cons, metric,'lastValue')
  fig.update_layout(xaxis_title= "QBtu")
  return fig

#callback for top n dependence
@app.callback(
  Output('top-n-dependency', 'figure'),
  [Input('metric-select3', 'value')])
def update_chart(metric):
  fig= make_fig_3(master_cons, metric,'dependence')
  fig.update_layout(xaxis_title= "Fraction of total energy use")
  return fig

#callback for top n intensity
@app.callback(
  Output('top-n-intensity', 'figure'),
  [Input('metric-select4', 'value')])
def update_chart(metric):
  if metric=="Energy consumption per GDP":
    fig_x=make_fig_3(master_cons, "Total energy consumption","TBtuUSD")
    uom="TBtuUSD"
  else:
    fig_x=make_fig_3(master_cons, "Total energy consumption","MBtuPP")
    uom="MBtuPP"
  fig_x.update_layout(xaxis_title=uom)
  return fig_x

if __name__ == '__main__':
  app.run_server()