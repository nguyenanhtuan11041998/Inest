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
import plotly.graph_objects as go
import pytz

def init_dashboard(server, db):
    dashapp = dash.Dash(__name__, server=server, url_base_pathname='/dashapp/')
    dashapp.layout = html.Div(
        children = [
            html.Div([
                html.H1(children='Dự án INEST',
                        style={'textAlign': 'center', 'color': 'white', 'font-family': 'Dosis', 'font-size': '30px'}
                        )],
                style={'padding-top': '0.2%', 'background-color' : 'rgb(41, 56, 55)'}
            ),

            html.Div([

                html.Div([], className='col-3'),

                html.Div([
                    html.A(
                        html.H4(children='Dữ liệu thô các thiết bị',
                                style={'text-decoration' : 'underline',
                                'text-decoration-color' : 'rgb(255, 101, 131)',
                                'text-shadow': '0px 0px 1px rgb(251, 251, 252)'}),
                        href='/dashapp/'
                    )
                ],
                    className='col-2'),

                html.Div([
                    html.A(
                        html.H4(children='Đánh giá thiết bị'),
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
                                children='Lọc theo khoảng thời gian:',
                                style={'text-align': 'left', 'color': 'rgb(77, 79, 91)'}
                            ),
                                html.Div(['Chọn khoảng thời gian: ',
                                dcc.DatePickerRange(
                                    id='my-date-picker-range',
                                    min_date_allowed=date(2020, 12, 1),
                                    max_date_allowed=date(2021, 12, 31),
                                    initial_visible_month=date(2021, 5, 1),
                                    start_date=date(2021, 4, 1),
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
                                        {'label': 'GRIMM03', 'value': 'GRIMM03'},
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
                    ], className = 'row'),
                ],className = 'col-12',
        style = {'border-radius' : '0px 0px 10px 10px',
                'border-style' : 'solid',
                'border-width' : '1px',
                'border-color' : 'rgb(186, 218, 212)',
                'background-color' : 'rgb(186, 218, 212)',
                'box-shadow' : '2px 5px 5px 1px  rgba(255, 101, 131, .5)'}),
            ], className='row sticky-top'),

            html.Div(
                style={"margin-top": "40px"},
                children = [
                dash_table.DataTable(
                id='table',
                export_format="csv",
                fixed_rows={'headers': True},
                # style table
                style_table={
                    'maxHeight': '50ex',
                    'overflowY': 'auto',
                    'page_size': 20,
                    'page_action':'custom',
                    'current_page':0,
                    'width': '100%',
                    'minWidth': '100%',
                },
                # style cell
                style_cell={
                    'fontFamily': 'Open Sans',
                    'textAlign': 'center',
                    'height': '60px',
                    'padding': '2px 22px',
                    'whiteSpace': 'inherit',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'State'},
                        'textAlign': 'left'
                    },
                ],
                # style header
                style_header={
                    'fontWeight': 'bold',
                    'backgroundColor': 'white',
                },
                # style filter
                # style data
                style_data_conditional=[
                    {
                        # stripped rows
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    },
                ],
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
            ]),
            html.Div(
                style={"margin-top": "40px"},
                children= [
                dcc.Graph(id='graph-output')
            ]),
        ],
    )

    init_callbacks(dashapp, db)

    return dashapp.server

def init_callbacks(dashapp, db):
    @dashapp.callback(
            [Output('table','columns'),
            Output('table','data'),
            Output('graph-output', 'figure'),
            Output('table-caption', 'children')],
            [Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date'),
            Input('demo-dropdown', 'value')]
        )
    def buil_fig(start_date, end_date, value):
        coll = db[value]

        unix_start= datetime.strptime(start_date, "%Y-%m-%d").timestamp()*1000
        unix_end= datetime.strptime(end_date, "%Y-%m-%d").timestamp()*1000


        result = list(coll.find({"updated_time": {'$gte': unix_start, '$lt': unix_end}}))
        df = pd.DataFrame(result)
        # print(df)
        if len(df) > 0:
            del df['_id']
            df = df.sort_values('updated_time')
            df['day_dif'] = df['updated_time'].diff()
            df.at[0, 'day_dif'] = 0
            local_timezone = tzlocal.get_localzone() # get pytz timezone
            df['date-local'] = df['updated_time'].apply(lambda d: datetime.fromtimestamp(d/1000, local_timezone))
            df['date-local'] = df['date-local'].apply(lambda d: " ".join(d.strftime("%Y-%m-%dT%H:%M:%S.%f%z").split("+")[0].split('.')[0].split("T")))

            df['day_dif'] = df['day_dif']/3600/24/1000
            df['pm2_5-copy'] = df['pm2_5']

            if value not in ["LCS17", "LCS18", "LCS19", "LCS20"]:
                df.loc[df["day_dif"] >= 0.004, "pm2_5-copy"] = None
            else:
                df.loc[df["day_dif"] >= 1.1, "pm2_5-copy"] = None
            ### Xử lí dữ liệu khác nhau ở đây
            if value in ["LCS1", "LCS2"]:
                df_comlumns = ["date-local", "pm1", "pm2_5", "pm10", "aqi", "h", "t", "pm2_5-copy"]
                df = df[df_comlumns]
            elif value in ["GRIMM03", "LCS3"]:
                df_columns = ["date-local", "pm1", "pm2_5", "pm10", "pm2_5-copy"]
                df = df[df_columns]
            elif value in ["LCS5", "LCS6", "LCS7", "LCS8", "LCS9", "LCS10"]:
                df_columns = ["Mã trạm", "date-local", "pm2_5", "pm10", "Temperature", "Humidity", "pm2_5-copy"]
                df = df[df_columns]
            elif value == "LCS12":
                df_columns = ["date-local", "pm1", "pm2_5", "temp", "hum", "pm2_5-copy"]
                df = df[df_columns]
            elif value in ["LCS14", "LCS15", "LCS16"]:
                df_columns = ["date-local", "pm2_5", "pm2_5-copy"]
                df = df[df_columns]
            elif value in ["LCS17", "LCS18"]:
                df_columns = ["date-local", "pm2_5", "aqi", "t", "h", "pm2_5-copy"]
                df = df[df_columns]
            elif value in ["LCS19", "LCS20"]:
                df_columns = ["date-local", "pm1", "pm2_5", "tp", "hm", "pm2_5-copy"]
                df = df[df_columns]


            # df.columns = [ ''.join(str(i) for i in col) for col in df.columns]
            fig = px.line(df, x=df['date-local'], y=df['pm2_5-copy'],
                        labels={"date-local": "Thời gian", "pm2_5-copy": "PM2.5"},
                        title="Nồng độ bụi PM2.5 theo thời gian")
            del df['pm2_5-copy']

            ### Xu li df khac nhau o day
            if value in ["LCS1", "LCS2"]:
                df.rename(columns={'date-local': 'Thời gian', "pm1": "PM1 (µg/m3)", "pm2_5": "PM2.5 (µg/m3)", "pm10": "PM10 (µg/m3)", "h": "Độ ẩm (µg/m3)", "t": "Nhiệt độ (C)", "aqi": "AQI"}, inplace=True)
            elif value in ["GRIMM03", "LCS3"]:
                df.rename(columns={'date-local': 'Thời gian', "pm1": "PM1 (µg/m3)", "pm2_5": "PM2.5 (µg/m3)", "pm10": "PM10 (µg/m3)"}, inplace=True)
            elif value in ["LCS5", "LCS6", "LCS7", "LCS8", "LCS9", "LCS10"]:
                df.rename(columns={'date-local': 'Thời gian', "pm1": "PM1 (µg/m3)", "pm2_5": "PM2.5 (µg/m3)", "pm10": "PM10 (µg/m3)", "Temperature": "Nhiệt độ (C)", "Humidity": "Độ ẩm (µg/m3)"},
                          inplace=True)
            elif value == "LCS12":
                df.rename(columns={'date-local': 'Thời gian', "pm1": "PM1 (µg/m3)", "pm2_5": "PM2.5 (µg/m3)", "temp": "Nhiệt độ (C)", "hum": "Độ ẩm (µg/m3)"},
                          inplace=True)
            elif value in ["LCS14", "LCS15", "LCS16"]:
                df.rename(columns={'date-local': 'Thời gian', "pm2_5": "PM2.5 (µg/m3)"}, inplace=True)
            elif value in ["LCS17", "LCS18"]:
                df.rename(columns={'date-local': 'Thời gian', "pm2_5": "PM2.5 (µg/m3)", "aqi": "AQI", "t": "Nhiệt độ (C)", "h": "Độ ẩm (µg/m3)"}, inplace=True)
            elif value in ["LCS19", "LCS20"]:
                df.rename(columns={'date-local': 'Thời gian', "pm1": "PM1 (µg/m3)", "pm2_5": "PM2.5 (µg/m3)", "tp": "Nhiệt độ (C)", "hm": "Độ ẩm (µg/m3)"}, inplace=True)

            columns = [{"name": i, "id": i} for i in df.columns]
            data = df.to_dict('records')
            caption = "Dữ liệu thiết bị {}".format(value)
            return columns, data, fig, caption

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
            return [], [], fig, ""
