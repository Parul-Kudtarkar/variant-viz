import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff

class VariantViz:

	dummy_data = {
		"footprints": [
			"HNF4",
			"STAT",
			"PPARA",
			"TCF3"
		],
		"genes": [
			"CAMK1D",
			"OPTN",
			"CCDC3"
		],
		"ChIP": [
			"FOXA2",
			"NKX2.2"
		],
		"chrom_state": ["EnhA1"],	
	}
	dummy_name = "rs11257655"

	def generate_positions(self, var_data, var_name, vert_space=4, box_width=10, \
						   box_height=4, text_y0=100, plot_width=100, offset=20, expanded=True):
		
		#get number of annotations
		num_annotations = len(var_data.keys())
		num_sides = int(num_annotations/2)
		
		#initialize text and shape position dicts:
		text_positions = {var_name: [plot_width/2, text_y0]}
		shape_positions = {
			var_name: [
				[(plot_width/2)-box_width/2, text_y0-box_height/2],
				[(plot_width/2)+box_width/2, text_y0+box_height/2]
			]
		}
		
		for i, annotation in enumerate(var_data.keys()):
			#get x offset:
			if num_annotations % 2 == 1 and i == int(num_annotations/2)+1:
				x_offset = text_positions[var_name][0] + offset
			elif i+1 <= num_sides: 
				x_offset = text_positions[var_name][0] - offset*(i+1)
			elif i+1 > num_sides and num_annotations % 2 == 1:
				x_offset = text_positions[var_name][0] + offset*(i-int(num_annotations/2))
			else:
				x_offset = text_positions[var_name][0] + offset*((i+1)-int(num_annotations/2))
			
			#set text and shape coordinates for current annotation
			text_positions[annotation] = {"coords": [
				x_offset,
				text_y0-(2*vert_space)
			]}
			
			shape_positions[annotation] = {
				"x0": text_positions[annotation]["coords"][0] - box_width/2,
				"y0": text_positions[annotation]["coords"][1] - box_height/2,
				"x1": text_positions[annotation]["coords"][0] + box_width/2, 
				"y1": text_positions[annotation]["coords"][1] + box_height/2,
			}
			
			#set text and shape coordinates for each item in annotation:
			if expanded == True:
				for j, item in enumerate(var_data[annotation]):
					if j == 0:
						text_positions[annotation][item] = [
							text_positions[annotation]["coords"][0],
							text_positions[annotation]["coords"][1] - box_height
						]
					else:
						text_positions[annotation][item] = [
							text_positions[annotation]["coords"][0],
							text_positions[annotation][var_data[annotation][j-1]][1] - box_height
						]
					
					shape_positions[annotation][item] = [
						[text_positions[annotation][item][0] - box_width/2, text_positions[annotation][item][1] - box_height/2],
						[text_positions[annotation][item][0] + box_width/2, text_positions[annotation][item][1] + box_height/2]
					]
			
		return text_positions, shape_positions

	def generate_shapes(self, var_data, shape_positions, colors=""):
		
		shape_coords = []
		shapes = []
		for key, val in shape_positions.items():
			if type(val) != dict:
				shape_coords.append(val)
			else:
				shape_coords.append([[val['x0'], val['y0']],[val['x1'], val['y1']]])
				cur_shapes = [val[k] for k in val.keys() if k not in ['x0', 'y0', 'x1', 'y1']]
				shape_coords += cur_shapes
		
		if colors == "":
			colors = ['#888' for i in range(len(shape_coords))]
		
		for i, coords in enumerate(shape_coords):
			shapes.append({
				'type': 'rect',
				'xref': 'x',
				'yref': 'y',
				'x0': coords[0][0],
				'y0': coords[0][1],
				'x1': coords[1][0],
				'y1': coords[1][1],
				'line': {
					'color': '#888',
					'width': 2,
				},
				'fillcolor': 'rgba(55, 128, 191, 0.6)',
				'opacity': 0.5
			})
		return shapes

	def invisible_points(self, text_pos, var_name):
	
		min_coords = [i for i in text_pos[var_name]]
		max_coords = [i for i in text_pos[var_name]]
				
		for key, val in text_pos.items():
			if type(val) == dict:
				for item in val.values():
					if item != "coords":
						if item[0] > max_coords[0]:
							max_coords[0] = item[0]
						if item[0] < min_coords[0]:
							min_coords[0] = item[0]
						if item[1] > max_coords[1]:
							max_coords[1] = item[1]
						if item[1] < min_coords[1]:
							min_coords[1] = item[1]
						
		return min_coords, max_coords

	def make_graph(self, var_data=dummy_data, var_name=dummy_name, subset_data="", vert_space=4, box_width=10, \
					box_height=4, text_y0=100, plot_width=100, offset=20, expanded=True):
		
		if subset_data != "":
			text_pos, shape_pos = self.generate_positions(subset_data, var_name, expanded=expanded)
		else:
			text_pos, shape_pos = self.generate_positions(var_data, var_name, expanded=expanded)
			
		all_text_pos, all_shape_pos = self.generate_positions(var_data, var_name, expanded=True)
		min_coords, max_coords = self.invisible_points(all_text_pos, var_name)

		#initialize node and edge traces:
		node_trace = go.Scatter(
			x = [],
			y = [],
			text = [],
			mode='markers+text',
			hoverinfo='none',
			marker=dict(
				color=[],
				size=10,
				line=dict(width=10),
				opacity=0.0
			)
		)

		edge_trace = go.Scatter(
			x = [],
			y = [],
			line=dict(width=2,color='#888'),
			hoverinfo='none',
			mode='lines'		
		)
			
		#populate node information with text positions:
		for key, val in text_pos.items():
			if type(val) == dict:
				node_trace['x'].append(val['coords'][0])
				node_trace['y'].append(val['coords'][1])
				node_trace['text'].append(key)
				for item in val.keys():
					if item not in ['coords']:
						node_trace['x'].append(val[item][0])
						node_trace['y'].append(val[item][1])
						node_trace['text'].append(item)
			else:
				node_trace['x'].append(val[0])
				node_trace['y'].append(val[1])
				node_trace['text'].append(key)

		#add invisible points:
		node_trace['x'].append(min_coords[0])
		node_trace['y'].append(min_coords[1])
		node_trace['x'].append(max_coords[0])
		node_trace['y'].append(max_coords[1])
		
		#fill in edges between name and annoations:
		for key, val in text_pos.items():
			if key != var_name:
				edge_trace['x'] += [text_pos[var_name][0], text_pos[key]["coords"][0] ,None]
				edge_trace['y'] += [text_pos[var_name][1]-box_height/2, text_pos[key]["coords"][1]+box_height/2, None]
		
		layout = go.Layout(
			xaxis = dict(
				showgrid=False, 
				zeroline=False,
				showline=False,
				ticks='',
				showticklabels=False
			),
			yaxis = dict(
				showgrid=False,
				zeroline=False,
				showline=False,
				ticks='',
				showticklabels=False
			),
			showlegend=False,
		)

		layout['shapes'] = self.generate_shapes(var_data, shape_pos)

		data = [node_trace, edge_trace]
		fig = go.Figure(data=data, layout=layout)
		return fig







