import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='pandemaniac',
    version='0.0.1',
    author='Rosita Fu',
    author_email='rosita.fu99@gmail.com',
    description='CS144 Pandemaniac iterative visualizer',
    long_description=long_description,
    long_description_content_type='ext/markdown',
    packages=setuptools.find_packages(),
    install_requires=["numpy", "pandas", "bokeh>=1.4.0",
                      "panel", "json", "networkx"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
