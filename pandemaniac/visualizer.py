import numpy as np
import pandas as pd

import bokeh
import bokeh.io
import panel as pn
pn.extension()

import json
import networkx as nx
import sim_viz


def style(p):
    p.title.text_font="Helvetica"
    p.title.text_font_size="16px"
    p.title.align="center"
    p.xaxis.axis_label_text_font="Helvetica"
    p.yaxis.axis_label_text_font="Helvetica"

    p.xaxis.axis_label_text_font_size="13px"
    p.yaxis.axis_label_text_font_size="13px"
    p.xaxis.axis_label_text_font_style = "normal"
    p.yaxis.axis_label_text_font_style = "normal"
    p.background_fill_alpha = 0

    p.xaxis.visible,p.yaxis.visible = False, False
    p.xgrid.grid_line_color,p.ygrid.grid_line_color = None, None
    return p

def simulate(graph, l_seed):
    """ Runs Simulation from sim.py
        --------------------------------------------
        graph : either dictionary or nx Graph object
        l_seed : list of seed nodes
    """
    if type(graph) == nx.classes.graph.Graph:
        graph = nx.to_dict_of_lists(graph)  # change graph object to dictionary

    d_seed = dict(zip([f"{i}" for i, _ in enumerate(l_seed)], l_seed))

    return sim_viz.run(graph, d_seed)

def read_opponents(file_path):
    with open(file_path, 'r') as j:
        _opponents = json.loads(j.read())
    opp_names = list(_opponents.keys())
#     opp_names.remove('Nooodles')
    _ = [_opponents[opp] for opp in opp_names]
    opponents = dict(zip(opp_names, _))
    return opponents

def dataframer(positions):
    d = {'nodes':[], 'x':[], 'y':[]}
    for k, v in positions.items():
        d['nodes'].append(k)
        d['x'].append(v[0])
        d['y'].append(v[1])
    df = pd.DataFrame(d)
    return df


def viz(G, seeds,
        palette=["#f49044", "#cb4f70", "#779e1a", "#1b718c"],
        uncolored_size=2.5,
        colored_size=4.5
        ):
    """
    Arguments
    -------------------------------------
    G : networkx Graph object
    seeds : list of list of seed nodes to play on G
    palette : list of strings (hex values or html names)
    uncolored_size : float, size of uncolored glyphs
    colored_size : float, size of colored glyphs

    Returns :
    -------------------------------------
    Bokeh panel object displaying color cascade, with iteration and zoom control.
    """
    df = dataframer(nx.spring_layout(G))
    result, history = simulate(G, seeds)

    color_map = {k:v for k, v in zip(result.keys(), palette)}
    color_map[None] = "grey"

    size_map = {None : uncolored_size}
    for k in result.keys():
        size_map[k] = colored_size

    i_slider = pn.widgets.IntSlider(start=0, end=len(history)-1, value=0,
                                    name="iteration", width=400)
    range_slider = pn.widgets.FloatSlider(name='zoom', width=400,
                                      start=0.1, end=1.5, value=0.4, step=0.05)
    @pn.depends(i_slider.param.value, range_slider.param.value)
    def plotter(i=1, z=1.5):
        df_ = df
        p = bokeh.plotting.figure(title=f"iteration {i+1}",
                                  width=600, height=450,
                                  x_range=[-z,z],y_range=[-z, z],  )

        # iterating, update color and size of node
        labels = list(history[i].values())
        df_["color"] = [color_map[label] for label in labels]
        df_["size"] = [size_map[label] for label in labels]
        df_ = df_.sort_values(by=["size"])

        # only plotting nodes
        p.circle(source=df_, x='x',y='y', color='color', size='size',
                 line_color="white", line_width=0.1)

        # creating legend
        items = [(f"team {k}", [p.circle(0,0, color=f"{v}")]) for k, v in color_map.items()]
        legend = bokeh.models.Legend(items=items, location="center")
        p.add_layout(legend, 'right')

        return style(p)
    return pn.Column(range_slider, i_slider, plotter)
