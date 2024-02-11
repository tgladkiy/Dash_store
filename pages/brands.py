import dash
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 
from datetime import datetime


#установим формат вывода данных типа float - 2 знака после заптой (для лучшего восприятия числовых данных)
pd.set_option('display.float_format', '{:.2f}'.format)
#устанавливаем максимальное количество отображаемых колонок
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)


dash.register_page(__name__, path='/brands', name='brands_page')


clrs  = { 'basic' : '#2c3e50',
          'green'  : '#18bc9c',
          'blue'  : '#3498db',
          'orange': '#f39c12',
          'grey'  : '#bfc2ca',
          'red'   : '#e74c3c',
          'dark_grey': '#7b8a8b'}


sales_by_brand = pd.read_csv('sales_by_brands.csv')
sales_by_brand['year_month'] = pd.to_datetime(sales_by_brand['year_month']).dt.to_period('M')
plans_all = pd.read_csv('plans2023_2024.csv')
plans_all['year_month'] = pd.to_datetime(plans_all['year_month']).dt.to_period('M')



df_plans_classes = (
    plans_all
    .pivot_table(index='year_month', values='sum', columns='class_name', aggfunc='sum')
    .reset_index()
    .rename(columns = {'year_month':'plan_2024_month'})
)

df_plans_brand = (
    plans_all
    .pivot_table(index='year_month', values='sum', columns='brand', aggfunc='sum')
    .reset_index()
    .rename(columns = {'year_month':'plan_2024_month'})
)


# ### График 1 (факт/план на текущий месяц)

now_month = datetime.now().strftime('%Y-%m')
now_month = pd.Period(now_month, freq='M')

df1 = (
    df_plans_classes
    .query('plan_2024_month == @now_month')
    .drop('plan_2024_month', axis=1)
    .T
    .reset_index()
)
df1.columns=['class_name','sum']
x_plan = list(df1['class_name'])
y_plan = list(df1['sum'])

df2 = sales_by_brand.query('year_month ==@now_month').groupby('class_name').sum()['sum'].reset_index()
x_fact = list(df2['class_name'])
y_fact = list(df2['sum'])


# In[7]:


fig_1_t1  = go.Bar(

        x = x_plan,
        y = y_fact,
        text= y_fact,
        name="Факт",
        marker_color=clrs['orange'],
        marker_line_width=1,

    )

fig_1_t2 = go.Bar(
        x = x_plan,
        y = y_plan,
        text= y_plan,
        name="План",
        marker_color =clrs['grey'],
        marker_line_width=0,
        marker_line_color='rgb(8,48,107)',
#         opacity=0.5
    )

fig_1_data = [fig_1_t1, fig_1_t2]

fig_1_layout = go.Layout(
    title_text='Выручка по направлениям за текущий месяц',
    legend_orientation="h",
    plot_bgcolor='white',
    paper_bgcolor='white'
)

fig_1 = go.Figure(data=fig_1_data, layout=fig_1_layout) #
fig_1.update_traces(texttemplate='%{text:.3s}', textposition='outside')
fig_1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

gr_classes_this_month = dcc.Graph(
    id = 'id_gr_classes_this_month',
    figure = fig_1,
#    style={'height': '50vh'}
)


# ### График 2 (выручка по направлениям на 6 мес)
#

now_month_minus_6 = now_month - pd.offsets.MonthEnd(6)


df_graph_2 = (
    sales_by_brand[['year_month','class_name','sum']]
    .query('year_month > @now_month_minus_6 & year_month < = @now_month')
    .groupby(by=['year_month','class_name'])
    .sum().reset_index()
)

fig_2 = px.line(df_graph_2, x=df_graph_2["year_month"].astype(str), y="sum",
                color='class_name', markers='*',
                color_discrete_map={"Керамика": clrs['blue'], 
                                        "Обои": clrs['red'], 
                                        "Краска": clrs['orange'], 
                                        "Ламинат": clrs['basic'], 
                                        "Шпаклевка": clrs['green']},)
fig_2.update_layout(title='Обороты за 6 месяцев по направлениям',
                    title_x = 0,
                    title_y = 0.914,
                    xaxis_title='',
                    yaxis_title='Выручка',
                    legend_orientation="h",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    yaxis_showgrid = True,
                    yaxis_gridwidth = 1,
                    yaxis_gridcolor = clrs['grey'],
                    legend = dict(orientation = "h",
                                x=-0.05,
                                y=-0.05,
                                title="",
                                title_font_family="Sitka Small",
                                bgcolor="white",
                                bordercolor="Black",
                                borderwidth=0)
                   )


gr_classes_6_months = dcc.Graph(
    id = 'id_gr_classes_6_months',
    figure = fig_2,
#    style={'height': '50vh'}
)


# ### Фильтр по направлениям 

radioitems = html.Div(
    [
        dbc.Label("Выбор направления"),
        dbc.RadioItems(
            options=[
                {"label": "Все направления", "value": "All"},                
                {"label": "Керамика", "value": "Керамика"},
                {"label": "Краска", "value": "Краска"},
                {"label": "Ламинат", "value": "Ламинат"},
                {"label": "Обои", "value": "Обои"},
                {"label": "Шпаклевка", "value": "Шпаклевка"}
                 ],
            value='All',
            id="id_radioitems_input",
        ),
    ]
)


radioitems_months = html.Div(
    [
        dbc.Label("Период"),
        dbc.RadioItems(
            options=[
                {"label": "текущий месяц", "value": 1},                
                {"label": "3 месяца", "value": 3},
#                {"label": "6 месяцев", "value": 6}
                 ],
            value= 1 ,
            id="id_radioitems_months_input",
        ),
    ]
)


# ### График 3 (выполнение плана по брендам внутри направления)

gr_classes_brands = dcc.Graph(
    id = 'id_gr_classes_brands',
    style={'height': '55vh'}
)


layout = [
            dbc.Row(
                [
                    dbc.Col(gr_classes_this_month, width=6),
                    dbc.Col(gr_classes_6_months, width=6),

                ]),
            
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col([radioitems,
                             html.Hr(),
                             radioitems_months
                            ], width=2),
                    dbc.Col(gr_classes_brands, width=10),

                ]),            

            
             ]
      
@callback(
    [Output("id_gr_classes_brands", "figure")],
    [Input("id_radioitems_input", "value"),
     Input("id_radioitems_months_input", "value"),]
)

def update_fig_sales(radioitems_input_value, radioitems_months_value):  
    classes_ch = radioitems_input_value
    month_ch = radioitems_months_value

    q_month = now_month - pd.offsets.MonthEnd(month_ch)

    if classes_ch in list(sales_by_brand['class_name'].unique()):
        qer = ' year_month > @q_month & year_month <= @now_month & class_name == @classes_ch '
    else: 
        qer = ' year_month > @q_month & year_month <= @now_month'

    df_fact = (
        sales_by_brand
        .query(qer)
        .pivot_table(index='brand', values='sum', aggfunc='sum')
        .reset_index()
    )

    xb_fact = df_fact['brand']
    yb_fact = df_fact['sum']

    df_plan = (
        plans_all
        .query(qer)
        .pivot_table(index='brand', values='sum', aggfunc='sum')
        .reset_index())

    xb_plan = df_plan['brand']
    yb_plan = df_plan['sum']

    str_title =  'Фактические и плановые показатели выручки по брендам направления: ' + str(radioitems_input_value)

    figure_out = {
    'data': [
        go.Bar(name='Факт ', x=xb_fact, y=yb_fact, marker_color=clrs['blue']),
        go.Bar(name='План', x=xb_fact, y=yb_plan, marker_color=clrs['orange']),
            ],
    'layout' : go.Layout(
         title = str_title,
         title_x = 0.05,
         margin = dict(b=90,
                       l=10,
                       pad=10,
                       r=30,
                       t=30))                         
            }, 
    
    
    return figure_out

