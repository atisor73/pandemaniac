import numpy as np
import pandas as pd

try:
    import iqplot
except:
    pass
    
import bokeh
import bokeh.io
import panel as pn
pn.extension()

import json
import networkx as nx
from . import sim_viz



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
        palette=['#cb4f70', '#1b718c', '#779e1a', '#f49044',
                '#46308d', '#2ea58e', '#e97d86', '#7e92bd',
                '#c21019', '#f56327', '#fab01d', '#026f69',
                '#750a2b', '#1b9e77', '#d95f02', '#7570b3',
                '#e7298a', '#66a61e'],
        uncolored_size=2.5,
        colored_size=4.5,
        names=None,
        layout=None,
        ):
    """
    Arguments
    -------------------------------------
    G : networkx Graph object
    seeds : list of list of seed nodes to play on G
    palette : list of strings (hex values or html names)
    uncolored_size : float, size of uncolored glyphs
    colored_size : float, size of colored glyphs
    names : list of opponent names for legend labels
    layout : string ("radial", "random", "kamada", "spectral"),
             default "spring"

    Returns :
    -------------------------------------
    Bokeh panel object displaying color cascade, with iteration and zoom control.
    """
    if layout == "radial":     layout = nx.circular_layout(G)
    elif layout == "random":   layout = nx.random_layout(G)
    elif layout == "kamada":   layout = nx.kamada_kawai_layout(G)
    elif layout == "spectral": layout = nx.spectral_layout(G)
    else:                      layout = nx.spring_layout(G)

    df = dataframer(layout)
    result, history = simulate(G, seeds)

    color_map = {k:v for k, v in zip(result.keys(), palette)}
    color_map[None] = "grey"
    print()
    size_map = {None : uncolored_size}
    for k in result.keys():
        size_map[k] = colored_size

    i_slider = pn.widgets.IntSlider(start=1, end=len(history), value=1,
                                    name="iteration", width=370)
    range_slider = pn.widgets.FloatSlider(name='zoom', width=370,
                                      start=0.10, end=2.0, value=1.1, step=0.05)
    @pn.depends(i_slider.param.value, range_slider.param.value)
    def plotter(i, z):
        z = 2.05 - z
        df_ = df
        p = bokeh.plotting.figure(title=f"iteration {i}",
                                  width=600, height=450,
                                  x_range=[-z,z],y_range=[-z, z],  )

        # iterating, update color and size of node
        labels = list(history[i-1].values())
        df_["color"] = [color_map[label] for label in labels]
        df_["size"] = [size_map[label] for label in labels]
        df_ = df_.sort_values(by=["size"])

        # creating legend
        if names==None:
            items = [(f"team {k}", [p.circle(0,0, color=f"{v}")])
                                        for k, v in color_map.items()]
        else:
            items = [(f"{list(names)[i]}", [p.circle(0,0, color=f"{kv[1]}")])
                                        for i, kv in enumerate(color_map.items())
                                        if i < len(seeds)
                                        ]
        legend = bokeh.models.Legend(items=items, location="center")
        p.add_layout(legend, 'right')

        # only plotting nodes
        p.circle(source=df_, x='x',y='y', color='color', size='size',
                 line_color="white", line_width=0.1)

        return style(p)
    return pn.Column(range_slider, i_slider, plotter)


def viz_tournament(G, players,
        palette=['#cb4f70', '#1b718c', '#779e1a', '#f49044',
                '#46308d', '#2ea58e', '#e97d86', '#7e92bd',
                '#c21019', '#f56327', '#fab01d', '#026f69',
                '#750a2b', '#1b9e77', '#d95f02', '#7570b3',
                '#e7298a', '#66a61e'],
        uncolored_size=2.5,
        colored_size=4.5,
        layout=None,
        ):
    """
    Arguments
    -------------------------------------
    G : networkx Graph object
    players : dictionary of {player names: chosen seeds}
    palette : list of strings (hex values or html names)
    uncolored_size : float, size of uncolored glyphs
    colored_size : float, size of colored glyphs
    layout : string ("radial", "random", "kamada", "spectral"),
             default "spring"

    Returns :
    -------------------------------------
    Bokeh panel object displaying color cascade, with cycle+iteration, and zoom control.
    """
    # ***************** GRAPH LAYOUT *****************
    print("graph layout... ")
    if layout == "radial":     layout = nx.circular_layout(G)
    elif layout == "random":   layout = nx.random_layout(G)
    elif layout == "kamada":   layout = nx.kamada_kawai_layout(G)
    elif layout == "spectral": layout = nx.spectral_layout(G)
    else:                      layout = nx.spring_layout(G)

    df = dataframer(layout)
    
    # ********* SIMULATING 50 CYCLES LAYOUT *********
    print("simulating... ")
    names = list(players.keys())
    all_seeds = list(players.values())
    
    N_CYCLES = 50
    results, histories = [], []
    for cycle in range(N_CYCLES):
        seeds = [team[cycle] for team in all_seeds]
        result, history = simulate(G, seeds)
        results.append(result)
        histories.append(history)
    
    
    # ****************** PLOTTING ******************
    print("plotting... ")
    color_map = {k:v for k, v in zip(result.keys(), palette)}
    color_map[None] = "grey"
    print()
    size_map = {None : uncolored_size}
    for k in result.keys():
        size_map[k] = colored_size

    cycle_selector = pn.widgets.Select(name="cycle", width=90,
        options=list(np.arange(N_CYCLES)), value=0)
    i_slider = pn.widgets.IntSlider(start=1, end=len(histories[0]), value=1,
                                    name="iteration", width=290)
    range_slider = pn.widgets.FloatSlider(name='zoom', width=400,
                                      start=0.10, end=2.0, value=1.1, step=0.05)
    
    @pn.depends(cycle_selector.param.value, watch=True)
    def update_i_end(cycle):
        i_slider.end = len(histories[cycle])
        
    @pn.depends(cycle_selector.param.value, i_slider.param.value, range_slider.param.value)
    def plotter(cycle, i, z):
        result, history = results[cycle], histories[cycle]
        z = 2.05 - z
        df_ = df
        p = bokeh.plotting.figure(title=f"iteration {i}",
                                  width=600, height=450,
                                  x_range=[-z,z],y_range=[-z, z],  )
        
        max_i = len(history)-1
        _index = max_i if i > max_i else i-1 
        
        # iterating, update color and size of node
        labels = list(history[_index].values())
        df_["color"] = [color_map[label] for label in labels]
        df_["size"] = [size_map[label] for label in labels]
        df_ = df_.sort_values(by=["size"])

        # creating legend
        if names==None:
            items = [(f"team {k}", [p.circle(0,0, color=f"{v}")])
                                        for k, v in color_map.items()]
        else:
            items = [(f"{list(names)[i]}", [p.circle(0,0, color=f"{kv[1]}")])
                                        for i, kv in enumerate(color_map.items())
                                        if i < len(seeds)
                                        ]
        legend = bokeh.models.Legend(items=items, location="center")
        p.add_layout(legend, 'right')

        # only plotting nodes
        p.circle(source=df_, x='x',y='y', color='color', size='size',
                 line_color="white", line_width=0.1)
        p.toolbar_location="below"
        return style(p)
    return pn.Column(range_slider, pn.Row(cycle_selector, i_slider), plotter)

def ecdf_rank(opponents, my_rank,
              palette=['#cb4f70', '#1b718c', '#779e1a', '#f49044',
                      '#46308d', '#2ea58e', '#e97d86', '#7e92bd',
                      '#c21019', '#f56327', '#fab01d', '#026f69',
                      '#750a2b', '#1b9e77', '#d95f02', '#7570b3',
                      '#e7298a', '#66a61e'],
              x_range=None, title=None
              ):
    """
    Plot ECDF of everyone's nodal choices.
    Note that this rank might not reflect their method of selection,
    this is mainly for diagnostic purposes.

    Arguments
    -------------------------------------
    opponents : dictionary loaded in from json file {team name : list of list of seeds}
    my_rank : dictionary of {node : rank}, node in graph, and integer rank

    Returns
    -------------------------------------
    ECDF of selected nodes with control of iterations over 50.
    """
    iteration_slider = pn.widgets.IntSlider(start=1, end=50, value=1, name="iteration",width=785)
    @pn.depends(iteration_slider.param.value)
    def ecdf_plotter(iteration=1):
        p = bokeh.plotting.figure(height=400, width=1000, title=title, x_range=x_range)
        for a, _ in enumerate(opponents.items()):
            k, v = _
            iqplot.ecdf(data=np.array([my_rank[i] for i in v[iteration-1]]),
                        p=p, style='staircase', palette=[palette[a]],legend_label=k)

            others = set()
            for _k, _v in opponents.items():
                if _k != k:
                    _data = np.array([my_rank[i] for i in _v[iteration-1]])
                    for val in _data:
                        others.add(val)
            data = np.array([my_rank[i] for i in v[iteration-1]])
            xs, ys = np.sort(data), np.arange(1, len(data)+1) / len(data)
            d_plot = dict(zip(xs, ys))
            keep_xs = [val for val in xs if val not in others]
            keep_ys = [d_plot[x] for x in keep_xs]
            p.circle(x=keep_xs, y=keep_ys,
                fill_alpha=0.0, color=palette[a], size=8,
                line_width=2.0, legend_label=k)
        return p
    return pn.Column(iteration_slider, ecdf_plotter)
