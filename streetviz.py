"""
Installation
"""
import osmnx as ox
"""
osmnx is the only dependency that requires special care
You will want to follow the recommendations here
https://osmnx.readthedocs.io/en/stable/installation.html
To do that, you need to install conda
https://www.anaconda.com/docs/getting-started/miniconda/main

if any other python requirements are missing after the osmnx
conda environment is configured, then they can be installed
using `pip install`
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point
from datetime import datetime
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from sys import argv

class Map():
    def __init__(self, file_in):
        self.file_in = file_in
        """
        The input file sets one variable on each line using the = operator.
        The street network is fetched according to instructions specified
        by the CENTER and RADIUS variables. The CENTER is latitude,longitude
        and the RADIUS is meters, eg,

        CENTER=33.88777,-118.18545
        RADIUS=1000

        A square area is fetched, with the sides RADIUS meters from CENTER
        at their closest points.

        The data is cached locally and repeat queries are usually much faster.
        Additional parameters to include in the input file are listed below.
        All are optional.

        An OUTPUT file should be given, which is a filepath to write to.
        It should be a format that matplotlib can write, like .png
        For example,

        OUTPUT=figures/map1.png

        where the `figures` directory should already exist.
        """
        self.read_in()

    def read_in(self):
        f=open(self.file_in, 'r')
        # The input file can contain comments beginning //
        lines = [line.split('//')[0] for line in f.readlines()]
        # A line should have a variable and a value separated by =
        lines = list(filter(lambda line: '=' in line, lines))
        pairs = [tuple([item.strip() for item in line.split('=')]) for line in lines]
        # Defaults for all parameters
        self.file_out=None
        self.bearings_out=None
        self.legend=False
        self.scale=False
        self.speeds=True
        self.street_colors='gray'
        self.street_color='white'
        self.bgcolor='black'
        self.center=None
        self.crs=None
        self.radius=1000
        self.network_type='all'
        self.figsize=5
        self.street_width=2
        for pair in pairs: self.setVal(pair)
        
    def setVal(self,pair):
        if pair[0] == 'OUTPUT': self.file_out=pair[1]
        if pair[0] == 'BEARINGS': self.bearings_out=pair[1]
        """
        LEGEND and SCALE: set to 1 to include these items
        """
        if pair[0] == 'LEGEND': self.legend=bool(int(pair[1]))
        if pair[0] == 'SCALE': self.scale=bool(int(pair[1]))
        """
        *COLORS: set these variables to valid matplotlib colormap names
        """
        if pair[0] == 'STREET_COLORS':
            self.speeds=True
            self.street_colors=pair[1]
        """
        *COLOR: set these variables to valid matplotlib colors
        """
        if pair[0] == 'STREET_COLOR':
            self.speeds=False
            self.street_color=pair[1]
        if pair[0] == 'BACKGROUND_COLOR': self.bgcolor=pair[1]
        """
        CENTER: query center, lat,long
        """
        if pair[0] == 'CENTER': self.center=tuple(float(x) for x in pair[1].split(','))
        """
        RADIUS: plot area, meters
        """
        if pair[0] == 'RADIUS': self.radius=float(pair[1])
        """
        CRS: coordinate reference system to project to
        (wgs84 default)
        """
        if pair[0] == 'CRS': self.crs=pair[1] 
        """
        NETWORK_TYPE: osmnx network type One of
            all (default)
            all_public
            bike
            drive
            drive_service
            walk
        """
        if pair[0] == 'NETWORK_TYPE': self.network_type=pair[1]
        """
        INCHES: plot size, 100dpi
        """
        if pair[0] == 'INCHES': self.figsize=float(pair[1])
        if pair[0] == 'ROUTES': self.routes=pair[1]
        """
        *WIDTH: line width, pixels
        """
        if pair[0] == 'STREET_WIDTH': self.street_width=float(pair[1])
        if pair[0] == 'ROUTE_WIDTH': self.route_width=float(pair[1])

        """
        Some color presets can be chosen by setting COLORS
        """
        if pair[0] == 'COLORS': 
            preset = pair[1].strip()
            if preset == 'lava' or preset == 'falcon':
                self.bgcolor='black' if preset == 'lava' else '#c00'
                self.street_colors='autumn'
            if preset == 'wire':
                self.speeds=False
                self.bgcolor='white'
                self.street_color='#333'
    
    def map(self):
        print('Getting street network')
        G = ox.graph_from_point(
                self.center, 
                dist=self.radius, 
                network_type=self.network_type
            )
        if self.bearings_out is not None:
            print('Adding street bearings')
            ox.add_edge_bearings(G)
            print('Plotting street bearings')
            ox.plot_orientation(G)
        plt.savefig(self.bearings_out)

        if self.crs is not None:
            G = ox.project_graph(G, to_crs=self.crs)

        if self.speeds:
            print('Getting speeds')
            ox.routing.add_edge_speeds(G)
            ec = ox.plot.get_edge_colors_by_attr(G, 'speed_kph', cmap=self.street_colors)
        else: ec=self.street_color
    
        print('Plotting network')
        size=(self.figsize, self.figsize)
        fig, ax = ox.plot_graph(
                   G, 
                   figsize=size,
                   bgcolor=self.bgcolor,
                   edge_color=ec, 
                   edge_linewidth=self.street_width,
                   show=False, 
                   node_size=0
                )
    
        if self.scale is True:
            print('Plotting scale')
            plt.gca().add_artist(AnchoredSizeBar(ax.transAxes,
                    0.2,
                    str((2 * self.radius) / 5)+'m',
                    'lower right'))
    
        plt.savefig(self.file_out)

for i in range(len(argv[1:])):
    g = Map(argv[i+1])
    g.map()
