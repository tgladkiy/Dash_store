import dash
from dash import html, dcc, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

#установим формат вывода данных типа float - 2 знака после заптой (для лучшего восприятия числовых данных)
pd.set_option('display.float_format', '{:.2f}'.format)
#устанавливаем максимальное количество отображаемых колонок
pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)


dash.register_page(__name__, path='/', name='sales_page')


clrs  = { 'basic' : '#2c3e50',
          'green'  : '#18bc9c',
          'blue'  : '#3498db',
          'orange': '#f39c12',
          'grey'  : '#bfc2ca',
          'red'   : '#e74c3c'}


# In[22]:


date_today = datetime.now()
#date_minus_1m = date_today - pd.DateOffset(month=1)
date_minus_30d = date_today - pd.DateOffset(days=30)
date_minus_1y = date_today - pd.DateOffset(days=365)
date_minus_1y_30d = date_minus_1y  - pd.DateOffset(days=30)
date_1day_current_month = date_today.replace(day=1).date()
current_mnth = pd.Period(date_today, freq='M')


str_date = 'НА ДАТУ:  ' + datetime.now().strftime("%d.%m.%Y")
str_txt_2 ='Показатель выполнения плана - с начала месяца'
str_txt_3 ='Остальные показатели - за последние 30 дней в сравнении с аналогичным периодом 2023 г.'

style_1 = {'align' : 'center',
           'font-family': 'Verdana',
           'color': '#07bdd4',
           'font-size': '18px',
           'text-align': 'left',
           'margin': '0px 0'}

style_2 = {'align' : 'center',
           'font-family': 'Verdana',
           'color': '#07bdd4',
           'font-size': '13px',
           'text-align': 'left',
           'margin': '0px 0'}
style_3 = {'align' : 'center',
           'font-family': 'Verdana',
           'color': '#07bdd4',
           'font-size': '13px',
           'text-align': 'left',
           'margin': '10px 0'}

cards_date = dbc.Card(
        [
            #dbc.CardHeader("План продаж"),
            dbc.CardBody(
                [
                    html.H3('ОЧЁТ ПО ТЕКУЩИМ ПОКАЗАТЕЛЯМ', style=style_1),
                    html.H3(str_date, style=style_1),
                    html.Br(),
                    html.H3(str_txt_2, style=style_2),
                    html.H3(str_txt_3, style=style_3),

                ],  style={'font-family': 'Lato'}, 
            ), 
        ], outline=True, style={"border" : "0"},

    )


# ### Вызов и обработка данных 

# In[24]:


adv_cost = pd.read_csv('adv_cost.csv')
plan = pd.read_csv('plan.csv')
plan['month'] = pd.to_datetime(plan['month']).dt.to_period('M')


sales = pd.read_csv('sales2023_2024.csv')
sales['month_tr'] = pd.to_datetime(sales['month_tr']).dt.to_period('M')
df_current_month23 = sales.query('year == 2023')
df_current_month24 = sales.query('year == 2024 & month_tr <= @current_mnth')

sales_by_brands = pd.read_csv('sales_by_brands.csv')
sales_by_brands['sum_orders'] = sales_by_brands['sum'] * sales_by_brands['paid']
sales_by_brands['date'] = pd.to_datetime(sales_by_brands['date'])


df_sbb = (
    sales_by_brands
    .pivot_table(index=['date','class_name'], 
                 values=['id_invoice','paid','sum_orders'], 
                 aggfunc={'id_invoice' : 'count', 'paid' : 'sum', 'sum_orders' : 'sum'})
    .reset_index()
    .rename(columns={'id_invoice' : 'invoses', 'paid' : 'orders', 'sum_orders' : 'sum'})
)


# ### Сравнение объемов с счетов по месяцам года


df_sbb_2023 = (
    df_sbb
    .query('date > @date_minus_1y_30d & date <= @date_minus_1y')
    .pivot_table(index = 'class_name', values=['invoses', 'orders', 'sum'], aggfunc = {'invoses': 'sum', 
                                                                                       'orders' : 'sum', 
                                                                                       'sum': 'sum'})
    .reset_index()
)

df_sbb_2024 = (
    df_sbb
    .query('date > @date_minus_30d & date <= @date_today')
    .pivot_table(index = 'class_name', values=['invoses', 'orders', 'sum'], aggfunc = {'invoses': 'sum', 
                                                                                       'orders' : 'sum', 
                                                                                       'sum': 'sum'})
    .reset_index()
)

fig_1_t1  = go.Bar(

        x = df_sbb_2024['class_name'],
        y = df_sbb_2024['sum'],
        text= df_sbb_2024['sum'],
        name="2024",
        marker_color=clrs['blue'],
        marker_line_width=1,

    )

fig_1_t2 = go.Bar(
        x = df_sbb_2024['class_name'],
        y = df_sbb_2023['sum'],
        text= df_sbb_2023['sum'],
        name="2023",
        marker_color =clrs['grey'],
        marker_line_width=0,
        marker_line_color='rgb(8,48,107)',
#         opacity=0.5
    )

fig_1_data = [fig_1_t1, fig_1_t2]

fig_1_layout = go.Layout(
    title_text='Объёмы продаж за последние 30 дней 2024 / 2023 год',
    legend_orientation="h",
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin = dict(b=10,
                  l=30,
                  pad=10,
                  r=30,
                  t=50)
)

fig_1 = go.Figure(data=fig_1_data, layout=fig_1_layout) #
fig_1.update_traces(texttemplate='%{text:.3s}', textposition='outside')
fig_1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')


fig_2_t1  = go.Bar(

        x = df_sbb_2024['class_name'],
        y = df_sbb_2024['orders'],
        text= df_sbb_2024['orders'],
        name="2024",
        marker_color=clrs['orange'],
        marker_line_width=1,

    )

fig_2_t2 = go.Bar(
        x = df_sbb_2024['class_name'],
        y = df_sbb_2023['orders'],
        text= df_sbb_2023['orders'],
        name="2023",
        marker_color =clrs['grey'],
        marker_line_width=0,
        marker_line_color='rgb(8,48,107)',
    )

fig_2_data = [fig_2_t1, fig_2_t2]

fig_2_layout = go.Layout(
    title_text='Заказы за последние 30 дней 2024 / 2023 год',
    legend_orientation="h",
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin = dict(b=10,
                  l=10,
                  pad=10,
                  r=30,
                  t=50)
)

fig_2 = go.Figure(data=fig_2_data, layout=fig_2_layout) #
fig_2.update_traces(texttemplate='%{text:.3s}', textposition='outside')
fig_2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')



gr_fig_1 = dcc.Graph(
    id = 'id_gr_fig_1',
    figure = fig_1,
    ####  сюда возвращает функция callback
    
    style={'height': '55vh'})

gr_fig_2 = dcc.Graph(
    id = 'id_gr_fig_2',
    figure = fig_2,
    ####  сюда возвращает функция callback
    
    style={'height': '55vh'})



today_month = pd.Period(date_today.now().strftime('%Y-%m'), freq='M')
last_year_month = today_month - pd.offsets.MonthEnd(12)

adv_cost['date'] = pd.to_datetime(adv_cost['date'])
adv_cost['month'] = adv_cost['date'].dt.to_period('M')

adv_cost_2023 = adv_cost.query('month == @last_year_month')
adv_cost_2024 = adv_cost.query('month == @today_month')



fig_4_t1  = go.Bar(
        x = adv_cost_2023['sum'],
        y = adv_cost_2023['chanel'],
        text= adv_cost_2023['sum'],
        name="2023",
        orientation='h',
        marker_color = clrs['blue'],
    )

fig_4_t2 = go.Bar(
        x = adv_cost_2024['sum'],
        y = adv_cost_2024['chanel'],
        text= adv_cost_2024['sum'],
        name="2024", 
        orientation='h',
        marker_color= clrs['orange'],
        marker_line_width=1,
    )

fig_4_data = [fig_4_t1, fig_4_t2]


str_text = 'Реклама на ' + pd.to_datetime(date_today).month_name(locale='Russian').lower() + ' 2024/23 г.'

fig_4_layout = go.Layout(
    title_text=str_text,
    legend_orientation="h",
    plot_bgcolor='white',
    margin = dict(b=10,
                  l=10,
                  pad=10,
                  r=30,
                  t=50),
    xaxis=dict(
        range = [0, 
                 max(adv_cost_2024['sum'].max(),adv_cost_2023['sum'].max()) * 1.15] ,
        side = 'right'
        ),
)

fig_4 = go.Figure(data=fig_4_data, layout=fig_4_layout) #
fig_4.update_traces(texttemplate='%{text:.3s}', textposition='outside')
fig_4.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')


gr_fig_4 = dcc.Graph(
    id = 'id_gr_fig_4',
    figure = fig_4,
    ####  сюда возвращает функция callback
    
    style={'height': '55vh'})


# ### График и фильтр


sales_gr = dcc.Graph(
    id = 'sales_gr',   
    ####  сюда возвращает функция callback
    style={'height': '55vh'})


monthly_sales_radioitems = html.Div(
    [
        dbc.RadioItems(
            options=[
            {'label' : 'Выручка', 'value' : 'sum_paid'},
            {'label' : 'Сумма счетов', 'value' : 'sum_all_inv'},                             
            {'label' : 'Счета (оплачено)', 'value' : 'paid_invoces'},
            {'label' : 'Счета (выставлено)', 'value' : 'all_invoces'}
            ],
            value='sum_paid',
            id="sales_radioitems_input",
            inline=True
        ),
    ]
)


# ### Фильтр даты

# ### Карточки выполнения плана продаж


ads_sum_23 = int(adv_cost.query('month == @last_year_month')['sum'].sum())
ads_sum_24 = int(adv_cost.query('month == @today_month')['sum'].sum())
ads_sum_24_23 = int(round(ads_sum_24 / ads_sum_23 * 100, 0))

sales_ty = sales_by_brands.query('date > = @date_minus_30d & date <= @date_today')
sales_ly = sales_by_brands.query('date > = @date_minus_1y_30d & date <= @date_minus_1y')

bills_ty = int(sales_ty['id_order'].drop_duplicates().count())
bills_ly = int(sales_ly['id_order'].drop_duplicates().count())
bills_ty_ly = int(round(bills_ty / bills_ly * 100, 0))

sum_ty = int(sales_ty['sum_orders'].sum())
sum_ly = int(sales_ly['sum_orders'].sum())
sum_ty_ly = int(round(sum_ty / sum_ly  * 100, 0))

sum_cur_month = sales_by_brands.query('date > = @date_1day_current_month & date <= @date_today')['sum_orders'].sum()
sum_mth_plan = int(plan.query('month == @today_month')['plan'])
sum_mth_ty_plan = int(round(sum_cur_month / sum_mth_plan * 100, 0))

sum_cur_month = round(sum_cur_month/1000000, 1)
sum_mth_plan = round(sum_mth_plan/1000000, 1)

sum_ty = round(sum_ty/1000000, 1)
sum_ly = round(sum_ly/1000000, 1)

ads_sum_23 = round(ads_sum_23/1000, 1)
ads_sum_24 = round(ads_sum_24/1000, 1)


#  

def cards(val_prc, str_line, val_f, val_p, str_line_2, str_line_3):
    colors = {'red' : '#ff6262',
          'green' : '#6ac65e'}

    str_line_2 = str_line_2.upper()
    str_line = str_line.upper()

    if val_prc < 99 : 
        clr = colors['red']
    else: clr = colors['green']    
    str_prc = str(val_prc)+' %'
    str_f_p = str(val_f) + ' ' + str(val_p)

    cards_1 = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H3(str_prc, style={'align' : 'center',
                                          'font-family': 'Lato',
                                          'color': clr,
                                          'font-size': '28px',
                                          'text-align': 'center',
                                          'margin': '0px 0'}),
                    html.Hr(style={'margin': '0px 0',
                                   'height':'5px' , 
                                   'border-width' : '0', 
                                   'background-color':'#bfbfbf'}),
                    html.H4(str_line, style={'vertical-align': 'super',
                                                      'font-family': 'Verdana',
                                                       'font-size': '12px',
                                                       'text-align': 'center',
                                                       'word-spacing': '5px',
                                                       'font-weight': '800',
                                                       'color': '#07bdd4'}),
                    html.H4(str_f_p, style={'align' : 'center',
                                          'font-family': 'Lato',
                                          'color': '#333d5e',
                                          'font-size': '15px',
                                          'word-spacing': '55px',
                                          'font-weight': '800',
                                          'text-align': 'center',
                                          'margin': '0px 0'}),

                    html.H4(str_line_2, style={'vertical-align': 'super',
                                                      'font-family': 'Verdana',
                                                       'font-size': '10px',
                                                       'text-align': 'center',
                                                       'word-spacing': '48px',
                                                       'font-weight': '800',
                                                       'color': '#07bdd4'}),
                    html.H4(str_line_3, style={'vertical-align': 'super',
                                                      'font-family': 'Verdana',
                                                       'font-size': '10px',
                                                       'text-align': 'center',
                                                       #'word-spacing': '48px',
                                                       'font-weight': '800',
                                                       'color': '#07bdd4'}),

                ],  style={'font-family': 'Lato'}, 
            ), 
        ], outline=True, style={"border" : "0"},

    )
    return cards_1


# ### Слои



layout =   [
            dbc.Row(
                [
                    dbc.Col(cards_date, width=4),
                    dbc.Col(cards(sum_mth_ty_plan, 'ПЛАН ПО ВЫРУЧКЕ', sum_cur_month, sum_mth_plan, 'факт план', 'млн. руб.'), width={"size": 2}),
                    dbc.Col(cards(sum_ty_ly, 'выручка 2024/23', sum_ty, sum_ly, '2024 2023', 'млн. руб.'), width=2),
                    dbc.Col(cards(bills_ty_ly, 'счета 2024/23', bills_ty, bills_ly, '2024 2023', 'счетов'), width=2),
                    dbc.Col(cards(ads_sum_24_23, 'реклама 2024/23', ads_sum_24, ads_sum_23, '2024 2023', 'тыс. руб.' ), width=2),
                ]),
            dbc.Row(
                [
                    dbc.Col(gr_fig_1, width=6),
                    dbc.Col(gr_fig_2, width=6),                    
                ], #style={'margin' : '0', 'margin-top' : '0', 'padding' : '0', 'padding-top' : '0'}
            ),
            dbc.Row(monthly_sales_radioitems, style={'margin-left': '40px'}),
            dbc.Row(
                [
                    dbc.Col(sales_gr , width=8),
                    dbc.Col(gr_fig_4, width=4),   
                ]),

            
             ]

@callback(
    Output("sales_gr", "figure"),
    [Input("sales_radioitems_input", "value"),])

def update_fig_sales(sales_radioitems_value):
    
    if sales_radioitems_value == 'sum_paid':
        y1 = round(df_current_month23['sum_paid']/1000000,0)
        y2 = round(df_current_month24['sum_paid']/1000000,0)
        tit = 'Сравнение объемов оплаченных счетов помесячно за 2024 / 2023 г.'
        yax = {'title' : 'Оплаченные счета в млн. руб.'}
    if sales_radioitems_value == 'sum_all_inv':
        y1 = round(df_current_month23['sum_all_inv']/1000000,0)
        y2 = round(df_current_month24['sum_all_inv']/1000000,0)
        tit = 'Сравнение объемов выставленный счетов помесячно за 2024 / 2023 г.'
        yax = {'title' : 'Выставленные счета в млн. руб.'}    
    if sales_radioitems_value == 'paid_invoces':
        y1 = df_current_month23['paid_invoces']
        y2 = df_current_month24['paid_invoces']
        tit = 'Сравнение количества оплаченных счетов помесячно за 2024 / 2023 г.'
        yax = {'title' : 'Количество счетов'}        
    
    if sales_radioitems_value == 'all_invoces':
        y1 = df_current_month23['all_invoces']
        y2 = df_current_month24['all_invoces']
        tit = 'Сравнение количества выставленных счетов помесячно за 2024 / 2023 г.'
        yax = {'title' : 'Количество счетов'}     
    
    
    fig_1d = go.Scatter(
        x = df_current_month23['month_name'],
        y = y1,
        name="2023",
        marker_color=clrs['blue'],
        marker_line_width=3)

    fig_2d = go.Scatter(
        x = df_current_month24['month_name'],
        y = y2,
        name="2024",
        marker_color=clrs['orange'],
        marker_line_width=1)

    fig_1_data = [fig_1d, fig_2d]

    fig_1_layout = go.Layout(
        title_text=tit,
        xaxis = {'title' : ''},
        yaxis = yax,
        yaxis_showgrid = True,
        yaxis_gridwidth = 1,
        yaxis_gridcolor = clrs['grey'],
#         xaxis_showgrid=False,
        #xaxis={'showgrid': True},
        legend_orientation="h",
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin = dict(b=10,
                  l=50,
                  pad=10,
                  r=10,
                  t=50)
    )

    fig = go.Figure(data=fig_1_data, layout=fig_1_layout) #

    
    return fig




