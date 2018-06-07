import dash
import dash_core_components as dcc 
import dash_html_components as html
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import numpy as np
import json
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from variant_viz import VariantViz
from dash.dependencies import Input, Output

#initialize dash app object:
app = dash.Dash()

#initializae VariantViz object:
vv = VariantViz()

#placeholder for now of obtaining dataset for plotting:
#var_data = vv.dummy_data
var_data = vv.dummy_json
var_name = vv.dummy_name

app.layout = html.Div(children=[

	dcc.Graph(id='test-interactivity',figure=vv.make_graph(var_data=var_data, var_name=var_name)),

	html.Div(children=[
		dcc.Input(
			value="rsid",
			type="text"
		),
		dcc.RadioItems(
			id='expand-radio',
			options = [
				{'label': "more", 'value': "more"},
				{'label': "less", 'value': "less"}
			],
			value = "more",
		),
		dcc.Dropdown(
			id='annotation-dropdown',
			#obtain options directly from var data:
			options=[{'label': key, 'value': key} for key in var_data.keys()],
			value=[key for key in var_data.keys()],
			multi=True
		),

	], style={'columnCount': 1})

])

@app.callback(
	Output('test-interactivity', 'figure'),
	[Input('annotation-dropdown', 'value'),
	 Input('expand-radio', 'value')]
)
def update_graph(annot_value, expand_value):

	#for now use dummy data as an example of "all data" being returned from a query
	#all_data = vv.dummy_data
	all_data = vv.dummy_json

	#make new dict using only checked values:
	new_data = {key:val for key, val in all_data.items() if key in annot_value}

	#expand or not?
	if expand_value == "more":
		expanded = True
	else:
		expanded = False

	return vv.make_graph(var_data=all_data, var_name=vv.dummy_name, subset_data=new_data, expanded=expanded)

if __name__ == '__main__':
	app.run_server(debug=True)








