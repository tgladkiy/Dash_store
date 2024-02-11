import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask
import pandas as pd
from datetime import datetime


#установим формат вывода данных типа float - 2 знака после заптой (для лучшего восприятия числовых данных)
pd.set_option('display.float_format', '{:.2f}'.format)
#устанавливаем максимальное количество отображаемых колонок
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)


server = Flask(__name__)
app = dash.Dash(__name__, pages_folder='pages', use_pages=True, server = server, external_stylesheets=[dbc.themes.FLATLY])


clrs  = { 'basic' : '#2c3e50',
          'green'  : '#18bc9c',
          'blue'  : '#3498db',
          'orange': '#f39c12',
          'grey'  : '#bfc2ca',
          'red'   : '#e74c3c'}

date_today = datetime.now()


navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("План продаж", href="/"),        #header=True
                dbc.DropdownMenuItem("Направления", href="/brands"),
                dbc.DropdownMenuItem("Сотрудники", href="/employes"),
                dbc.DropdownMenuItem("Маркетинг", href="/marketing"),
            ],
            nav=True,
            in_navbar=True,
            label="Разделы отчета",
        ),
        
        dbc.NavItem(dbc.NavLink(datetime.now().strftime("%d %B %Y"), href="/")),       
        
    ],
    brand="Dashboard  «База отделочных материалов»",
    brand_href="/",
    color="primary",
    dark=True,
)

app.layout = html.Div( 
    [
        dbc.Container([            
            dbc.Row(navbar),

            dash.page_container            
             ],           
        style={"background-color": "white", 'color':'black'}
        )
    ],
    style={ "background-color": "#E6E6E6", 'color':'black'})


if __name__ == '__main__':
   app.run_server(port = 4030, debug=True)