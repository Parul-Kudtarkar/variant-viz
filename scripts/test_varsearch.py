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
import urllib.request
import time

#initialize dash app object:
app = dash.Dash()

#initializae VariantViz object:
vv = VariantViz()

#initialize var_data
var_name = "rs11257655"
#var_name = "rs7903146"
with urllib.request.urlopen(vv.rsid_url(var_name)) as url:
	var_data = json.loads(url.read())
all_annotations = [key for key in var_data.keys()]

#initialize number of button clicks:
rsid_button_clicks = 0

app.layout = html.Div(children=[

	html.Div(children=[

		html.Plaintext('search rsid'),
		dcc.Input(
			id='rsid-input',
			value=var_name,
			type="text"
		),
		html.Button('update', id='rsid-button'),
		dcc.RadioItems(
			id='expand-radio',
			options = [
				{'label': "more", 'value': "more"},
				{'label': "less", 'value': "less"}
			],
			value = "more",
		),

		html.Plaintext('select annotations'),
		dcc.Dropdown(
			id='annotation-dropdown',
			#obtain options directly from var data:
			options=[{'label': anno, 'value': anno} for anno in all_annotations],
			value=[key for key in var_data.keys()],
			multi=True
		),
		html.Plaintext('select biosamples'),
		dcc.Dropdown(
			id='biosample-dropdown',
			options=[{'label': biosample, 'value': biosample} for biosample in vv.get_biosamples(var_data)],
			value=[biosample for biosample in vv.get_biosamples(var_data)],
			multi=True
		)
		#html.Div(children=[])

	], style={'columnCount': 1}),

	dcc.Graph(id='test-interactivity',figure=vv.make_graph(var_data=var_data, var_name=var_name)),


])


@app.callback(
	Output('test-interactivity', 'figure'),
	[Input('annotation-dropdown', 'value'),
	 Input('expand-radio', 'value'),
	 Input('rsid-input', 'value'),
	 Input('rsid-button', 'n_clicks'),
	 Input('biosample-dropdown', 'value')])
def update_graph(annot_value, expand_value, new_rsid, num_clicks, selected_biosamples):
	print("updating graph")
	print("biosamples:", len(selected_biosamples), selected_biosamples)
	#declare globals
	global var_name
	global var_data
	global all_annotations
	global rsid_button_clicks
	print("num_clicks:", num_clicks)
	print("rsid_button_clicks", rsid_button_clicks)
	#try to update to new rsid
	if num_clicks is not None and num_clicks == rsid_button_clicks + 1:
		rsid_button_clicks += 1
		if new_rsid != var_name:
			with urllib.request.urlopen(vv.rsid_url(new_rsid)) as url:
				u = url.read()
				if u != bytes():
					var_data = json.loads(u)
					var_name = new_rsid
					#all_annotations = [key for key in var_data.keys()]
					return vv.make_graph(var_data=var_data, var_name=var_name)
				else:
					print("not a valid rsid:", new_rsid)

	#make new dict using only checked values:
	new_data = {key:val for key, val in var_data.items() if key in annot_value}

	#expand or not?
	if expand_value == "more":
		expanded = True
	else:
		expanded = False

	return vv.make_graph(var_data=var_data, var_name=var_name, subset_data=new_data, expanded=expanded, \
		biosamples=selected_biosamples)

#update menu choices when var_name changes:
@app.callback(
	Output('annotation-dropdown', 'options'),
	[Input('rsid-input', 'value'),
	 Input('rsid-button', 'n_clicks')])
def update_dropdown(new_rsid, num_clicks):

	global rsid_button_clicks
	global all_annotations

	#if num_clicks is not None and num_clicks == rsid_button_clicks + 1:
	if num_clicks > 0:
		print("updating dropdown menu")
		print("annotations:", all_annotations)
		all_annotations = [key for key in var_data.keys()]

	return [{'label': anno, 'value': anno} for anno in all_annotations]



if __name__ == '__main__':
	app.run_server(debug=True)




