#!/usr/bin/env python
# coding: utf-8

# In[52]:


import dash
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 
from flask import Flask
from datetime import datetime
import datetime as dt 
from plotly.subplots import make_subplots

#установим формат вывода данных типа float - 2 знака после заптой (для лучшего восприятия числовых данных)
pd.set_option('display.float_format', '{:.2f}'.format)
#устанавливаем максимальное количество отображаемых колонок
pd.set_option('display.max_rows', 150)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None


# In[53]:


dash.register_page(__name__, path='/marketing', name='marketing_page')


# In[54]:


clrs  = { 'basic' : '#2c3e50',
          'green'  : '#18bc9c',
          'blue'  : '#3498db',
          'orange': '#f39c12',
          'grey'  : '#bfc2ca',
          'red'   : '#e74c3c'}


# Вызов и обработка данных 

# In[55]:


today_dt = pd.to_datetime(datetime.now())
today_mth_dt = today_dt.to_period('M')


# In[56]:


df_statistics = pd.read_csv('df_statistics.csv')
adv_cost = pd.read_csv('adv_cost.csv')
advertising = pd.read_csv('advertising.csv')
orders = pd.read_csv('orders.csv')


# In[57]:


orders['date'] = pd.to_datetime(orders['date'])
df_statistics['date'] = pd.to_datetime(df_statistics['date'])


# ### Дата отчета

# In[59]:


datepicker_single = html.Div(
    dcc.DatePickerSingle(
        date=datetime.now(),
#        date=fake_today_dt,
        display_format = 'YYYY-MM-DD',
        className="mb-2",
        id = 'dt_selector')
)


# ### График конверсий с сайта в продажи

# In[60]:


df_statistics['sum_adv'] = df_statistics['email'] + df_statistics['google'] + df_statistics['vk']+ df_statistics['yandex']
df_statistics['visits_total'] = df_statistics['ya_visits'] + df_statistics['gl_visits'] + df_statistics['vk_visits']+ df_statistics['em_visits']+ df_statistics['or_visits']
df_ads_contacts = df_statistics[['date','sum_adv','visits_total']]
df_orders = (
    orders
    .query('date <= @today_dt')
    .pivot_table(index='date', values=['id_invoice','paid'], aggfunc={'id_invoice': 'count',  'paid' : 'sum'})
    .reset_index()
    .rename(columns={'id_invoice': 'all_invoices', 'paid' : 'paid_orders'})
)
df_all = (
    df_ads_contacts
    .merge(df_orders, left_on='date', right_on='date')
)
df_all['date'] = pd.to_datetime(df_all['date'])


# In[61]:


df_weekly = df_all.groupby(pd.Grouper(freq='W', key='date', closed='left')).mean()

fig = make_subplots(rows=2, cols=1)

fig.append_trace(go.Scatter(
    x=df_weekly.index,
    y=df_weekly['visits_total'],
    line_color=clrs['red'],
    name='Визиты сайта'
), row=1, col=1)

fig.append_trace(go.Scatter(
    x=df_weekly.index,
    y=df_weekly['all_invoices'],
    line_color=clrs['green'],
    name='Заявки'
), row=2, col=1)

fig.append_trace(go.Scatter(
    x=df_weekly.index,
    y=df_weekly['paid_orders'],
    line_color=clrs['blue'],
    name='Заказы'
), row=2, col=1)

 
fig.update_layout(title_text="Динамика визитов на сайт, заявок и заказов",
                  plot_bgcolor='white',
                  yaxis_showgrid = True,
                  yaxis_gridwidth = 1,
                  yaxis_gridcolor = clrs['grey'],
                  yaxis2_showgrid = True,
                  yaxis2_gridwidth = 1,
                  yaxis2_gridcolor = clrs['grey'],
                  legend = dict(orientation = "h",
                        x= 0,
                        y= 1.1,
                        title="",
                        title_font_family="Sitka Small",
                        bgcolor="white",
                        bordercolor="Black",
                        borderwidth=0)
                 )    #height=600, width=600,


# In[62]:


gr_visits_inv_ord = dcc.Graph(
    id = 'id_gr_visits_inv_ord',
    figure = fig,
    #style={'height': '45vh'}
)


# ### Воронка
# 
# 

# In[63]:


df_all['month'] = df_all['date'].dt.to_period('M')


# In[65]:


today_dt = pd.to_datetime('2024-01-30', format='%Y-%m-%d')
today_mth_dt = today_dt.to_period('M')
today_dt_1m = today_dt - pd.offsets.MonthEnd(1)
today_dt_3m = today_dt - pd.offsets.MonthEnd(3)


# In[66]:


funn_1m = dict(
    df_all
    .query('date >= @today_dt_1m  & date <= @today_dt')[['visits_total','all_invoices','paid_orders']]
    .mean()
)

funn_3m = dict(
    df_all
    .query('date >= @today_dt_3m  & date <= @today_dt')[['visits_total','all_invoices','paid_orders']]
    .mean()
)
funn_keys = ['Визиты на сайт','Звонки/Счета','Оплаченые счета']


# In[67]:


list_1m = [round(elem, 0) for elem in list(funn_1m.values()) ]
list_3m = [round(elem, 0) for elem in list(funn_3m.values()) ]


fig_f = go.Figure()

fig_f.add_trace(go.Funnel(
    name = 'Текущий месяц',
    y = ['Визиты сайта','Заявки','Заказы'],
    x = list_1m,
    marker_color=clrs['blue'],
    textposition = "auto",
    textinfo = "value+percent previous",
    textfont_color='black',
    textfont_size = 12 ,


))

fig_f.add_trace(go.Funnel(
    name = 'Текущий квартал',
    y = ['Визиты сайта','Заявки','Заказы'],
    x = list_3m,
    textfont_color='black',
    marker_color=clrs['red'],
    textposition = "auto",
    textfont_size = 14,

    textinfo = "value+percent previous"))

fig_f.update_layout(title_text="Воронка продаж среднесуточная за 1 / 3 мес",
                  plot_bgcolor='white',
                  paper_bgcolor='white',
                  yaxis_showgrid = True,
                  yaxis_gridwidth = 1,
                  legend_orientation="h",
                  yaxis_gridcolor = clrs['grey'], 
                  uniformtext_minsize=9, 
                  uniformtext_mode='show'
                 ) 

fig_f.update_yaxes(showticklabels=True,
                  tickangle=-45)


gr_funnel = dcc.Graph(
    id = 'id_gr_funnel',
    figure = fig_f,
    #style={'height': '45vh'}
)


# ### График расходов по каналам


adv_cost['date'] = pd.to_datetime(adv_cost['date'])
adv_cost['month'] = adv_cost['date'].dt.to_period('M')


df_statistics['date'] = pd.to_datetime(df_statistics['date'])
df_statistics['month'] = df_statistics['date'].dt.to_period('M')
df_visits_month = (
    df_statistics
    .query('date <= @today_dt')
    .groupby(by='month')[['ya_visits', 'gl_visits' , 'vk_visits' , 'em_visits' , 'or_visits']]
    .sum()
    .reset_index()
)
df_visits_month.columns = ['month', 'yandex','google','vk','email','organic']

df_visits_month = (
    pd.melt(df_visits_month, id_vars='month', value_vars=['yandex', 'google', 'vk','email','organic'])
    .rename(columns={'month': 'month' , 'variable':'chanel', 'value':'count'})
)


df_org_temp = adv_cost[['date','month']].drop_duplicates()
df_org_temp['chanel'] = 'organic'
df_org_temp['sum'] = 0
adv_cost = pd.concat([adv_cost, df_org_temp])


df_adv_to_graph = adv_cost.merge(df_visits_month, left_on=['month','chanel'], right_on=['month','chanel'])
df_adv_to_graph['last_day_m'] = df_adv_to_graph['month'].apply(lambda x: x.end_time.date())



@callback(
    Output("id_gr_adv", "figure"),
    Input("id_kanals_filter", "value"))

def update_fig_sales(kanals_radioitems_value):
    if kanals_radioitems_value == "All": 
        x_q =  df_adv_to_graph['last_day_m'].drop_duplicates()
        y_q1 = df_adv_to_graph.groupby(by='date')['count'].sum()
        y_q2 = df_adv_to_graph.groupby(by='date')['sum'].sum()
        
        y1_max = y_q1.max()
        y2_max = y_q2.max()
        
    else: 
        x_q =  df_adv_to_graph.query('chanel ==@kanals_radioitems_value')['last_day_m']
        y_q1 = df_adv_to_graph.query('chanel ==@kanals_radioitems_value')['count']
        y_q2 = df_adv_to_graph.query('chanel ==@kanals_radioitems_value')['sum']
        y1_max = y_q1.max()
        y2_max = y_q2.max()
    
    y1_max = df_adv_to_graph.groupby(by='date')['count'].sum().max()
    y2_max = df_adv_to_graph.groupby(by='date')['sum'].sum().max()
    
    trace1  = go.Scatter(
            mode='lines+markers',
            x = x_q,
            y = y_q1,
            name="Трафик",
            marker_color='crimson',
            marker_line_width=1,
            line=dict(width=7)
        )

    trace2 = go.Bar(
            x = x_q,
            y = y_q2,
            name="Расходы",
            yaxis='y2',
            marker_color ='green',
            marker_line_width=1,
            marker_line_color='rgb(8,48,107)',
            opacity=0.5
        )

    data = [trace1, trace2]

    layout = go.Layout(
        title_text='Расходы по каналам привлечения и количество визитов на сайт',
        plot_bgcolor='white',
        yaxis_showgrid = True,
        yaxis_gridwidth = 1,
        yaxis_gridcolor = clrs['grey'],
        yaxis=dict(
            range = [y1_max * 0, 
                     y1_max * 1.05] ,
            side = 'right'
        ),
        yaxis2=dict(
            range = [y2_max * 0, 
                     y2_max * 1.05] ,
            overlaying='y',
            anchor='y3',
        )
    )
    fig_3 = go.Figure(data=data, layout=layout) #
    #fig_3.show()
    
    return fig_3

    #iplot(fig, filename='multiple-axes-double')
    #**Line_Bar_chart Code**:


# In[74]:


gr_adv = dcc.Graph(
    id = 'id_gr_adv',
    #figure = fig_3,
    #style={'height': '45vh'}
)


# ### Фильтр отчета по каналам
# 
# 

# In[75]:


inline_radioitems = html.Div(
    [
        dbc.RadioItems(
            options=[
                {"label": "Все каналы", "value": 'All'},
                {"label": "Яндекс",     "value": 'yandex'},
                {"label": "Google",     "value": 'google'},
                {"label": "VK",         "value": 'vk'},
                {"label": "E-mail",     "value": 'email'},
                {"label": "Organic",    "value": 'organic'},
            ],
            value= 'All',
            id="id_kanals_filter",      
            inline=True,
        ),
    ]
)


# ### Слои

# In[76]:


layout = [    
            dbc.Row(
                [
                    dbc.Col(gr_visits_inv_ord, width=7),
                    dbc.Col(gr_funnel, width=5)
                ]
            ),
            
            dbc.Row(inline_radioitems, style={'margin-left': '55px'}),
            dbc.Row(
                [
                    gr_adv,
                    
                ],
            ),

             ]

