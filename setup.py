import setuptools

setuptools.setup(
    name='pandemaniac',
    version='1.0.2',
    author='Rosita Fu',
    author_email='rosita.fu99@gmail.com',
    url="https://github.com/atisor73/pandemaniac",
    description='CS144 Pandemaniac iterative visualizer',
    long_description="Pandemaniac is a package for visualizing the history of competing seeds on a multiplayer graph for the ‘pandemaniac’ project in CS144 at Caltech.",
    packages=setuptools.find_packages(),
    install_requires=["numpy", "pandas", "bokeh>=2.4.2",
                      "panel>=0.12.6", "networkx", "iqplot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
