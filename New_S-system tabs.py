import pandas as pd
import dash
from dash import dcc
from dash import html
from dash import dash_table as dt
from dash.dependencies import Input, Output, State
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
import dash_bootstrap_components as dbc
import subprocess
from subprocess import call
import datetime
#import base64
from datetime import date
import plotly.graph_objs as go
import plotly.express as px


import warnings # to remove warnings while displaying result.
warnings.filterwarnings(action='ignore')

connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=172.16.1.181;Database=New_Ssystem;UID=sa3;PWD=rauto;)'
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
engine = create_engine(connection_url)

sql1=f"SELECT * FROM PE_spread_qtysheet"
sql2=f"SELECT * FROM PE_spread_expiry"
day=datetime.datetime.now().date()
year = datetime.datetime.now().year
month = datetime.datetime.now().month
da = datetime.datetime.now().day

# For plot tab

min_day = pd.read_sql(sql=f"select top(1) CandleDateTime FROM PE_spread_plot order by CandleDateTime asc", con= engine)
min_day = min_day['CandleDateTime'][0]
max_day = pd.read_sql(sql=f"select top(1) CandleDateTime FROM PE_spread_plot order by CandleDateTime desc", con= engine)
max_day = max_day['CandleDateTime'][0]

temp_NF = pd.read_sql(sql=f"SELECT top(100) * FROM PE_spread_plot order by CandleDateTime desc", con=engine)
temp_NF = temp_NF.iloc[::-1]
temp_NF = temp_NF.reset_index(drop=True)

fig = px.line(temp_NF,x='CandleDateTime',y='Strike',color='Stage',markers=True)
fig.update_xaxes(ticks= "outside",
                 ticklabelmode= "period",
                 tickcolor= "black",
                 ticklen=7)

app = dash.Dash()
application = app.server
server = app.server
app.title = 'S_system tabs'

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("PE_Spread Execution Tab", style={"text-align": "center",'font-weight': 'bold'})),

            html.Label(id='Total_table', style={'font-weight': 'bold'}),

            html.Div(id="table4", style={'margin-top': 10, 'margin-bottom': 20, 'text-align':'left'}),

            html.Center([dbc.Button(id='submit-button_qtysheet', children='Download',
                                    style={'width': '200px', 'margin-top': 30, 'margin-bottom': 30})]),

            dcc.Download(id="download-dataframe-qtysheet-csv"),

            html.Center(html.Div(id="display_qtysheet", style={'font-weight': 'bold', 'color': 'red'})),

            html.Label(id='Expiry_table',style={'font-weight': 'bold'}),

            html.Div(id="table2", style={'margin-top': 10, 'margin-bottom': 20}),

            html.Label("Client :", style={'font-weight': 'bold'}),

            dcc.Dropdown(id='stock_dropdown', placeholder='Select the client',
                         style={'width': '800px', 'margin-left': 100, 'margin-bottom': 20, 'margin-top': 20}),

            html.Label(id='qty_sheet',style={'font-weight': 'bold'}),

            html.Div(id="table1", style={'margin-top': 10}),

            dcc.Interval(id='interval-component', interval=60 * 1000, n_intervals=0)
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("PE_Spread Debug", style={"text-align": "center",'font-weight': 'bold'})),

            dash.html.Center(dcc.Dropdown(id='dt_dropdown', placeholder='Select the CandleDateTime',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            dash.html.Center(dcc.Dropdown(id='stocks_dropdown', placeholder='Select the stock',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            dash.html.Center(dcc.Dropdown(id='client_dropdown', placeholder='Select the client',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            html.Div([dash.html.Center(dbc.Button(id='submit-button2_1', children='Display the total_Dir_qtysheet',
                                 style={'width': '200px', 'margin-top': 20}))]),

            html.Div(id="table2_1", style={'margin-top': 10}),

            html.Div(id="table2_2", style={'margin-top': 10}),

            dash.html.Center(dcc.Dropdown(['CE', 'PE'], id='CE/PE_dropdown', placeholder='Select PE/CE',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            dcc.Interval(id='interval-component', interval=60 * 1000, n_intervals=0),

            html.Label("Strike_wise distribution :",style={'font-weight': 'bold','margin-bottom': 20}),

            dt.DataTable(id="table2_3",style_table={'margin-top': 20})
        ]
    ),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.H2('DAILY ATMS of PE_Spread system', style={"text-align": "center",'font-weight': 'bold'}),

            dash.html.Center(dcc.DatePickerRange(id='my-date-picker-range', min_date_allowed=min_day, max_date_allowed=max_day,
                                initial_visible_month=date(year, month, da),style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20})),

            html.H4('NIFTY ATM Plot', style={"text-align": "center", 'margin-top': 50}),

            dcc.Graph(id='plot', figure=fig),
        ]
    ),
    className="mt-3",
)

tab4_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("PE_Spread Whole Sheet", style={"text-align": "center"})),

            html.Label("PE_Spread Whole Sheet : ", style={'font-weight': 'bold', 'margin-bottom': 20}),

            dash.html.Center(dcc.Dropdown(['All','D1_T1','D1_T2','D1_T3','D2_T1','D2_T2','D2_T3','D3_T1','D3_T2','D3_T3'],id='stage_dropdown', placeholder='Select the Stage to display',
                                          style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20,
                                                 'text-align': 'Left'})),

            html.Div(id="table_whole", style={'margin-top': 10}),

            dcc.Interval(id='interval', interval=60 * 1000, n_intervals=0),
        ]
    ),
    className="mt-3",
)

tab5_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("PE_Spread Current Sheet", style={"text-align": "center"})),

            html.Label("PE_Spread Current Sheet : ", style={'font-weight': 'bold', 'margin-bottom': 20}),

            dash.html.Center(
                dcc.Dropdown(['All', 'D1_T1', 'D1_T2', 'D1_T3', 'D2_T1', 'D2_T2', 'D2_T3', 'D3_T1', 'D3_T2', 'D3_T3'],
                             id='stages_dropdown', placeholder='Select the Stage to display',
                             style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20,
                                    'text-align': 'Left'})),

            html.Div(id="table_current", style={'margin-top': 10}),
            html.Center([dbc.Button(id='submit-button_2', children='Download',
                                    style={'width': '200px', 'margin-top': 30, 'margin-bottom': 30})]),
            dcc.Download(id="download-dataframe-2-csv"),
            html.Center(html.Div(id="display2", style={'font-weight': 'bold', 'color': 'red'})),
            dcc.Interval(id='intervals', interval=60 * 1000, n_intervals=0),
        ]
    ),
    className="mt-3",
)

tab6_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("Flagship Execution Tab", style={"text-align": "center",'font-weight': 'bold'})),

            html.Label(id='Total_table_flag', style={'font-weight': 'bold'}),

            html.Div(id="table4_flag", style={'margin-top': 10, 'margin-bottom': 20, 'text-align':'left'}),

            html.Center([dbc.Button(id='submit-button_qtysheet_flag', children='Download',
                                    style={'width': '200px', 'margin-top': 30, 'margin-bottom': 30})]),

            dcc.Download(id="download-dataframe-qtysheet-csv_flag"),

            html.Center(html.Div(id="display_qtysheet_flag", style={'font-weight': 'bold', 'color': 'red'})),


            html.Label(id='Expiry_table_flag',style={'font-weight': 'bold'}),

            html.Div(id="table2_flag", style={'margin-top': 10, 'margin-bottom': 20}),

            html.Label("Client :", style={'font-weight': 'bold'}),

            dcc.Dropdown(id='stock_dropdown_flag', placeholder='Select the client',
                         style={'width': '800px', 'margin-left': 100, 'margin-bottom': 20, 'margin-top': 20}),

            html.Label(id='qty_sheet_flag',style={'font-weight': 'bold'}),

            html.Div(id="table1_flag", style={'margin-top': 10}),

            dcc.Interval(id='interval-component_flag', interval=60 * 1000, n_intervals=0)
        ]
    ),
    className="mt-3",
)

tab7_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("Flagship Debug", style={"text-align": "center",'font-weight': 'bold'})),

            dash.html.Center(dcc.Dropdown(id='dt_dropdown_FD', placeholder='Select the CandleDateTime',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            dash.html.Center(dcc.Dropdown(id='stocks_dropdown_FD', placeholder='Select the stock',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            dash.html.Center(dcc.Dropdown(id='client_dropdown_FD', placeholder='Select the client',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            html.Div([dash.html.Center(dbc.Button(id='submit-button2_1_FD', children='Display the total_Dir_qtysheet',
                                 style={'width': '200px', 'margin-top': 20}))]),

            html.Div(id="table2_1_FD", style={'margin-top': 10}),

            html.Div(id="table2_2_FD", style={'margin-top': 10}),

            dash.html.Center(dcc.Dropdown(['CE', 'PE'], id='CE/PE_dropdown_FD', placeholder='Select PE/CE',
                         style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20, 'text-align':'Left'})),

            dcc.Interval(id='interval-component_FD', interval=60 * 1000, n_intervals=0),

            html.Label("Strike_wise distribution :",style={'font-weight': 'bold','margin-bottom': 20}),

            dt.DataTable(id="table2_3_FD",style_table={'margin-top': 20})
        ]
    ),
    className="mt-3",
)

tab8_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("Flagship Whole Sheet", style={"text-align": "center"})),

            html.Label("Flagship Whole Sheet : ", style={'font-weight': 'bold', 'margin-bottom': 20}),

            dash.html.Center(dcc.Dropdown(['All','D1_T1','D1_T2','D1_T3'],id='stage_dropdown_flag', placeholder='Select the Stage to display',
                                          style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20,
                                                 'text-align': 'Left'})),

            html.Div(id="table_whole_flag", style={'margin-top': 10}),

            dcc.Interval(id='interval_flag', interval=60 * 1000, n_intervals=0),
        ]
    ),
    className="mt-3",
)

tab9_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(html.H2("Flagship Current Sheet", style={"text-align": "center"})),

            html.Label("Flagship Current Sheet : ", style={'font-weight': 'bold', 'margin-bottom': 20}),

            dash.html.Center(
                dcc.Dropdown(['All', 'D1_T1', 'D1_T2', 'D1_T3'],
                             id='stages_dropdown_flag', placeholder='Select the Stage to display',
                             style={'width': '800px', 'margin-bottom': 20, 'margin-top': 20,
                                    'text-align': 'Left'})),

            html.Div(id="table_current_flag", style={'margin-top': 10}),
            html.Center([dbc.Button(id='submit-button', children='Download',
                                    style={'width': '200px', 'margin-top': 30, 'margin-bottom': 30})]),
            dcc.Download(id="download-dataframe-csv"),
            html.Center(html.Div(id="display", style={'font-weight': 'bold', 'color': 'red'})),
            dcc.Interval(id='intervals_flag', interval=60 * 1000, n_intervals=0),
        ]
    ),
    className="mt-3",
)

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'fontWeight': 'bold'
}

tab_selected_style = {
    'backgroundColor': '#800080',
    'color': 'white',
}

app.layout = html.Div(
    [
        html.H1("S_system Tabs",style={"textAlign": "center"}),
        html.Hr(),
        dbc.Row(
            dbc.Tabs(
                [
                    dbc.Tab(label="PE_Spread Execution Tab", tab_id="tab-1", style=tab_style,active_tab_style=tab_selected_style),
                    dbc.Tab(label="PE_Spread Debug", tab_id="tab-2", style=tab_style,active_tab_style=tab_selected_style),
                    dbc.Tab(label="PE_Spread ATM plot", tab_id="tab-3", style=tab_style,active_tab_style=tab_selected_style),
                    dbc.Tab(label="PE_Spread WholeSheet", tab_id="tab-4", style=tab_style,active_tab_style=tab_selected_style),
                    dbc.Tab(label="PE_Spread CurrentSheet", tab_id="tab-5", style=tab_style,active_tab_style=tab_selected_style),
                    dbc.Tab(label="Flagship Execution Tab", tab_id="tab-6", style=tab_style,
                            active_tab_style=tab_selected_style),
                    dbc.Tab(label="Flagship Debug", tab_id="tab-7", style=tab_style,
                            active_tab_style=tab_selected_style),
                    dbc.Tab(label="Flagship WholeSheet", tab_id="tab-8", style=tab_style,
                            active_tab_style=tab_selected_style),
                    dbc.Tab(label="Flagship CurrentSheet", tab_id="tab-9", style=tab_style,active_tab_style=tab_selected_style)

                ],
                id="tabs",
                active_tab="tab-1",
            ),
        ),
        html.Hr(),
        html.Div(id="content"),
    ]
)
app.config.suppress_callback_exceptions=True

@app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
def switch_tab(at):
    if at == "tab-1":
        return tab1_content
    elif at == "tab-2":
        return tab2_content
    elif at == "tab-3":
        return tab3_content
    elif at == "tab-4":
        return tab4_content
    elif at == "tab-5":
        return tab5_content
    elif at == "tab-6":
        return tab6_content
    elif at == "tab-7":
        return tab7_content
    elif at == "tab-8":
        return tab8_content
    elif at == "tab-9":
        return tab9_content
    return html.P("This shouldn't ever be displayed...")

@app.callback(Output('stock_dropdown','options'), Input('interval-component','n_intervals'),suppress_callback_exceptions=True)
def stock_list(n):
    sql3 = f"SELECT distinct([AccountID]) FROM PEspread_clientConfig"
    df = pd.read_sql(sql3,engine)
    return [{'label': i['AccountID'], 'value': i['AccountID']} for r, i in df.iterrows()]

@app.callback(Output('table1','children'),Output('qty_sheet','children'),Input('stock_dropdown','value'),prevent_initial_call=True)
def update_datatable(csv_file):
    df = pd.read_sql(
        sql=f"SELECT * FROM PE_spread_qtysheet where [AccountID] = '{csv_file}' and Symbol = 'NIFTY' order by OptionType desc, Strike asc",
        con=engine)

    df = df.reset_index(drop=True)
    data = df.to_dict('rows')
    columns =  [{"name": i, "id": i,} for i in (df.columns)]
    return dt.DataTable(data=data, columns=columns),\
            "Qty Sheet :"

@app.callback(Output('table4','children'),Output('Total_table','children'),Input('interval-component','n_intervals'))
def update_datatable(n_clicks):
    sql4 = f"SELECT * FROM PE_spread_qtysheet"

    df4 = pd.read_sql(sql4, engine)
    df4 = df4.groupby(by=['AccountID','Symbol','Expiry','OptionType','CandleDateTime']).sum().reset_index()
    df4.drop(columns=['Strike','OptionType'],axis=1,inplace=True)
    df4 = df4[['CandleDateTime','AccountID','Expiry','Symbol','qty','Long_qty','Short_qty']]
    df4.rename(columns={'qty':'Total_qty'},inplace=True)
    # Calculate the Total
    nifty = df4.loc[df4['Symbol'] == 'NIFTY']
    nifty_sum = nifty['Total_qty'].astype(int).sum()
    nifty_long = nifty['Long_qty'].astype(int).sum()
    nifty_short = nifty['Short_qty'].astype(int).sum()
    banknifty = df4.loc[df4['Symbol'] == 'BANKNIFTY']
    banknifty_long = banknifty['Long_qty'].astype(int).sum()
    banknifty_short = banknifty['Short_qty'].astype(int).sum()
    banknifty_sum = banknifty['Total_qty'].astype(int).sum()
    df4 = df4.append({'Symbol': 'NIFTY_TOTAL','Total_qty':nifty_sum,'Long_qty':nifty_long,'Short_qty':nifty_short},ignore_index=True)
    df4 = df4.append({'Symbol': 'BANKNIFTY_TOTAL', 'Total_qty': banknifty_sum,'Long_qty':banknifty_long,'Short_qty':banknifty_short},ignore_index=True)

    data = df4.to_dict('rows')
    columns =  [{"name": str(i), "id": str(i),} for i in (df4.columns)]
    return dt.DataTable(data=data, columns=columns),\
            "Total sheet :"

@app.callback(Output('table2','children'),Output('Expiry_table','children'),Input('interval-component','n_intervals'))
def update_datatable(n_clicks):
    df2 = pd.read_sql(sql2, engine)
    data = df2.to_dict('rows')
    columns =  [{"name": i, "id": i,} for i in (df2.columns)]
    return dt.DataTable(data=data, columns=columns),\
            "Expiry Sheet :"

@app.callback(Output('dt_dropdown','options'), Input('interval-component','n_intervals'))
def stock_list(n):
    df = pd.read_sql(sql= f"select distinct CandleDateTime FROM PE_spread_Whole_qtysheet order by CandleDateTime desc", con= engine)
    return [str(i['CandleDateTime']) for r, i in df.iterrows()]

@app.callback(Output('stocks_dropdown','options'), Input('interval-component','n_intervals'))
def stock_list(n):
    df = pd.read_sql(sql= f"select distinct Symbol FROM PE_spread_Whole_qtysheet", con= engine)
    return [{'label': i['Symbol'], 'value': i['Symbol']} for r, i in df.iterrows()]

@app.callback(Output('client_dropdown','options'), Input('interval-component','n_intervals'))
def stock_list(n):
    df = pd.read_sql(sql= f"select distinct AccountID FROM PE_spread_Whole_qtysheet", con= engine)
    return [{'label': i['AccountID'], 'value': i['AccountID']} for r, i in df.iterrows()]

@app.callback(Output('table2_1','children'),
            [Input('submit-button2_1','n_clicks'),Input('dt_dropdown','value'),Input('stocks_dropdown','value'),Input('client_dropdown','value')],
                [State('submit-button2_1','n_clicks')])
def update_datatable(n_clicks,val1,val2,cli,ticker):
    if n_clicks:
        val1 = str(val1).replace('T',' ')
        df = pd.read_sql(sql= f"select * FROM PE_spread_Whole_qtysheet where CandleDateTime = '{val1}' and Symbol = '{val2}' and AccountID = '{cli}' order by AccountID asc", con= engine)
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data, columns=columns)

@app.callback(Output('table2_2','children'),
            [Input('submit-button2_1','n_clicks'),Input('dt_dropdown','value'),Input('stocks_dropdown','value'),Input('client_dropdown','value')],
                [State('submit-button2_1','n_clicks')])

def update_datatable(n_clicks,val1,val2,cli,ticker):
    if n_clicks:
        val1 = str(val1).replace('T', ' ')
        df = pd.read_sql(sql=f"select * FROM PE_spread_Whole_qtysheet where CandleDateTime = '{val1}' and Symbol = '{val2}' and AccountID = '{cli}' order by AccountID asc",con=engine)

        b = pd.DataFrame()
        b['CandleDateTime'] = ''
        b['AccountID'] = ''
        b['Expiry'] = ''
        b['Symbol'] = ''
        b['Total_qty'] = ''
        b['Long_CE_qty'] = ''
        b['Long_PE_qty'] = ''
        b['Short_CE_qty'] = ''
        b['Short_PE_qty'] = ''

        exp = df['Expiry'].unique()
        df_prev = df.groupby(by=['AccountID', 'Symbol', 'Expiry', 'OptionType']).sum().reset_index()
        #print(df_prev)
        time = val1
        for i in range(0,len(exp)):
            df_test = df_prev.loc[df_prev['Expiry'] == exp[i]]
            for_BNF = df_test.loc[df_test['Symbol'] == f'{val2}']
            for_BNF = for_BNF.reset_index(drop=True)
            long_CE_qty = for_BNF.loc[for_BNF['OptionType'] == 'CE']
            long_CE_qty = long_CE_qty.reset_index(drop=True)
            if long_CE_qty.empty == 1:
                long_CE = 0
                short_CE_qty = 0
            else:
                long_CE = long_CE_qty['Long_qty'][0]
                short_CE_qty = long_CE_qty['Short_qty'][0]
            long_PE_qty = for_BNF.loc[for_BNF['OptionType'] == 'PE']
            long_PE_qty = long_PE_qty.reset_index(drop=True)
            if long_PE_qty.empty == 1:
                long_PE = 0
                short_PE_qty = 0
            else:
                long_PE = long_PE_qty['Long_qty'][0]
                short_PE_qty = long_PE_qty['Short_qty'][0]

            b.loc[len(b.index)] = [time, for_BNF['AccountID'][0], for_BNF['Expiry'][0], for_BNF['Symbol'][0],
                                   for_BNF['qty'].sum(), long_CE, long_PE, short_CE_qty, short_PE_qty]

        #print(b)
        data = b.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (b.columns)]
        return dt.DataTable(data=data, columns=columns)

@app.callback([Output('table2_3','data'),Output('table2_3','columns')],Input('stocks_dropdown','value'),Input('CE/PE_dropdown','value'))
def update_table(stock,ce_pe):
    df = pd.read_sql(
        sql=f"SELECT Stage,Symbol,Strike,Ratio FROM PE_spread_currentSheet where Symbol = '{stock}' and stage like '%_OneFour' AND OptionType = '{ce_pe}'",
        con=engine)
    df2 = pd.read_sql(
        sql=f"SELECT Stage,Symbol,Strike,Ratio FROM PE_spread_currentSheet where Symbol = '{stock}' and stage like '%_OneHalf' AND OptionType = '{ce_pe}'",
        con=engine)
    df3 = pd.read_sql(
        sql=f"SELECT Stage,Symbol,Strike,Ratio FROM PE_spread_currentSheet where Symbol = '{stock}' and stage like '%_OneEight' AND OptionType = '{ce_pe}'",
        con=engine)

    df['OneFour'] = ''
    df2['OneHalf'] = ''
    df3['OneEight'] = ''
    qty_sheet = pd.read_sql(
        sql=f"SELECT distinct [Stage],[qty] FROM PE_spread_qtyConfig where Symbol = '{stock}' and CEPE = '{ce_pe}'",
        con=engine)
    qty_sheet['qty'] = qty_sheet['qty'].astype(float)
    qty_sheet = qty_sheet.set_index('Stage')

    for i in range(0, len(df)):
        temp = df['Stage'][i]
        temp2 = df2['Stage'][i]
        temp3 = df3['Stage'][i]
        df['OneFour'][i] = df['Ratio'][i] * qty_sheet['qty'][temp]
        df2['OneHalf'][i] = df2['Ratio'][i] * qty_sheet['qty'][temp2]
        df3['OneEight'][i] = df3['Ratio'][i] * qty_sheet['qty'][temp3]

    df = df.drop(['Ratio', 'Stage', 'Symbol'], axis=1)
    df = df.groupby(by=['Strike']).sum().reset_index()

    df2 = df2.drop(['Ratio', 'Stage', 'Symbol'], axis=1)
    df2 = df2.groupby(by=['Strike']).sum().reset_index()

    df3 = df3.drop(['Ratio', 'Stage', 'Symbol'], axis=1)
    df3 = df3.groupby(by=['Strike']).sum().reset_index()

    l = []
    l.append(df['Strike'].values.tolist() + df2['Strike'].values.tolist() + df3['Strike'].values.tolist())
    res = [*set(l[0])]
    res.sort()

    df = df.set_index('Strike')
    df2 = df2.set_index('Strike')
    df3 = df3.set_index('Strike')

    total_df = pd.DataFrame()
    total_df['Strike'] = res
    total_df['OneEight'] = ''
    total_df['OneHalf'] = ''
    total_df['OneFour'] = ''

    for i in range(0, len(total_df)):
        try:
            total_df['OneEight'][i] = df3['OneEight'][total_df['Strike'][i]]
        except:
            total_df['OneEight'][i] = 0

        try:
            total_df['OneHalf'][i] = df2['OneHalf'][total_df['Strike'][i]]
        except:
            total_df['OneHalf'][i] = 0

        try:
            total_df['OneFour'][i] = df['OneFour'][total_df['Strike'][i]]
        except:
            total_df['OneFour'][i] = 0

    total_df = total_df.astype(str)
    return total_df.to_dict('records'), [{"name": i, "id": i} for i in total_df.columns]

@app.callback(Output('plot','figure'),[Input('my-date-picker-range','start_date'),Input('my-date-picker-range','end_date')],prevent_initial_call=True)
def func(start,end):

    start = str(start)+" 9:30:00"
    end = str(end)+" 14:30:00"

    #df = pd.read_sql(sql=f"select * FROM [DeltaV7DB].[dbo].[DeltaV7_plot] where CandleDateTime >= '{start}' and CandleDateTime <='{end}' and Symbol='{index}'  order by CandleDateTime asc", con= engine)

    df = pd.read_sql(sql=f"select * FROM PE_spread_plot where CandleDateTime >= '{start}' and CandleDateTime <='{end}' order by CandleDateTime asc", con= engine)

    fig = px.line(df, x='CandleDateTime', y='Strike', color='Stage', markers=True)
    fig.update_xaxes(ticks="outside",
                     ticklabelmode="period",
                     tickcolor="black",
                     ticklen=10)

    return fig

@app.callback(Output('table_whole','children'),Input('interval','n_intervals'),Input('stage_dropdown','value'),prevent_initial_call=True)
def update_WholeSheet(n,stage):
    if stage == 'All':
        df = pd.read_sql(sql=f"SELECT top(100) * FROM PE_spread_wholeSheet order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    if stage == 'D1_T1' or stage == 'D1_T2' or stage == 'D1_T3' or stage == 'D2_T1' or stage == 'D2_T2' or stage == 'D2_T3' or stage == 'D3_T1' or stage == 'D3_T2' or stage == 'D3_T3':
        df = pd.read_sql(sql=f"SELECT top(200) * FROM PE_spread_wholeSheet where Stage like '{stage}'+'%' order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    else:
        return dash.no_update

@app.callback(Output('table_current','children'), Input('intervals','n_intervals'),Input('stages_dropdown','value'))
def update_CurrentSheet(n,stage):
    if stage == 'All':
        df = pd.read_sql(sql=f"SELECT * FROM [New_Ssystem].[dbo].[PE_spread_currentSheet] order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    if stage == 'D1_T1' or stage == 'D1_T2' or stage == 'D1_T3' or stage == 'D2_T1' or stage == 'D2_T2' or stage == 'D2_T3' or stage == 'D3_T1' or stage == 'D3_T2' or stage == 'D3_T3':
        df = pd.read_sql(sql=f"SELECT top(200) * FROM PE_spread_currentSheet where Stage like '{stage}'+'%' order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    else:
        return dash.no_update

@app.callback(Output('stock_dropdown_flag','options'), Input('interval-component_flag','n_intervals'),suppress_callback_exceptions=True)
def stock_list(n):
    sql3 = f"SELECT distinct([AccountID]) FROM Flagship_clientConfig_NF"
    df = pd.read_sql(sql3,engine)
    return [{'label': i['AccountID'], 'value': i['AccountID']} for r, i in df.iterrows()]

@app.callback(Output('table1_flag','children'),Output('qty_sheet_flag','children'),Input('stock_dropdown_flag','value'),prevent_initial_call=True)
def update_datatable(csv_file):
    df = pd.read_sql(
        sql=f"SELECT * FROM Flagship_qtysheet where AccountID = '{csv_file}' and (Symbol = 'NIFTY' or Symbol = 'BANKNIFTY') order by OptionType desc, Strike asc",
        con=engine)

    df = df.reset_index(drop=True)
    data = df.to_dict('rows')
    columns =  [{"name": i, "id": i,} for i in (df.columns)]
    return dt.DataTable(data=data, columns=columns),\
            "Qty Sheet :"

@app.callback(Output('table4_flag','children'),Output('Total_table_flag','children'),Input('interval-component_flag','n_intervals'))
def update_datatable(n_clicks):
    sql4 = f"SELECT * FROM Flagship_qtysheet"
    df4 = pd.read_sql(sql4, engine)
    df4 = df4.groupby(by=['AccountID','Symbol','Expiry','CandleDateTime']).sum().reset_index()
    df4.drop(columns=['Strike'],axis=1,inplace=True)
    df4 = df4[['CandleDateTime','AccountID','Expiry','Symbol','qty','Long_qty','Short_qty']]
    df4.rename(columns={'qty':'Total_qty'},inplace=True)
    # Calculate the Total
    nifty = df4.loc[df4['Symbol'] == 'NIFTY']
    nifty_sum = nifty['Total_qty'].astype(int).sum()
    nifty_long = nifty['Long_qty'].astype(int).sum()
    nifty_short = nifty['Short_qty'].astype(int).sum()
    banknifty = df4.loc[df4['Symbol'] == 'BANKNIFTY']
    banknifty_long = banknifty['Long_qty'].astype(int).sum()
    banknifty_short = banknifty['Short_qty'].astype(int).sum()
    banknifty_sum = banknifty['Total_qty'].astype(int).sum()
    df4 = df4.append({'Symbol': 'NIFTY_TOTAL','Total_qty':nifty_sum,'Long_qty':nifty_long,'Short_qty':nifty_short},ignore_index=True)
    df4 = df4.append({'Symbol': 'BANKNIFTY_TOTAL', 'Total_qty': banknifty_sum,'Long_qty':banknifty_long,'Short_qty':banknifty_short},ignore_index=True)
    data = df4.to_dict('rows')
    columns =  [{"name": str(i), "id": str(i),} for i in (df4.columns)]
    return dt.DataTable(data=data, columns=columns),\
            "Total sheet :"

@app.callback(Output('table2_flag','children'),Output('Expiry_table_flag','children'),Input('interval-component_flag','n_intervals'))
def update_datatable(n_clicks):
    df2 = pd.read_sql(sql=f"select * from Flagship_expiry", con=engine)
    data = df2.to_dict('rows')
    columns =  [{"name": i, "id": i,} for i in (df2.columns)]
    return dt.DataTable(data=data, columns=columns),\
            "Expiry Sheet :"

@app.callback(Output('dt_dropdown_FD','options'), Input('interval-component_FD','n_intervals'))
def stock_list(n):
    df = pd.read_sql(sql= f"select distinct CandleDateTime FROM Flagship_Whole_qtysheet order by CandleDateTime desc", con= engine)
    return [str(i['CandleDateTime']) for r, i in df.iterrows()]

@app.callback(Output('stocks_dropdown_FD','options'), Input('interval-component_FD','n_intervals'))
def stock_list(n):
    df = pd.read_sql(sql= f"select distinct Symbol FROM Flagship_Whole_qtysheet", con= engine)
    return [{'label': i['Symbol'], 'value': i['Symbol']} for r, i in df.iterrows()]

@app.callback(Output('client_dropdown_FD','options'), Input('interval-component_FD','n_intervals'))
def stock_list(n):
    df = pd.read_sql(sql= f"select distinct AccountID FROM Flagship_Whole_qtysheet", con= engine)
    return [{'label': i['AccountID'], 'value': i['AccountID']} for r, i in df.iterrows()]

@app.callback(Output('table2_1_FD','children'),
            [Input('submit-button2_1_FD','n_clicks'),Input('dt_dropdown_FD','value'),Input('stocks_dropdown_FD','value'),Input('client_dropdown_FD','value')],
                [State('submit-button2_1_FD','n_clicks')])
def update_datatable(n_clicks,val1,val2,cli,ticker):
    if n_clicks:
        val1 = str(val1).replace('T',' ')
        df = pd.read_sql(sql= f"select * FROM Flagship_Whole_qtysheet where CandleDateTime = '{val1}' and Symbol = '{val2}' and AccountID = '{cli}' order by AccountID asc", con= engine)
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data, columns=columns)

@app.callback(Output('table2_2_FD','children'),
            [Input('submit-button2_1_FD','n_clicks'),Input('dt_dropdown_FD','value'),Input('stocks_dropdown_FD','value'),Input('client_dropdown_FD','value')],
                [State('submit-button2_1_FD','n_clicks')])

def update_datatable(n_clicks,val1,val2,cli,ticker):
    if n_clicks:
        val1 = str(val1).replace('T', ' ')
        df = pd.read_sql(sql=f"select * FROM Flagship_Whole_qtysheet where CandleDateTime = '{val1}' and Symbol = '{val2}' and AccountID = '{cli}' order by AccountID asc",con=engine)

        b = pd.DataFrame()
        b['CandleDateTime'] = ''
        b['AccountID'] = ''
        b['Expiry'] = ''
        b['Symbol'] = ''
        b['Total_qty'] = ''
        b['Long_CE_qty'] = ''
        b['Long_PE_qty'] = ''
        b['Short_CE_qty'] = ''
        b['Short_PE_qty'] = ''

        exp = df['Expiry'].unique()
        df_prev = df.groupby(by=['AccountID', 'Symbol', 'Expiry', 'OptionType']).sum().reset_index()
        #print(df_prev)
        time = val1
        for i in range(0,len(exp)):
            df_test = df_prev.loc[df_prev['Expiry'] == exp[i]]
            for_BNF = df_test.loc[df_test['Symbol'] == f'{val2}']
            for_BNF = for_BNF.reset_index(drop=True)
            long_CE_qty = for_BNF.loc[for_BNF['OptionType'] == 'CE']
            long_CE_qty = long_CE_qty.reset_index(drop=True)
            if long_CE_qty.empty == 1:
                long_CE = 0
                short_CE_qty = 0
            else:
                long_CE = long_CE_qty['Long_qty'][0]
                short_CE_qty = long_CE_qty['Short_qty'][0]
            long_PE_qty = for_BNF.loc[for_BNF['OptionType'] == 'PE']
            long_PE_qty = long_PE_qty.reset_index(drop=True)
            if long_PE_qty.empty == 1:
                long_PE = 0
                short_PE_qty = 0
            else:
                long_PE = long_PE_qty['Long_qty'][0]
                short_PE_qty = long_PE_qty['Short_qty'][0]

            b.loc[len(b.index)] = [time, for_BNF['AccountID'][0], for_BNF['Expiry'][0], for_BNF['Symbol'][0],
                                   for_BNF['qty'].sum(), long_CE, long_PE, short_CE_qty, short_PE_qty]

        #print(b)
        data = b.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (b.columns)]
        return dt.DataTable(data=data, columns=columns)

@app.callback([Output('table2_3_FD','data'),Output('table2_3_FD','columns')],Input('stocks_dropdown_FD','value'),Input('CE/PE_dropdown_FD','value'))
def update_table(stock,ce_pe):
    df = pd.read_sql(
        sql=f"SELECT Stage,Symbol,Strike,Ratio FROM Flagship_currentSheet where Symbol = '{stock}' and stage like '%_OneFour' AND OptionType = '{ce_pe}'",
        con=engine)
    df2 = pd.read_sql(
        sql=f"SELECT Stage,Symbol,Strike,Ratio FROM Flagship_currentSheet where Symbol = '{stock}' and stage like '%_OneHalf' AND OptionType = '{ce_pe}'",
        con=engine)
    df3 = pd.read_sql(
        sql=f"SELECT Stage,Symbol,Strike,Ratio FROM Flagship_currentSheet where Symbol = '{stock}' and stage like '%_OneEight' AND OptionType = '{ce_pe}'",
        con=engine)

    df['OneFour'] = ''
    df2['OneHalf'] = ''
    df3['OneEight'] = ''
    qty_sheet = pd.read_sql(
        sql=f"SELECT distinct [Stage],[qty] FROM Flagship_qtyConfig where Symbol = '{stock}' and CEPE = '{ce_pe}'",
        con=engine)
    qty_sheet['qty'] = qty_sheet['qty'].astype(float)
    qty_sheet = qty_sheet.set_index('Stage')

    for i in range(0, len(df)):
        temp = df['Stage'][i]
        temp2 = df2['Stage'][i]
        temp3 = df3['Stage'][i]
        df['OneFour'][i] = df['Ratio'][i] * qty_sheet['qty'][temp]
        df2['OneHalf'][i] = df2['Ratio'][i] * qty_sheet['qty'][temp2]
        df3['OneEight'][i] = df3['Ratio'][i] * qty_sheet['qty'][temp3]

    df = df.drop(['Ratio', 'Stage', 'Symbol'], axis=1)
    df = df.groupby(by=['Strike']).sum().reset_index()

    df2 = df2.drop(['Ratio', 'Stage', 'Symbol'], axis=1)
    df2 = df2.groupby(by=['Strike']).sum().reset_index()

    df3 = df3.drop(['Ratio', 'Stage', 'Symbol'], axis=1)
    df3 = df3.groupby(by=['Strike']).sum().reset_index()

    l = []
    l.append(df['Strike'].values.tolist() + df2['Strike'].values.tolist() + df3['Strike'].values.tolist())
    res = [*set(l[0])]
    res.sort()

    df = df.set_index('Strike')
    df2 = df2.set_index('Strike')
    df3 = df3.set_index('Strike')

    total_df = pd.DataFrame()
    total_df['Strike'] = res
    total_df['OneEight'] = ''
    total_df['OneHalf'] = ''
    total_df['OneFour'] = ''

    for i in range(0, len(total_df)):
        try:
            total_df['OneEight'][i] = df3['OneEight'][total_df['Strike'][i]]
        except:
            total_df['OneEight'][i] = 0

        try:
            total_df['OneHalf'][i] = df2['OneHalf'][total_df['Strike'][i]]
        except:
            total_df['OneHalf'][i] = 0

        try:
            total_df['OneFour'][i] = df['OneFour'][total_df['Strike'][i]]
        except:
            total_df['OneFour'][i] = 0

    total_df = total_df.astype(str)
    return total_df.to_dict('records'), [{"name": i, "id": i} for i in total_df.columns]

@app.callback(Output('table_whole_flag','children'),Input('interval_flag','n_intervals'),Input('stage_dropdown_flag','value'),prevent_initial_call=True)
def update_WholeSheet(n,stage):
    if stage == 'All':
        df = pd.read_sql(sql=f"SELECT top(100) * FROM Flagship_wholeSheet order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        df['ATM_CE_close'] = round(df['ATM_CE_close'], 2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2'))) | ((df['Symbol']=='BANKNIFTY') & (df['OptionType'] == 'CE') & ((df['Ticker']=='ATM_Strike1') | (df['Ticker']=='ATM_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    if stage == 'D1_T1' or stage == 'D1_T2' or stage == 'D1_T3' or stage == 'D2_T1' or stage == 'D2_T2' or stage == 'D2_T3' or stage == 'D3_T1' or stage == 'D3_T2' or stage == 'D3_T3':
        df = pd.read_sql(sql=f"SELECT top(200) * FROM Flagship_wholeSheet where Stage like '{stage}'+'%' order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        df['ATM_CE_close'] = round(df['ATM_CE_close'], 2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2'))) | ((df['Symbol']=='BANKNIFTY') & (df['OptionType'] == 'CE') & ((df['Ticker']=='ATM_Strike1') | (df['Ticker']=='ATM_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    else:
        return dash.no_update

@app.callback(Output('table_current_flag','children'), Input('intervals_flag','n_intervals'),Input('stages_dropdown_flag','value'))
def update_CurrentSheet(n,stage):
    if stage == 'All':
        df = pd.read_sql(sql=f"SELECT * FROM Flagship_currentSheet order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        df['ATM_CE_close'] = round(df['ATM_CE_close'], 2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2'))) | ((df['Symbol']=='BANKNIFTY') & (df['OptionType'] == 'CE') & ((df['Ticker']=='ATM_Strike1') | (df['Ticker']=='ATM_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    if stage == 'D1_T1' or stage == 'D1_T2' or stage == 'D1_T3':
        df = pd.read_sql(sql=f"SELECT top(200) * FROM Flagship_currentSheet where Stage like '{stage}'+'%' order by CandleDateTime desc",con=engine)
        df['Syn_Fut'] = round(df['Syn_Fut'],2)
        df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
        df['ATM_CE_close'] = round(df['ATM_CE_close'], 2)
        # Filtering out the OneHalf's and OneEight's
        df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2'))) | ((df['Symbol']=='BANKNIFTY') & (df['OptionType'] == 'CE') & ((df['Ticker']=='ATM_Strike1') | (df['Ticker']=='ATM_Strike2')))]
        data = df.to_dict('rows')
        columns = [{"name": i, "id": i, } for i in (df.columns)]
        return dt.DataTable(data=data,columns=columns)
    else:
        return dash.no_update

@app.callback(Output("download-dataframe-csv", "data"),Output('display','children'),Input('submit-button','n_clicks'),Input('stages_dropdown_flag','value'),prevent_initial_call = True)
def download_table(n_clicks,stage):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if n_clicks and context == 'submit-button':
        try:
            if stage == 'All':
                df = pd.read_sql(sql=f"SELECT * FROM Flagship_currentSheet order by CandleDateTime desc", con=engine)
                df['Syn_Fut'] = round(df['Syn_Fut'], 2)
                df['ATM_PE_close'] = round(df['ATM_PE_close'], 2)
                df['ATM_CE_close'] = round(df['ATM_CE_close'], 2)
                # Filtering out the OneHalf's and OneEight's
                df = df.loc[((df['Symbol'] == 'NIFTY') & (df['OptionType'] == 'PE') & (
                            (df['Ticker'] == 'OneHalf_Strike1') | (df['Ticker'] == 'OneHalf_Strike2') | (
                                df['Ticker'] == 'OneEight_Strike1') | (df['Ticker'] == 'OneEight_Strike2'))) | (
                                        (df['Symbol'] == 'BANKNIFTY') & (df['OptionType'] == 'CE') & (
                                            (df['Ticker'] == 'ATM_Strike1') | (df['Ticker'] == 'ATM_Strike2')))]
                df.reset_index(drop=True,inplace=True)
                
                d = df['CandleDateTime'][0]
                
                return dcc.send_data_frame(df.to_csv, f"Flagship_CurrentSheet_{d}.csv", index=False), \
                       f"Download Successful"
        except Exception as e:
            print("The exception is ...")
            print(e)
            return f"NA", \
                   f"Download Failed"
        
        try:

            if stage == 'D1_T1' or stage == 'D1_T2' or stage == 'D1_T3':
                df = pd.read_sql(
                    sql=f"SELECT top(200) * FROM Flagship_currentSheet where Stage like '{stage}'+'%' order by CandleDateTime desc",
                    con=engine)
                df['Syn_Fut'] = round(df['Syn_Fut'], 2)
                df['ATM_PE_close'] = round(df['ATM_PE_close'], 2)
                df['ATM_CE_close'] = round(df['ATM_CE_close'], 2)
                # Filtering out the OneHalf's and OneEight's
                df = df.loc[((df['Symbol'] == 'NIFTY') & (df['OptionType'] == 'PE') & (
                            (df['Ticker'] == 'OneHalf_Strike1') | (df['Ticker'] == 'OneHalf_Strike2') | (
                                df['Ticker'] == 'OneEight_Strike1') | (df['Ticker'] == 'OneEight_Strike2'))) | (
                                        (df['Symbol'] == 'BANKNIFTY') & (df['OptionType'] == 'CE') & (
                                            (df['Ticker'] == 'ATM_Strike1') | (df['Ticker'] == 'ATM_Strike2')))]
                df.reset_index(drop=True, inplace=True)
                d = df['CandleDateTime'][0]

                return dcc.send_data_frame(df.to_csv, f"Flagship_CurrentSheet_{d}.csv", index=False), \
                        f"Download Successful"
        except:
            return f"NA", \
                   f"Download Failed"
        else:
            return dash.no_update
    else:
        return dash.no_update

@app.callback(Output("download-dataframe-2-csv", "data"),Output('display2','children'),Input('submit-button_2','n_clicks'),Input('stages_dropdown','value'),prevent_initial_call = True)
def download_table(n_clicks,stage):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if n_clicks and context == 'submit-button_2':
        if stage == 'All':
            try:
                df = pd.read_sql(sql=f"SELECT * FROM [New_Ssystem].[dbo].[PE_spread_currentSheet] order by CandleDateTime desc",con=engine)
                df['Syn_Fut'] = round(df['Syn_Fut'],2)
                df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
                # Filtering out the OneHalf's and OneEight's
                df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2')))]
                df.reset_index(drop=True, inplace=True)

                d = df['CandleDateTime'][0]

                return dcc.send_data_frame(df.to_csv, f"PEspread_CurrentSheet_{d}.csv", index=False), \
                       f"Download Successful"
            except:
                return f"NA", \
                       f"Download Failed"

        if stage == 'D1_T1' or stage == 'D1_T2' or stage == 'D1_T3' or stage == 'D2_T1' or stage == 'D2_T2' or stage == 'D2_T3' or stage == 'D3_T1' or stage == 'D3_T2' or stage == 'D3_T3':
            try:
                df = pd.read_sql(sql=f"SELECT top(200) * FROM PE_spread_currentSheet where Stage like '{stage}'+'%' order by CandleDateTime desc",con=engine)
                df['Syn_Fut'] = round(df['Syn_Fut'],2)
                df['ATM_PE_close'] = round(df['ATM_PE_close'],2)
                # Filtering out the OneHalf's and OneEight's
                df = df.loc[((df['Symbol']=='NIFTY') & (df['OptionType'] == 'PE') & ((df['Ticker']=='OneHalf_Strike1')|(df['Ticker']=='OneHalf_Strike2')| (df['Ticker']=='OneEight_Strike1')|(df['Ticker']=='OneEight_Strike2')))]
                df.reset_index(drop=True, inplace=True)

                d = df['CandleDateTime'][0]

                return dcc.send_data_frame(df.to_csv, f"PEspread_CurrentSheet_{d}.csv", index=False), \
                       f"Download Successful"
            except:
                return f"NA", \
                       f"Download Failed"
        else:
            return dash.no_update
    else:
        return dash.no_update

@app.callback(Output("download-dataframe-qtysheet-csv", "data"),Output('display_qtysheet','children'),Input('submit-button_qtysheet','n_clicks'),prevent_initial_call = True)
def download_qtysheet(n_clicks):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if n_clicks and context == 'submit-button_qtysheet':
        try:
            df = pd.read_sql(sql=f"SELECT * FROM PE_spread_qtysheet order by Symbol desc,AccountID asc,Strike asc,OptionType asc",con=engine)
            d = df['CandleDateTime'][0]
            return dcc.send_data_frame(df.to_csv,f"PEspread_qtysheet_{d}.csv",index=False), \
                    f"Download Successful"
        except:
            return f"NA", \
                   f"Download Failed"
    else:
        return dash.no_update

@app.callback(Output("download-dataframe-qtysheet-csv_flag", "data"),Output('display_qtysheet_flag','children'),Input('submit-button_qtysheet_flag','n_clicks'),prevent_initial_call = True)
def download_qtysheet(n_clicks):
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if n_clicks and context == 'submit-button_qtysheet_flag':
        try:
            df = pd.read_sql(sql=f"SELECT * FROM Flagship_qtysheet order by Symbol desc,AccountID asc,Strike asc,OptionType asc",con=engine)
            d = df['CandleDateTime'][0]
            return dcc.send_data_frame(df.to_csv,f"Flagship_qtysheet_{d}.csv",index=False), \
                    f"Download Successful"
        except:
            return f"NA", \
                   f"Download Failed"
    else:
        return dash.no_update


if __name__=='__main__':
    #app.run_server(debug=False,host='0.0.0.0',port=5030)
    app.run_server(debug=False)
