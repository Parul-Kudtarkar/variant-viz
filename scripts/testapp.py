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
fig = vv.initial_graph()

app.layout = html.Div(children=[

	html.H1(children='Testing'),
	html.Div(children='''
		visualize dummy data
	'''),

	dcc.Graph(
		id='example',
		figure=fig
	)
])

if __name__ == '__main__':
	app.run_server(debug=True)








