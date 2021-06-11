import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash
import dash_table
import pymongo
import pandas as pd
import json
import sys
from datetime import  datetime, timedelta, date
import tzlocal
import dash_table
import plotly.express as px
import pytz
from sklearn.metrics import mean_squared_error
import plotly.graph_objects as go
from plotly.subplots import make_subplots

client = pymongo.MongoClient("mongodb+srv://tuanna:tuanna123@bkluster.2bddf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.data_raw

def to_group_day(d):
    if d.hour < 9:
        return d.date() - timedelta(days=1)
    elif d.hour > 9:
        return d.date()
    else:
        if (d.minute < 30):
            return d.date() - timedelta(days=1)

collGRIMM = db['GRIMM03']
result2 = list(collGRIMM.find({"updated_time": {'$gte': 1610038800000, '$lt': 1619974800000}}, {"_id": 0, "updated_time": 1, "pm2_5": 1}))
dfGRI = pd.DataFrame(result2)
dfGRI = dfGRI.sort_values('updated_time')
local_timezone = pytz.timezone("Asia/Ho_Chi_Minh")  # get pytz timezone
dfGRI['date-local'] = dfGRI['updated_time'].apply(lambda d: datetime.fromtimestamp(d / 1000, local_timezone))
dfGRI['group_date'] = dfGRI['date-local'].apply(lambda d: to_group_day(d))
dfGRI['pm2_5'] = dfGRI['pm2_5'] * 1.7907 + 7.5745

dfGRI_raw = dfGRI.copy()
dfGRI_raw['day_dif'] = dfGRI_raw['updated_time'].diff()
dfGRI_raw.at[0, 'day_dif'] = 0
dfGRI_raw['day_dif'] = dfGRI_raw['day_dif']/3600/24/1000
dfGRI_raw.loc[dfGRI_raw["day_dif"] >= 0.004, "pm2_5"] = None

del dfGRI['date-local']
del dfGRI['updated_time']
# print(dfGRI)
dfGRI = dfGRI.groupby(['group_date']).agg(['mean', 'count'])
dfGRI.columns = [' '.join(str(i) for i in col) for col in dfGRI.columns]
dfGRI.reset_index(inplace=True)
dfGRI = dfGRI.drop(dfGRI[dfGRI['pm2_5 count'] < 240].index)
cols = ['group_date', 'pm2_5 mean']
dfGRI = dfGRI[cols]
dfGRI.rename(columns={'group_date': 'date', 'pm2_5 mean': 'pm2_5'}, inplace=True)
# dfCompare = pd.merge(dfGRI, dfLCS, on="date")

# print(dfCompare['pm2_5_x'].corr(dfCompare['pm2_5_y'], method='pearson'))
# sns_plot  = sns.scatterplot(x="pm2_5_x", y="pm2_5_y", data=dfCompare)
# sns_plot.figure.savefig("output.png")
# rmse = mean_squared_error(dfCompare['pm2_5_x'], dfCompare['pm2_5_y'], squared = False)
# print (rmse)

def init_comparedashboard(server):
    comparedashboard = dash.Dash(__name__, server=server, url_base_pathname='/compare/')
    comparedashboard.layout = html.Div([
        html.Div([
            html.H1(children='Dự án INEST',
                    style={'textAlign': 'center', 'color': 'white', 'font-family': 'Dosis', 'font-size': '30px'}
                    )],
            style={'padding-top': '0.2%', 'background-color': 'rgb(41, 56, 55)'}
        ),

        html.Div([

            html.Div([], className='col-3'),

            html.Div([
                html.A(
                    html.H4(children='Dữ liệu thô các thiết bị'),
                    href='/dashapp/'
                )
            ],
                className='col-2'),

            html.Div([
                html.A(
                    html.H4(children='Hiệu chuẩn thiết bị',
                            style={'text-decoration': 'underline',
                                   'text-decoration-color': 'rgb(255, 101, 131)',
                                   'text-shadow': '0px 0px 1px rgb(251, 251, 252)'}
                            ),
                    href='/compare/'
                )
            ],
                className='col-2'),

            html.Div([
                html.A(
                    html.H4(children='Thành viên dự án'),
                    href='/upload/'
                )
            ],
                className='col-2'),

            html.Div([], className='col-3')

        ],
            className='row',
            style={'background-color': 'rgb(57, 81, 85)',
                   'box-shadow': '2px 5px 5px 1px rgba(255, 101, 131, .5)'}
        ),

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                    ],
                        className='col-2'),
                    html.Div(
                        [html.H5(
                            children='Lọc theo hoảng thời gian:',
                            style={'text-align': 'left', 'color': 'rgb(77, 79, 91)'}
                        ),
                            html.Div(['Chọn khoảng thời gian: ',
                                      dcc.DatePickerRange(
                                          id='my-date-picker-range',
                                          min_date_allowed=date(2020, 12, 1),
                                          max_date_allowed=date(2021, 12, 31),
                                          initial_visible_month=date(2021, 5, 1),
                                          start_date=date(2020, 12, 30),
                                          end_date=date.today(),
                                          style={'font-size': '15px', 'display': 'inline-block', 'border-radius': '2px',
                                                 'border': '1px solid #ccc', 'color': '#333', 'border-spacing': '0',
                                                 'border-collapse': 'separate'}
                                      ), ],
                                     style={'margin-top': '10px',
                                            'margin-bottom': '5px',
                                            'text-align': 'left',
                                            'paddingLeft': 5}
                                     )
                        ], className='col-4'),
                    html.Div([
                    ],
                        className='col-2'),
                    html.Div([
                        html.H5(
                            children='Tên thiết bị:',
                            style={'text-align': 'left', 'color': 'rgb(77, 79, 91)'}
                        ),
                        html.Div([
                            'Chọn thiết bị thiển thị: ',
                            dcc.Dropdown(
                                id='demo-dropdown',
                                options=[
                                    {'label': 'LCS1', 'value': 'LCS1'},
                                    {'label': 'LCS2', 'value': 'LCS2'},
                                    {'label': 'LCS3', 'value': 'LCS3'},
                                    {'label': 'LCS5', 'value': 'LCS5'},
                                    {'label': 'LCS6', 'value': 'LCS6'},
                                    {'label': 'LCS7', 'value': 'LCS7'},
                                    {'label': 'LCS8', 'value': 'LCS8'},
                                    {'label': 'LCS9', 'value': 'LCS9'},
                                    {'label': 'LCS10', 'value': 'LCS10'},
                                    {'label': 'LCS12', 'value': 'LCS12'},
                                    {'label': 'LCS14', 'value': 'LCS14'},
                                    {'label': 'LCS15', 'value': 'LCS15'},
                                    {'label': 'LCS16', 'value': 'LCS16'},
                                    {'label': 'LCS17', 'value': 'LCS17'},
                                    {'label': 'LCS18', 'value': 'LCS18'},
                                    {'label': 'LCS19', 'value': 'LCS19'},
                                    {'label': 'LCS20', 'value': 'LCS20'},
                                ],
                                value='LCS1',
                                style=dict(
                                    width='100px',
                                    display='inline-block',
                                    verticalAlign="middle",
                                    fontsize='11px'

                                )
                            )
                        ], style={'margin-top': '10px',
                                  'margin-bottom': '5px',
                                  'text-align': 'left',
                                  'paddingLeft': 5})
                    ], className='col-4'),
                    html.Div([
                    ],
                        className='col-2')  # Blank 2 columns
                ], className='row'),
            ], className='col-12',
                style={'border-radius': '0px 0px 10px 10px',
                       'border-style': 'solid',
                       'border-width': '1px',
                       'border-color': 'rgb(186, 218, 212)',
                       'background-color': 'rgb(186, 218, 212)',
                       'box-shadow': '2px 5px 5px 1px  rgba(255, 101, 131, .5)'}),
        ], className='row sticky-top'),



        html.Div(
        style={'marginLeft': 'auto', 'marginRight': 'auto', "margin-top": "40px"},
        children = [
        dash_table.DataTable(
            id='table',
            fixed_rows={'headers': True},
            style_table={
                'width': '50%',
                'minWidth': '50%',
                'marginLeft': 'auto',
                'marginRight': 'auto'
            },
            style_cell={
                'fontFamily': 'Open Sans',
                'textAlign': 'center',
                'height': '60px',
                'padding': '2px 22px',
                'whiteSpace': 'inherit',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
        ),
        html.Div(
            style={"margin-top": "20px"},
            children=[
            html.H5(id="table-caption",
                    style={
                        'textAlign': 'center',
                        'color': 'rbg(0,0,0)',
                        'fontWeight': 'bold',
                    })
        ]
        )
        ],
        ),
        html.Div(style={"display": "table", "width": "100%", "table-layout": "fixed", "border-spacing": "10px"},
                 children=[
                     html.Div(style={"width": "150px", "display":"table-cell"}),
                     html.Div(
                         style={"display": "table-cell"},
                         children=[
                             dcc.Graph(id='scatter-output')
                         ]),
                     html.Div(
                         style={"display": "table-cell"},
                         children=[
                             dcc.Graph(id='bar-output')
                         ]),
                     html.Div(style={"width": "150px", "display": "table-cell"}),
        ]),
        # html.Div(
        #     children=[
        #         dcc.Graph(id='scatter-output')
        #     ]),
        # html.Div(
        #     children=[
        #         dcc.Graph(id='bar-output')
        #     ]),
        html.Div(
            children=[
                dcc.Graph(id='line-output')
            ]),
    ])
    init_callbacks(comparedashboard)

    return comparedashboard.server

def init_callbacks(comparedashapp):
    @comparedashapp.callback(
        [Output('table', 'columns'),
         Output('table', 'data'),
         Output('scatter-output', 'figure'),
         Output('table-caption', 'children'),
         Output('line-output', 'figure'),
         Output('line-output', 'style'),
         Output('bar-output', 'figure'),
         Output('bar-output', 'style')],
        [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date'),
         Input('demo-dropdown', 'value')]
    )
    def buil_fig(start_date, end_date, value):
        coll = db[value]

        unix_start = datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000
        unix_end = datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000


        result = list(coll.find({"updated_time": {'$gte': unix_start, '$lt': unix_end}}, {"_id": 0, "updated_time": 1, "pm2_5": 1}))
        dfLCS = pd.DataFrame(result)

        if len(dfLCS) > 0:
            dfLCS = dfLCS.sort_values('updated_time')
            local_timezone = pytz.timezone("Asia/Ho_Chi_Minh")  # get pytz timezone
            dfLCS['date-local'] = dfLCS['updated_time'].apply(lambda d: datetime.fromtimestamp(d / 1000, local_timezone))
            dfLCS['group_date'] = dfLCS['date-local'].apply(lambda d: to_group_day(d))

            dfLCS_raw = dfLCS.copy()
            dfLCS_raw['day_dif'] = dfLCS_raw['updated_time'].diff()
            dfLCS_raw.at[0, 'day_dif'] = 0
            dfLCS_raw['day_dif'] = dfLCS_raw['day_dif'] / 3600 / 24 / 1000

            if value not in ["LCS17", "LCS18", "LCS19", "LCS20"]:
                dfLCS_raw.loc[dfLCS_raw["day_dif"] >= 0.004, "pm2_5"] = None
            else:
                dfLCS_raw.loc[dfLCS_raw["day_dif"] >= 0.042, "pm2_5"] = None
            del dfLCS['date-local']
            del dfLCS['updated_time']

            dfLCS = dfLCS.groupby(['group_date']).agg(['mean', 'count'])
            dfLCS.columns = [' '.join(str(i) for i in col) for col in dfLCS.columns]
            dfLCS.reset_index(inplace=True)
            if value not in ["LCS17", "LCS18", "LCS19", "LCS20"]:
                dfLCS = dfLCS.drop(dfLCS[dfLCS['pm2_5 count'] < 240].index)
            else:
                dfLCS = dfLCS.drop(dfLCS[dfLCS['pm2_5 count'] < 20].index)
            cols = ['group_date', 'pm2_5 mean']
            dfLCS = dfLCS[cols]
            dfLCS.rename(columns={'group_date': 'date', 'pm2_5 mean': 'pm2_5'}, inplace=True)

            dfCompare = pd.merge(dfGRI, dfLCS, on="date")
            dfCompare['Bias'] = (dfCompare['pm2_5_y']/dfCompare['pm2_5_x'] - 1)*100

            fulfillment = round(len(dfCompare)/len(dfGRI), 3)
            pearson_cor = round(dfCompare['pm2_5_x'].corr(dfCompare['pm2_5_y'], method='pearson'),2)
            rmse = round(mean_squared_error(dfCompare['pm2_5_x'], dfCompare['pm2_5_y'], squared=False),3)
            table_data = [{"Số điểm quan sát": [len(dfGRI)], "Tỉ lệ lấp đầy": [fulfillment], "Pearson Correlation": [pearson_cor],
                          "RMSE": [rmse], "Bias min": [round(dfCompare['Bias'].min(), 2)], "Bias max": [round(dfCompare['Bias'].max(), 2)]}]
            columns_name = ["Số điểm quan sát", "Tỉ lệ lấp đầy", "Pearson Correlation", "RMSE", "Bias min", "Bias max"]
            columns=[{"name": i, "id": i} for i in columns_name]

            fig = px.scatter(x=dfCompare['pm2_5_x'], y=dfCompare['pm2_5_y'],
                             labels={"x": "GRIMM03", "y": value},
                             title="So sánh nồng độ PM2.5 giữa GRIMM03 và {}".format(value))

            fig.update_xaxes(
                range=[0, 300],  # sets the range of xaxis
                constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
            )

            fig.update_yaxes(
                scaleanchor="x",
                scaleratio=1,
                range=[0,300],
            )
            fig.update_layout(
                width=700,
                height=700,
            )

            # fig = px.line(dfGRI_raw, x=dfGRI_raw['date-local'], y=dfGRI_raw['pm2_5'])
            fig_line = make_subplots(specs=[[{"secondary_y": False}]])
            fig_line.add_trace(
                go.Line(x=dfGRI_raw['date-local'], y=dfGRI_raw['pm2_5'], name ="Dữ liệu GRIMM03")
            )
            fig_line.add_trace(
                go.Line(x=dfLCS_raw['date-local'], y=dfLCS_raw['pm2_5'], name="Dữ liệu LCS")
            )
            fig_line.update_layout(
                title="Nồng độ bụi PM2.5 theo thời gian".format(value),
                xaxis_title="Thời gian",
                yaxis_title="Giá trị (µg/m3)")

            caption = "Bảng đánh giá thiết bị {} theo trung bình ngày".format(value)

            bardata = {"Devices": ["GRIMM03", value], "Conc": [dfGRI_raw['pm2_5'].mean(), dfLCS_raw['pm2_5'].mean()]}
            bardf = pd.DataFrame.from_dict(bardata)
            # print(bardf)
            # fig_bar = px.bar(bardf, x=bardf["Devices"], y=bardf["Conc"])
            fig_bar = go.Figure(data=[go.Bar(
                x=bardf["Devices"],
                y=bardf["Conc"],
                marker_color=['blue','red'],
                # marker color can be a single color value or an iterable
            )])
            fig_bar.update_layout(
                title="Nồng độ bụi PM2.5 trung bình của GRIMM03 và {}".format(value),
                xaxis_title="Thiết bị",
                yaxis_title="Giá trị (µg/m3)")

            return columns, table_data, fig, caption, fig_line, {'display':'block'}, fig_bar, {'display':'block'}
        else:
            fig = go.Figure()
            fig.update_layout(
                xaxis={"visible": False},
                yaxis={"visible": False},
                annotations=[
                    {
                        "text": "Không tìm thấy dữ liệu",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            )
            return None, None, fig, None, {}, {'display':'none'}, {}, {'display':'none'}
