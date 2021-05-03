import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash  # (version 1.12.0) pip install dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np

external_stylesheets = ['./assets/my_template.css']
My_settings = {
        "Deactive_color": "#19aae1",
        "Active_color": '#ffa500',
        "Plot_color": '#1f2c56',
        "Paper_color": '#1f2c56',
        "Font_color": '#ee9b06',
        "text_color": 'white',
        "grid_color": '#476293',
        "margin_left": "1.6vw"
    }
# ---------- Import and clean data (importing csv into pandas)
#ranked_comb_info = pd.read_csv("results/all_ranked_comb.csv")

#----------------------
Num_act = 7
Num_motor = 13
Num_gear = 4
Num_stiff = 8
Motor_i = 1
Gear_i = 1
Stiff_i = 1
Ass_i = 1
cycle = np.arange(100)

#---------------------------
Motor_i_prev = 0
Gear_i_prev = 0
Stiff_i_prev = 0
Ass1_i_prev, Ass2_i_prev, Ass3_i_prev, Ass4_i_prev, Ass5_i_prev, Ass6_i_prev, Ass7_i_prev = 0, 0, 0, 0, 0, 0, 0
fig1, fig2, fig3, fig4, fig5, fig6 = 0, 0, 0, 0, 0, 0
fig7, fig8, fig9, fig10, fig11, fig12 = 0, 0, 0, 0, 0, 0
fig13, fig14, fig15, fig16, fig17, fig18 = 0, 0, 0, 0, 0, 0
fig19, fig20, fig21, fig22, fig23, fig24 = 0, 0, 0, 0, 0, 0
fig25, fig26, fig27, fig28, fig29, fig30 = 0, 0, 0, 0, 0, 0
fig31, fig32, fig33, fig34, fig35, fig36 = 0, 0, 0, 0, 0, 0
fig37, fig38, fig39, fig40, fig41, fig42 = 0, 0, 0, 0, 0, 0

# ------------------------------------------------------------------------------
# App layout

Silder_length = 220
Fig_width = 240
Fig_height = 150

def generate_graph(base_id1=None, base_id2=None, num_act=None):
    all_graphs = []
    for i in range(num_act):
        graph_pair = html.Div(children=[
            dcc.Graph(id=base_id1.format(i+1), figure={}, style={"width": Fig_width, "height": Fig_height}),
            dcc.Graph(id=base_id2.format(i+1), figure={}, style={"width": Fig_width, "height": Fig_height})
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"], 'margin-top': '1vw'})
        all_graphs.append(graph_pair)

    return all_graphs


def generate_text_slide_bar(text_id=None, silder_id=None, stat_id=None, num_rating=2):
    all_comp = []
    default_value = [0.8, 0.8]
    activity_titles = ['Torque rating', 'Speed rating']
    for i in range(num_rating):
        single_comp = html.Div(children=[
            html.P(id=text_id.format(i+1), children=activity_titles[i]),
            dcc.Slider(id=silder_id.format(i+1),
                       min=0.1,
                       max=1,
                       step=0.1,
                       marks={0: "0%",
                              0.5: "50%",
                              1: "100%"},
                       value=default_value[i],
                       ),
            html.Div(id=stat_id.format(i+1))

        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw', 'margin-right': '1vw',
                  'margin-top': '1vw', "width": Silder_length})
        all_comp.append(single_comp)

    return all_comp


def generate_activity(text_id=None, activity_titles=None, num_act=7):
    all_comp = []
    for i in range(num_act):
        single_comp = html.Div(children=[
            html.P(id=text_id.format(i + 1), children=activity_titles[i])
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw', 'margin-right': '1vw',
                  'margin-top': '1vw', "width": Silder_length})
        all_comp.append(single_comp)

    return all_comp


def generate_optimality_numbers(text_id1=None, text_id2=None, text_id3=None, num_act=7):
    all_comp = []
    margins = ['2vw', '7vw', '7vw', '7vw', '7vw', '7vw', '7vw']
    for i in range(num_act):
        single_comp = html.Div(children=[
            html.P(id=text_id1.format(i+1), children="Initializing..."),
            html.P(id=text_id2.format(i+1), children="Initializing..."),
            html.P(id=text_id3.format(i+1), children="Initializing...")
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': margins[i], 'margin-top': '1vw'})
        all_comp.append(single_comp)

    return all_comp


def generate_ts_ta_graphs(text_id1=None, num_act=7):
    all_comp = []
    for i in range(num_act):
        single_comp = html.Div(children=[
              dcc.Graph(id=text_id1.format(i+1), figure={},
                        style={"width": Fig_width, "height": Fig_height})
          ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                    'margin-top': '1vw'})
        all_comp.append(single_comp)

    return all_comp


def generate_table(text_id1=None, data=None):
    single_comp = dash_table.DataTable(
        id=text_id1,
        columns=[{"name": i, "id": i} for i in data.columns],
        data=data.to_dict('records'),
        style_cell={
            'backgroundColor': My_settings["Plot_color"],
            'color': "#f3f5f4"})

    return single_comp


def generate_app_layout(ranked_comb_info, human_data, motor_catalog, gear_catalog, actuator):

    num_activity = len(human_data.weights)

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        # left-side column
        html.Div(style={'display': 'inline-block', 'background-color': '#192444', 'vertical-align': 'top', 'margin-left': '1vw', 'margin-right': '1vw', 'margin-top': '1vw'},
                 children=[
            html.Div(style={'background-color': '#192444'},
                     children=[

                # 0th row
                html.Div(children=[
                    html.P(id = 'text0', children='Actuator optimization - by Mingrui and Tomislav'),
                    html.P(id='text09', children="Bodyweight: 90kg")
                ], className='row', style={'fontColor': 'white'}),

                # select row
                html.Div(children=[
                    html.Br()] + generate_text_slide_bar(text_id="rating_title{}", silder_id="rating_slider{}", stat_id="rating_slider_output_container{}", num_rating=2),
                    className='row', style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '7vw', 'margin-right': '3vw', 'margin-top': '1vw'}),


                # first row
                html.Div(children=[
                    html.Br()] + generate_activity(text_id="act_title{}", activity_titles=human_data.angle_files, num_act=num_activity),
                    className='row', style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '7vw', 'margin-right': '3vw', 'margin-top': '1vw'}),

                # second row
                html.Div(children=[
                    html.Div(children=[
                        html.P(id='Combination_txt', children='Combination'),
                        dcc.Dropdown(id='Combination',
                                     options=[
                                        {'label': 'C1', 'value': 'C1'},
                                        {'label': 'C2', 'value': 'C2'},
                                        {'label': 'C3', 'value': 'C3'},
                                        {'label': 'C4', 'value': 'C4'},
                                        {'label': 'C5', 'value': 'C5'},
                                        {'label': 'C6', 'value': 'C6'},
                                        {'label': 'C7', 'value': 'C7'},
                                        {'label': 'C8', 'value': 'C8'},
                                         {'label': 'C9', 'value': 'C9'},
                                         {'label': 'C10', 'value': 'C10'}
                                     ],
                                     value="M13",
                                     style={"color": "#212121"}),
                    ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '1vw'})],
                       className='row'),

                # sixth row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='ts1', children='Torque-speed'),
                          html.P(id='ts2', children='Desired', style={"color": "red"}),
                          html.P(id='ts3', children='Actual', style={"color": My_settings["Active_color"]})

                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_ts_ta_graphs(text_id1="Act{}_ts", num_act=num_activity),
                         className='row'),

                # seventh row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='ta1', children='Torque-angle'),
                          html.P(id='ta2', children='Desr motor t/a after g', style={"color": "red", "font-size": 10}),
                          html.P(id='ta4', children='Actual motor t/a after g (J)', style={"color": "yellow", "font-size": 10})
                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_ts_ta_graphs(text_id1="Act{}_ta", num_act=num_activity),
                         className='row'),

                # seventh.5 row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='tt1', children='Torque-time'),
                          html.P(id='tt2', children='T desired', style={"color": "red", "font-size": 12}),
                          html.P(id='tt4', children='T actual (J)', style={"color": "yellow", "font-size": 12})
                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_ts_ta_graphs(text_id1="Act{}_tt", num_act=num_activity),
                         className='row'),

                # eighth row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='power_eff1', children='Efficiency'),
                          html.P(id='power_eff2', children='P Mechanical', style={"color": "yellow"}),
                          html.P(id='power_eff3', children='P Electrical', style={"color": "red"})
                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_ts_ta_graphs(text_id1="Act{}_powerEff", num_act=num_activity),
                         className='row'),

                # ninth row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='voltage_current', children='Inputs   ')
                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_ts_ta_graphs(text_id1="Act{}_vc", num_act=num_activity),
                         className='row')
            ])
        ]),

        # right-side column

    ])

    # Callbacks
    # ------------------------------------------------------------------------------
    # Connect the Plotly graphs with Dash Components
    output_ts = [Output(component_id='Act{}_ts'.format(i), component_property='figure') for i in range(num_activity)]
    output_ta = [Output(component_id='Act{}_ta'.format(i), component_property='figure') for i in range(num_activity)]
    output_powerEff = [Output(component_id='Act{}_powerEff'.format(i), component_property='figure') for i in range(num_activity)]
    output_vc = [Output(component_id='Act{}_vc'.format(i), component_property='figure') for i in range(num_activity)]
    output_tt = [Output(component_id='Act{}_tt'.format(i), component_property='figure') for i in range(num_activity)]
    output_list = output_ts + output_ta + output_powerEff + output_vc + output_tt

    input_list = [Input(component_id='Combination', component_property='value'),
         Input(component_id='rating_slider1', component_property='value'),
         Input(component_id='rating_slider2', component_property='value')
         ]

    @app.callback(output_list, input_list)
    def update_graph(comb, user_torque_rating, user_speed_rating):
        filtered_comb = [x for x in ranked_comb_info if
                         x["T_rating"] >= float(user_torque_rating) and x["V_rating"] >= float(user_speed_rating)]
        comb_i = int(comb[1:])
        motor = motor_catalog.loc[motor_catalog['ID'] == filtered_comb[comb_i]["motor_id"]]
        gear = gear_catalog.loc[gear_catalog['ID'] == filtered_comb[comb_i]["gear_id"]]
        stiffness = filtered_comb[comb_i]["stiffness"]

        for i in range(num_activity):
            actuator.initialize()
            actuator.gather_info(stiffness, gear, motor,
                                 human_data.torque_data[i]["Data"], human_data.angle_data[i]["Data"],
                                 human_data.angle_data[i]["Time"])
            get_dash_plots(actuator)


        global fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12, fig13, fig14
        global Motor_i_prev
        global Gear_i_prev
        global Stiff_i_prev
        global Ass1_i_prev, Ass2_i_prev, Ass3_i_prev, Ass4_i_prev, Ass5_i_prev, Ass6_i_prev, Ass7_i_prev

        # TODO: Add reflected inertia?

        return [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10]

    return app

def get_dash_plots(actuator):
    pass


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app = generate_app_layout()
    app.run_server(debug=True)
