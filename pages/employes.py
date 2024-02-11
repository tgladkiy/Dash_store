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
pd.options.mode.chained_assignment = None


# In[2]:


dash.register_page(__name__, path='/employes', name='employes_page')


# In[3]:


clrs  = { 'basic' : '#2c3e50',
          'green'  : '#18bc9c',
          'blue'  : '#3498db',
          'orange': '#f39c12',
          'grey'  : '#bfc2ca',
          'red'   : '#e74c3c'}


# Вызов и обработка данных 


fake_today_dt = pd.to_datetime('2024-01-30', format='%Y-%m-%d')
fake_today_mth_dt = fake_today_dt.to_period('M')


orders_by_managers = pd.read_csv('orders_by_managers.csv')
orders_by_managers['month_sh']= pd.to_datetime(orders_by_managers['month_sh']).dt.to_period('M')
orders_by_managers['date'] = pd.to_datetime(orders_by_managers['date'])


# ### Дата отчета


datepicker_single = html.Div(
    dcc.DatePickerSingle(
        date=datetime.now(),
#        date=fake_today_dt,
        display_format = 'YYYY-MM-DD',
        className="mb-2",
        id = 'dt_selector')
)


# ### График ЗП и премии


graf_1 = dcc.Graph(
    id = 'id_graf_1',
    #figure = fig_1,
    style={'height': '40vh'}
)


# ### График динамики показателей за 12 мес  (с фильтром по показателю)

graf_3 = dcc.Graph(
    id = 'id_graf_3',
    #figure = fig,
    style={'height': '45vh'}
)


# ### Таблица рабочих дней на неделю


work_list = pd.read_csv('work_list.csv')
work_list = work_list[['manager','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']]
work_list.columns = ['Сотрудник','Пн','Вт','Ср','Чт','Пт','Сб','Вс'] 
work_list = work_list.replace( {0: '-' , 1: '+'})


table_4 = dbc.Table.from_dataframe(work_list, striped=True, bordered=True, hover=True, index=False,
                                                   style = {
                                                       'fontFamily': 'Arial',
                                                       'fontSize': '12px',
                                                       'textAlign': 'center'})


# ### Меню выбора отчета

inline_radioitems = html.Div(
    [
        dbc.RadioItems(
            options=[
                {"label": "Все счета", "value": 1},
                {"label": "Опл. счета", "value": 2},
                {"label": "Средня выручка", "value": 3},
            ],
            value=1,
            id="id_radioitems_input",
            inline=True,
        ),
    ]
)


# ### Слои


layout = [
            dbc.Row(
                [
                    dbc.Col(html.H5('Отчет на дату:'), width=2, align="center"),
                    dbc.Col(datepicker_single, width=10, align="center")
                ],
            ),
                

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6('Отчет по ЗП и премиям'),
                            graf_1,
                        ],
                        width=6
                    ),
                    dbc.Col(
                        [
                            html.H6('Отчет по конверсиям, счетам и пр.'),
                            html.Div(id='id_tab2'),
                        ],
                        width=6
                    ),
                ]),
            
            html.Hr(),
            
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6('Показатели за период 6 мес'),
                            inline_radioitems,
                            graf_3,
                        ],
                        width=6
                    ),
                    dbc.Col(
                        [
                            html.H6('График работы на неделю'),
                            table_4,
                        ],
                        width=6
                    ),
                ]),         
            

             ]

@callback(
    Output("id_graf_1", "figure"),
    Output("id_tab2", "children"),
    Input("dt_selector", "date"))
def update_fig_sales(date_inp):  
    fake_today_dt = pd.to_datetime(date_inp, format='%Y-%m-%d')
    fake_today_mth_dt = pd.Period(fake_today_dt, freq='M')
    
    df_managers_sales = (
        orders_by_managers
        .query('month_sh == @fake_today_mth_dt &  date <= @fake_today_dt')
        .pivot_table(index='manager',
                     values=['id_order','paid','sum', 'salary', 'bonus'], 
                     aggfunc={'id_order':'count','paid':'sum','sum':'sum', 'salary':'max', 'bonus':'max'})
        .reset_index()
    )
    df_managers_sales['bonus_sum'] = df_managers_sales['sum']* df_managers_sales['bonus']/8
    df_managers_sales['prc_eff'] = df_managers_sales['paid'] / df_managers_sales['id_order'] * 100
    df_managers_sales['total_salary'] = df_managers_sales['bonus_sum'] + df_managers_sales['salary']
    df_managers_sales.columns= ['manager', 'bonus', 'all_orders', 'paid_orders', 'salary', 'total_sum', 'bonus_sum','efficiency', 'total_salary']

    sd_salary = df_managers_sales[['manager','salary','bonus_sum','total_salary']]

    fig_1 = go.Figure()
    fig_1.add_trace(go.Bar(
        y=sd_salary['manager'].sort_values(ascending=False),
        x=sd_salary['salary'],
        name='Оклад',
        orientation='h',
        marker=dict(
            color='#3498db',
            line=dict(color='rgba(246, 78, 139, 1.0)', width=0)
        )
    ))
    fig_1.add_trace(go.Bar(
        y=sd_salary['manager'].sort_values(ascending=False),
        x=sd_salary['bonus_sum'],
        name='Бонус',
        orientation='h',
        marker=dict(
            color='#f39c12',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=0)
        )
    ))

    fig_1.update_layout(barmode='stack',
                        plot_bgcolor='white',
                        margin = dict(b=10,
                                     l=10,
                                     pad=10,
                                     r=10,
                                     t=20))   #верхнее поле отступ
     
    
    tab_achievements = df_managers_sales[['manager','all_orders','paid_orders','efficiency','total_sum']]
    tab_achievements['total_sum'] = tab_achievements['total_sum'].round(0)
    tab_achievements['efficiency'] = tab_achievements['efficiency'].round(1)
    tab_achievements.index.name = "№"
    tab_achievements.index = tab_achievements.index + 1
    tab_achievements.columns=['Сотрудник', 'Все заказы', 'Оплаченные','Эффективность', 'Общая сумма']

    table_2 = dbc.Table.from_dataframe(tab_achievements, striped=True, bordered=True, hover=True, index=True,
                                   style = {
                                       'fontFamily': 'Arial',
                                       'fontSize': '12px',
                                       'textAlign': 'center'})
    
    return fig_1, table_2 


@callback(
    Output("id_graf_3", "figure"),
    Input("id_radioitems_input", "value"),
    Input("dt_selector", "date")
    )
def update_fig_dinamics(value_ch, date_inp):  
    day_last = pd.to_datetime(date_inp, format='%Y-%m-%d')
    day_first = day_last  - pd.offsets.MonthEnd(6)

    df_weekly_paid = (
        orders_by_managers
        .query('date >= @day_first  & date < = @day_last')
        .groupby(['manager', pd.Grouper(freq='W', key='date', closed='left')])['paid']
        .sum()
        .unstack(fill_value=0)
        .T
    )
    df_weekly_paid.drop(df_weekly_paid.tail(1).index,inplace=True)

    df_weekly_all_orders = (
        orders_by_managers
        .query('date >= @day_first  & date < = @day_last')
        .groupby(['manager', pd.Grouper(freq='W', key='date', closed='left')])['id_order']
        .count()
        .unstack(fill_value=0)
        .T
    )
    df_weekly_all_orders.drop(df_weekly_all_orders.tail(1).index,inplace=True)


    df_weekly_sum = (
        orders_by_managers
        .query('date >= @day_first  & date < = @day_last')
        .groupby(['manager', pd.Grouper(freq='W', key='date', closed='left')])['sum']
        .mean()
        .unstack(fill_value=0)
        .T
    )
    df_weekly_sum.drop(df_weekly_sum.tail(1).index,inplace=True)


    df_weekly = df_weekly_sum
    
    if value_ch == 1: df_weekly = df_weekly_all_orders
    if value_ch == 2: df_weekly = df_weekly_paid
    if value_ch == 3: df_weekly = df_weekly_sum

        
    fig_3 = px.line(df_weekly.rolling(window=2).mean())
    
    fig_3.update_layout(
                    #title='Обороты за 6 месяцев по направлениям',
                    #title_x = 0,
                    #title_y = 0.914,
                    xaxis_title='',
                    yaxis_title='',
                    legend_orientation="h",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    yaxis_showgrid = True,
                    yaxis_gridwidth = 1,
                    yaxis_gridcolor = clrs['grey'],
                    legend = dict(orientation = "h",
                                x=-0.05,
                                y=-0.15,
                                title="",
                                title_font_family="Sitka Small",
                                bgcolor="white",
                                bordercolor="Black",
                                borderwidth=0),
                    margin = dict(b=10,
                                 l=10,
                                 pad=10,
                                 r=10,
                                 t=20)
    ) 

    
    return fig_3

