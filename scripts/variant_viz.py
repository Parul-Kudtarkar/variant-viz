import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import json
import numpy as np
from copy import deepcopy

class VariantViz:

	dummy_name = "rs11257655"
	dummy_data = {
		"chromatin_state": [
			{
				"state": "enhA1",
				"biosample_term_name": "skeletal muscle"
			},
			{
				"state": "promoter",
				"biosample_term_name": "islet"
			}
		],
		"footprints": [
			{
				"footprint": "HNF4",
				"biosample_term_name": "islet"
			},
			{
				"footprint": "PPARA",
				"biosample_term_name": "islet",
			},
			{
				"footprint": "TCF3",
				"biosample_term_name": "hippocampus"
			},
			{
				"footprint": "STAT",
				"biosample_term_name": "skeletal muscle"
			}
			
		],

		"ChIP": [
			{
				"target": "FOXA2",
				"biosample_term_name": "islet",
			},
			{
				"target": "NKX2.2",
				"biosample_term_name": "skeletal muscle"
			},
			{
				"target": "CTCF",
				"biosample_term_name": "islet"
			},
		]
		
	}

	#get all biosample_term_names in var_data:
	def get_biosamples(self, var_data):
		biosamples = []
		for anno in var_data.keys():
			for item in var_data[anno]:
				biosamples.append(item["biosample_term_name"])

		return list(set(biosamples))

	def generate_positions(self, var_data=dummy_data, var_name=dummy_name, vert_space=4, box_width=10, \
						   box_height=4, text_y0=100, plot_width=100, offset=20, expanded=True, biosamples=""):
		
		#sort items within var_data (should I do this outside of this function??):
		var_data = {anno: sorted(items, key=lambda x: x['biosample_term_name']) for anno, items in var_data.items()}

		#get number of annotations
		num_annotations = len(var_data.keys())
		num_sides = int(num_annotations/2)
		
		positions = {
			var_name: {
				"text-coords": [plot_width/2, text_y0],
				"shape-coords": [
					[(plot_width/2)-box_width/2, text_y0-box_height/2],
					[(plot_width/2)+box_width/2, text_y0+box_height/2]
				],
				"annotations": {key: {"items": val} for key, val in var_data.items()}
			}
		}
		
		for i, anno in enumerate(positions[var_name]["annotations"].keys()):
			#get x offset:
			if num_annotations % 2 == 1 and i == int(num_annotations/2)+1:
				x_offset = positions[var_name]["text-coords"][0] + offset
			elif i+1 <= num_sides: 
				x_offset = positions[var_name]["text-coords"][0] - offset*(i+1)
			elif i+1 > num_sides and num_annotations % 2 == 1:
				x_offset = positions[var_name]["text-coords"][0] + offset*(i-int(num_annotations/2))
			else:
				x_offset = positions[var_name]["text-coords"][0] + offset*((i+1)-int(num_annotations/2))
				
			#set text coordinates for this annotation
			positions[var_name]["annotations"][anno]["text-coords"] = [
				x_offset, 
				text_y0-(2*vert_space)
			]
			
			#set shape coordinates for this annotation
			positions[var_name]["annotations"][anno]["shape-coords"] = [
				[
					positions[var_name]["annotations"][anno]["text-coords"][0]-box_width/2,
					positions[var_name]["annotations"][anno]["text-coords"][1]-box_height/2
				],
				[
					positions[var_name]["annotations"][anno]["text-coords"][0]+box_width/2,
					positions[var_name]["annotations"][anno]["text-coords"][1]+box_height/2
				]
			]
			
			#create lists to keep track of text-coords and shape-coords 
			cur_text_coords = []
			cur_shape_coords = []
			last_biosample = ""

			if expanded == True:
				for j, item in enumerate(positions[var_name]["annotations"][anno]["items"]):
					cur_biosample = item['biosample_term_name']
					if item["biosample_term_name"] in biosamples:
						#text coordinates
						if len(cur_text_coords) == 0:
							item["text-coords"] = [
								positions[var_name]["annotations"][anno]["text-coords"][0],
								positions[var_name]["annotations"][anno]["text-coords"][1] - box_height
							]
						else:
							item["text-coords"] = [
								cur_text_coords[-1][0],
								cur_text_coords[-1][1] - box_height
							]
						cur_text_coords.append(item["text-coords"])

						#shape coordinates
						if j==0 or cur_biosample != last_biosample:
							cur_shape_coords = [
							[item["text-coords"][0]-box_width/2, item["text-coords"][1]-box_height/2],
							[item["text-coords"][0]+box_width/2, item["text-coords"][1]+box_height/2]
						]
						elif cur_biosample == last_biosample:
							cur_shape_coords[0][1] -= box_height
						item["shape-coords"] = cur_shape_coords
						last_biosample = cur_biosample

					else:
						print(item["biosample_term_name"], "biosample_term_name not found")
						if "text-coords" in item.keys():
							item.pop("text-coords")
							item.pop("shape-coords")
					
		return positions

	def generate_shapes(self, positions, var_name, colors="", expanded=True):
		
		shape_coords = [positions[var_name]["shape-coords"]]
		shapes = []
		
		for anno in positions[var_name]["annotations"].keys():
			shape_coords.append(positions[var_name]["annotations"][anno]["shape-coords"])
			if expanded == True:
				last_biosample = ""
				for item in positions[var_name]["annotations"][anno]["items"]:
					cur_biosample = item["biosample_term_name"]
					if cur_biosample != last_biosample and "shape-coords" in item.keys():
						shape_coords.append(item["shape-coords"])
					last_biosample = cur_biosample

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

	def invisible_points(self, positions, var_name):
		
		min_coords = [i for i in positions[var_name]["text-coords"]]
		max_coords = [i for i in positions[var_name]["text-coords"]]
		
		for anno, info in positions[var_name]["annotations"].items():
			if info["text-coords"][0] > max_coords[0]:
				max_coords[0] = info["text-coords"][0]
			elif info["text-coords"][0] < min_coords[0]:
				min_coords[0] = info["text-coords"][0]
			if info["text-coords"][1] > max_coords[1]:
				max_coords[1] = info["text-coords"][1]
			elif info["text-coords"][1] < min_coords[1]:
				min_coords[1] = info["text-coords"][1]
			
			for item in positions[var_name]["annotations"][anno]["items"]:
				if "text-coords" in item.keys():
					if item["text-coords"][0] > max_coords[0]:
						max_coords[0] = item["text-coords"][0]
					elif item["text-coords"][0] < min_coords[0]:
						min_coords[0] = item["text-coords"][0]
					if item["text-coords"][1] > max_coords[1]:
						max_coords[1] = item["text-coords"][1]
					elif item["text-coords"][1] < min_coords[1]:
						min_coords[1] = item["text-coords"][1]

		#extend invisible x points to avoid text cutoffs
		min_coords[0] -= 25
		max_coords[0] += 25
	
		return min_coords, max_coords

	#finds the longest label name
	def max_text_len(self, var_data):
		
		max_text_len = 0
		
		for anno, items in var_data.items():
			if len(anno) > max_text_len:
				max_text_len = len(anno)
			for item in items:
				text = item["biosample_term_name"] + ": "
				if "state" in item.keys():
					text += "state"
				elif "target" in item.keys():
					text += "target"
				elif "footprint" in item.keys():
					text += "footprint"
				if len(text) > max_text_len:
					max_text_len = len(text)
		
		return max_text_len

	def rsid_url(self, rsid):
		return "https://www.t2depigenome.org/peak_metadata/region=%s&genome=GRCh37/peak_metadata.tsv" % rsid

	def make_graph(self, var_data=dummy_data, var_name=dummy_name, subset_data="", vert_space=4, box_width=25, \
				box_height=4, text_y0=100, plot_width=1000, plot_height=500, offset=20, expanded=True, biosamples=""):

		if biosamples == "":
			biosamples = self.get_biosamples(var_data)

		#get max number of items in one annotation
		max_items = max([len([item for item in var_data[anno] if item["biosample_term_name"] in self.get_biosamples(var_data)]) for anno in var_data.keys()])
		num_annotations = len(var_data.keys())
	
		#compute plot width and height:
		plot_height = 350 * np.log(max_items)
		plot_width = 1200 * np.log(num_annotations)
		box_width = self.max_text_len(var_data)
		offset = box_width + 5

		all_positions = self.generate_positions(var_data, var_name, expanded=expanded, box_height=box_height, \
								   box_width=box_width, offset=offset, text_y0=text_y0, biosamples=biosamples)
		if subset_data == "":
			positions = self.generate_positions(var_data, var_name, expanded=expanded, box_height=box_height, \
								   box_width=box_width, offset=offset, text_y0=text_y0, biosamples=biosamples)
		else:
			positions = self.generate_positions(subset_data, var_name, expanded=expanded, box_height=box_height, \
								   box_width=box_width, offset=offset, text_y0=text_y0, biosamples=biosamples)

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
		node_trace['x'].append(positions[var_name]["text-coords"][0])
		node_trace['y'].append(positions[var_name]["text-coords"][1])
		node_trace['text'].append(var_name)
		for anno in positions[var_name]["annotations"].keys():
			node_trace['x'].append(positions[var_name]["annotations"][anno]["text-coords"][0])
			node_trace['y'].append(positions[var_name]["annotations"][anno]["text-coords"][1])
			node_trace['text'].append(anno)
			last_biosample = ""
			if expanded == True:
				for item in positions[var_name]["annotations"][anno]["items"]:
					if item["biosample_term_name"] in biosamples:
						cur_biosample = item["biosample_term_name"]
						node_trace['x'].append(item["text-coords"][0])
						node_trace['y'].append(item["text-coords"][1])
						'''
						if cur_biosample != last_biosample:
							text = item["biosample_term_name"] + ":<br>"
						else:
							text = ""
						'''
						text = item['biosample_term_name'] + ": "
						if "state" in item.keys():
							text += item['state']
						elif "footprint" in item.keys():
							text += item['footprint']
						elif "target" in item.keys():
							text += item['target']
						node_trace['text'].append(text)
						last_biosample = cur_biosample

		#fill in edges between variant name and annotation names:
		for anno in positions[var_name]["annotations"].keys():
			edge_trace['x'] += [positions[var_name]["text-coords"][0], positions[var_name]["annotations"][anno]["text-coords"][0], None]
			edge_trace['y'] += [positions[var_name]["shape-coords"][0][1], positions[var_name]["annotations"][anno]["shape-coords"][1][1], None]
		
		#add invisible points:
		
		min_coords, max_coords = self.invisible_points(all_positions, var_name)
		node_trace['x'].append(min_coords[0])
		node_trace['y'].append(min_coords[1])
		node_trace['x'].append(max_coords[0])
		node_trace['y'].append(max_coords[1])
		
		layout = go.Layout(
			width=plot_width,
			height=plot_height,
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

		layout['shapes'] = self.generate_shapes(positions, var_name, expanded=expanded)

		data = [node_trace, edge_trace]
		fig = go.Figure(data=data, layout=layout)
		return fig
		











