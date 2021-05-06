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

Num_rating = 6
Slider_length = 220
Fig_width = 240
Fig_height = 150
Performance_metrics = ["energy", "stiffness", "gear_name", "motor_name", "T_rating", "V_rating",
                       'U_rating', 'I_rating', 'motor_dia', 'motor_length']

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


def generate_graph(base_id1=None, base_id2=None, num_act=None, settings=None):
    all_graphs = []
    for i in range(num_act):
        graph_pair = html.Div(children=[
            dcc.Graph(id=base_id1.format(i+1), figure={}, style={"width": Fig_width, "height": Fig_height}),
            dcc.Graph(id=base_id2.format(i+1), figure={}, style={"width": Fig_width, "height": Fig_height})
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': settings["margin_left"], 'margin-top': '1vw'})
        all_graphs.append(graph_pair)

    return all_graphs


def generate_text_slide_bar(text_id=None, slider_id=None, stat_id=None, num_rating=1, max_ratings=None):
    all_comp = []
    default_value = [max_ratings["T_rating"], max_ratings["V_rating"], max_ratings["U_rating"], max_ratings["I_rating"], 100, 80]
    all_min = [0, 0, 0, 0, 10, 10]
    all_max = [max_ratings["T_rating"], max_ratings["V_rating"], max_ratings["U_rating"], max_ratings["I_rating"], 120, 120]
    all_step = [max_ratings["T_rating"] / 100, max_ratings["V_rating"] / 100, max_ratings["U_rating"] / 100, max_ratings["I_rating"] / 100, 10, 10]
    activity_titles = ['Torque rating', 'Speed rating', 'U_rating', 'I_rating', 'Motor dia', 'Motor len']
    for i in range(num_rating):
        single_comp = html.Div(children=[
            html.P(id=text_id.format(i+1), children=activity_titles[i]),
            dcc.Slider(id=slider_id.format(i+1),
                       min=all_min[i],
                       max=all_max[i],
                       step=all_step[i],
                       marks={0: "0",
                              all_max[i]: "{:.2f}".format(all_max[i])},
                       value=default_value[i],
                       ),
            html.Div(id=stat_id.format(i+1))

        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw', 'margin-right': '1vw',
                  'margin-top': '1vw', "width": Slider_length})
        all_comp.append(single_comp)

    return all_comp


def generate_activity_text(text_id=None, activity_titles=None, num_act=1):
    all_comp = []
    for i in range(num_act):
        single_comp = html.Div(children=[
            html.P(id=text_id.format(i + 1), children=activity_titles[i])
        ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '1vw', 'margin-right': '1vw',
                  'margin-top': '1vw', "width": Slider_length})
        all_comp.append(single_comp)

    return all_comp


def generate_performance_graphs(text_id1=None, num_act=1, settings=None):
    all_comp = []
    for i in range(num_act):
        single_comp = html.Div(children=[
              dcc.Graph(id=text_id1.format(i+1), figure={},
                        style={"width": Fig_width, "height": Fig_height})
          ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': settings["margin_left"],
                    'margin-top': '1vw'})
        all_comp.append(single_comp)

    return all_comp


def generate_table(text_id1=None, data=None):
    single_comp = dash_table.DataTable(
        id=text_id1,
        columns=[{"name": i, "id": i} for i in Performance_metrics],
        data=data.to_dict("record"),
        style_cell={
            'backgroundColor': My_settings["Paper_color"],
            'color': "#f3f5f4"})

    return single_comp


def generate_app_layout(human_data, table_data, max_ratings):
    """ Generate app layout """
    num_activity = len(human_data.weights)
    external_stylesheets = ['./assets/my_template.css']
    dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    dash_app.layout = html.Div(children=[
        # left-side column
        html.Div(style={'display': 'inline-block', 'background-color': '#192444', 'vertical-align': 'top',
                        'margin-left': '1vw', 'margin-right': '1vw', 'margin-top': '1vw'},
                 children=[
            html.Div(style={'background-color': '#192444'},
                     children=[

                # 0th row
                html.Div(children=[
                    html.P(id = 'text0', children='Actuator optimization')
                ], className='row', style={'fontColor': 'white'}),

                # first row
                html.Div(children=[
                    html.Br()] + generate_activity_text(text_id="act_title{}", activity_titles=human_data.angle_files,
                                                        num_act=num_activity),
                    className='row', style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '7vw',
                                            'margin-right': '3vw', 'margin-top': '1vw'}),

                # 2th row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='ts1', children='Torque-speed'),
                          html.P(id='ts2', children='Desired', style={"color": "red"}),
                          html.P(id='ts3', children='Actual', style={"color": My_settings["Active_color"]})],
                               style={'display': 'inline-block', 'vertical-align': 'top',
                                      'margin-left': My_settings["margin_left"], 'margin-top': '1vw'})] + generate_performance_graphs(text_id1="Act{}_ts", num_act=num_activity, settings=My_settings), className='row'),

                # seventh row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='ta1', children='Torque-angle'),
                          html.P(id='ta2', children='Desr motor t/a after g', style={"color": "red", "font-size": 10}),
                          html.P(id='ta4', children='Actual motor t/a after g (J)', style={"color": "yellow", "font-size": 10})
                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_performance_graphs(text_id1="Act{}_tt", num_act=num_activity, settings=My_settings),
                         className='row'),

                # eighth row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='power_eff1', children='Efficiency'),
                          html.P(id='power_eff2', children='P Mechanical', style={"color": "yellow"}),
                          html.P(id='power_eff3', children='P Electrical', style={"color": "red"})
                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_performance_graphs(text_id1="Act{}_powerEff", num_act=num_activity, settings=My_settings),
                         className='row'),

                # ninth row
                html.Div(children=[
                      html.Div(children=[
                          html.P(id='voltage_current', children='Inputs   ')
                      ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': My_settings["margin_left"],
                                'margin-top': '1vw'})] + generate_performance_graphs(text_id1="Act{}_vc", num_act=num_activity, settings=My_settings),
                         className='row')
            ])
        ]),

        # right-side column
        html.Div(style={'display': 'inline-block', 'background-color': '#192444', 'vertical-align': 'top',
                        'margin-left': '1vw', 'margin-right': '1vw', 'margin-top': '3vw'},
                 children=[
                     html.Div(children=[html.Br()] + [html.Div(children=[
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
                                      value="C1",
                                      style={"color": "#212121"}),
                     ], style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw',
                               'margin-top': '1vw'})]
                                       + generate_text_slide_bar(text_id="rating_title{}", slider_id="rating_slider{}",
                                                                 stat_id="rating_slider_output_container{}",
                                                                 num_rating=Num_rating, max_ratings=max_ratings), className='row',
                              style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '7vw',
                                     'margin-right': '3vw', 'margin-top': '1vw'}),

                     html.Div(style={'background-color': '#192444'},
                              children=[
                                  html.P(id='table_title2', children='Gear-list'),
                                  generate_table(text_id1="filtered_comb_table", data=table_data)
                              ])
                 ]),
    ])

    # Callback input outputs
    fig_name_format = ['Act{}_ts', 'Act{}_tt', 'Act{}_powerEff', 'Act{}_vc']
    graph_output = []
    for act_i in range(num_activity):
        for fig_name in fig_name_format:
            graph_output.append(Output(component_id=fig_name.format(act_i+1), component_property='figure'))

    graph_input = [Input(component_id='Combination', component_property='value'),
                   Input(component_id='rating_slider1', component_property='value'),
                   Input(component_id='rating_slider2', component_property='value'),
                   Input(component_id='rating_slider3', component_property='value'),
                   Input(component_id='rating_slider4', component_property='value'),
                   Input(component_id='rating_slider5', component_property='value'),
                   Input(component_id='rating_slider6', component_property='value')]

    datatable_input = [
                  Input(component_id='rating_slider1', component_property='value'),
                  Input(component_id='rating_slider2', component_property='value'),
                  Input(component_id='rating_slider3', component_property='value'),
                  Input(component_id='rating_slider4', component_property='value'),
                  Input(component_id='rating_slider5', component_property='value'),
                  Input(component_id='rating_slider6', component_property='value')]

    datatable_output = [
        Output(component_id='filtered_comb_table', component_property='data')]

    stat_output = [Output(component_id='rating_slider_output_container1', component_property='children'),
                   Output(component_id='rating_slider_output_container2', component_property='children'),
                   Output(component_id='rating_slider_output_container3', component_property='children'),
                   Output(component_id='rating_slider_output_container4', component_property='children'),
                   Output(component_id='rating_slider_output_container5', component_property='children'),
                   Output(component_id='rating_slider_output_container6', component_property='children')]

    return dash_app, graph_output, graph_input, datatable_output, datatable_input, stat_output


def get_dash_plots(actuator, motor, settings):
    """ Generate all performance plots for each activity"""
    ts_fig = generate_ts_fig(actuator, motor, settings)
    torque_fig = generate_torque_fig(actuator, motor, settings)
    power_fig = generate_power_fig(actuator, motor, settings)
    input_fig = generate_input_fig(actuator, motor, settings)

    return ts_fig, torque_fig, power_fig, input_fig


def generate_ts_fig(actuator, motor, settings):
    """ Speed-torque graph on motor side """
    n0max = actuator.params.v_limit * motor["kn"]  # no-load speed at maximum allowed voltage
    Mhmax = n0max / motor["gradient"]  # corresponding stall torque to n0max
    ts_fig = px.line(None, x=actuator.des_motor_torque,
                     y=actuator.des_motor_speed, color_discrete_sequence=["red"])

    ts_fig.add_trace(go.Scatter(x=actuator.actual_motor_torque, y=actuator.actual_motor_speed,
                                mode='lines',
                                line=dict(color=settings["Active_color"], dash='dash')))
    ts_fig.add_trace(go.Scatter(x=[0, Mhmax, 0, -Mhmax, 0], y=[n0max, 0, -n0max, 0, n0max],
                                mode='lines',
                                line=dict(color=settings["Active_color"], dash='dash')))
    ts_fig.update_layout(
        margin=dict(
            l=5,
            r=5,
            b=1,
            t=1),
        yaxis_title="Motor speed (rpm)",
        xaxis_title="Motor torque (Nm)",
        plot_bgcolor=settings["Plot_color"],
        paper_bgcolor=settings['Paper_color'],
        font_color=settings['Font_color'],
        showlegend=False
    )
    ts_fig.update_xaxes(showline=True, linewidth=1, linecolor=settings["grid_color"], gridcolor=settings["grid_color"])
    ts_fig.update_yaxes(showline=True, linewidth=1, linecolor=settings["grid_color"], gridcolor=settings["grid_color"])
    return ts_fig


def generate_torque_fig(actuator, motor, settings):
    """ Actual output torque vs desired output torque """
    normalized_time = actuator.time_series / actuator.time_series.iloc[-1] * 100   # one cycle 0-100%
    torque_fig = px.line(None, x=normalized_time, y=actuator.des_output_torque, color_discrete_sequence=["red"])
    torque_fig.add_trace(go.Scatter(x=normalized_time, y=actuator.actual_output_torque, mode='lines',
                                    line=dict(color="yellow", dash='dot')), secondary_y=False)
    torque_fig.update_layout(
        margin=dict(
            l=5,
            r=5,
            b=1,
            t=1),
        showlegend=False,
        xaxis_title="Cycle (%)",
        yaxis_title="Torque (Nm)",
        plot_bgcolor=settings["Plot_color"],
        paper_bgcolor=settings['Paper_color'],
        font_color=settings['Font_color']
    )
    torque_fig.update_xaxes(showline=True, linewidth=1, linecolor=settings["grid_color"],
                            gridcolor=settings["grid_color"])
    torque_fig.update_yaxes(showline=True, linewidth=1, linecolor=settings["grid_color"],
                            gridcolor=settings["grid_color"])
    return torque_fig


def generate_power_fig(actuator, motor, settings):
    """ Mechanical power vs electrical power """
    normalized_time = actuator.time_series / actuator.time_series.iloc[-1] * 100  # one cycle 0-100%
    power_fig = px.line(None, x=normalized_time, y=actuator.electrical_power,
                        color_discrete_sequence=["red"])
    power_fig.add_trace(go.Scatter(x=normalized_time, y=actuator.mechanical_power,
                                   mode='lines',
                                   line=dict(color="yellow")), secondary_y=False)

    power_fig.update_layout(
        margin=dict(
            l=5,
            r=5,
            b=1,
            t=1),
        showlegend=False,
        xaxis_title="Cycle (%)",
        yaxis_title="Power (W)",
        plot_bgcolor=settings["Plot_color"],
        paper_bgcolor=settings['Paper_color'],
        font_color=settings['Font_color']
    )
    power_fig.update_xaxes(showline=True, linewidth=1, linecolor=settings["grid_color"],
                           gridcolor=settings["grid_color"])
    power_fig.update_yaxes(showline=True, linewidth=1, linecolor=settings["grid_color"],
                           gridcolor=settings["grid_color"])
    return power_fig


def generate_input_fig(actuator, motor, settings):
    """ Input voltage and current """
    normalized_time = actuator.time_series / actuator.time_series.iloc[-1] * 100
    input_fig = make_subplots(specs=[[{"secondary_y": True}]])
    input_fig.add_trace(go.Scatter(x=normalized_time, y=actuator.input_current, mode='lines',
                                   line=dict(color=settings["Active_color"])), secondary_y=False)
    input_fig.add_trace(go.Scatter(x=[0, 100], y=[motor["In"]] * 2, mode='lines',
                                   line=dict(color=settings["Active_color"], dash='dash')), secondary_y=False)
    input_fig.add_trace(go.Scatter(x=[0, 100], y=[-motor["In"]] * 2, mode='lines',
                                   line=dict(color=settings["Active_color"], dash='dash')), secondary_y=False)
    # TODO: plot nominal voltage?
    input_fig.add_trace(go.Scatter(x=normalized_time, y=actuator.input_voltage, mode='lines',
                                   line=dict(color="#FF97FF")), secondary_y=True)
    input_fig.update_layout(
        margin=dict(
            l=5,
            r=5,
            b=1,
            t=1),
        showlegend=False,
        xaxis_title="Cycle (%)",
        plot_bgcolor=settings["Plot_color"],
        paper_bgcolor=settings['Paper_color'],
        font_color=settings['Font_color']
    )
    input_fig.update_xaxes(showline=True, linewidth=1, linecolor=settings["grid_color"],
                           gridcolor=settings["grid_color"])
    input_fig.update_yaxes(title_text="Input current (A)", showline=True, linewidth=1, linecolor=settings["grid_color"],
                           gridcolor=settings["grid_color"], color=settings["Active_color"], secondary_y=False)
    input_fig.update_yaxes(title_text="Input voltage (V)", showline=True, linewidth=1, linecolor=settings["grid_color"],
                           gridcolor=settings["grid_color"], color="#FF97FF", secondary_y=True)
    return input_fig
