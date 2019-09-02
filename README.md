# multiply-ui

A Jupyter-based UI for the [Multiply](https://github.com/multiply-org) project based on
[Jupyter Widgets](https://ipywidgets.readthedocs.io) and [Bokeh](https://bokeh.pydata.org).

# Concept

The Multiply images include Jupyter Lab, a dedicated Multiply REST server
and a Multiply Notebook API. 

When the Docker is started on its host VM, the Jupyter Lab server and the Multiply
REST server are started. User get a dedicated URL that brings up the Jupyter Lab
in their browser. From Jupyter Lab they have access to
* Jupyter Notebooks that can import the Multiply Notebook API
* Terminal windows that allow accessing the container environment and 
  mounted file systems. 

The Multiply Notebook API provides a simple set of functions (API) that 
bring up dedicated UI forms, such as data query and job execution.

The API provides access to objects that are a result of the GUI interaction.
Users can further interact with such objects e.g. `job = Job(13); job.cancel()`. 
These objects also have dedicated HTML representations in the notebook. For example
a query result may render a table of data files, or a processing result 
may render quicklooks. 

Another set of functions may be provided for simple analysis and visualisation of the 
processing results. 

For new users, we will provide a set of Notebooks for the most common 
Multiply use cases. Users can use them as starting points.


## Advantages of using Jupyter Lab

* With Jupyter Lab, users can 
  * create and modify any number of wokflows and data anlyses and store them
    in their workspaces;
  * have numerous notebooks and output displays side by side;
  * use a variability of data visualisations already available.
* Very flexible, users can bring up UIs anywhere in the flow and interact with
  the objects they produce such as jobs, queries.
* Python programmers can easily extend the UI capabilities by writing 
  new UI, analysis and visualisation functions.
* Custom widgets can be implemented using JavaScript. 
  This allows for integration of popular and powerful JS visualisation libraries 
  (e.g. Leaflet Map, D3)
* In the Notebooks, users can exploit the power of numerous popular Python data science 
  packages (xarray, numpy, scipy, pandas, ...)


# Installation

Create environment:

    $ cd multiply-ui
    $ conda env create

Activate environment and install sources:

    $ conda activate multiply-ui

You will also need to install the [MULTIPLY Core](https://github.com/multiply-org/multiply-core) and 
[Data Access components](https://github.com/multiply-org/data-access) components. After you have checked out the 
source code from github, you can install the packages with

    $ python setup.py develop 

Install jupyter-widgets and jupyter-leaflet extension for Jupyter-Lab

    $ jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.38.1
    $ jupyter labextension install jupyter-leaflet@0.10.4

Install the MULTIPLY extension for Jupyter-Lab

    $ cd js
    $ npm install
    $ cd ..
    4 jupyter labextension install js

Install multiply-ui from source code:

    $ python setup.py develop

Run multiply-ui web service:

    $ mui-server

Run Jupyter Lab

    $ jupyter-lab notebooks/mui-demo.ipynb

Note for developers: For automatically building the JavaScript code every time there is a change,
run the following command from the /js/ directory:

    $ npm run watch

And to run Jupyter Lab, use this command:

    $ jupyter lab --watch notebooks/mui-demo.ipynb

Every time a JavaScript build has terminated you need to refresh the Notebook page
in order to load the JavaScript code again.

# Related Reads

* Jupyter Lab: https://jupyterlab.readthedocs.io
* Jupyter Widgets: https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html
* Bokeh docs: https://bokeh.pydata.org/en/latest/docs/user_guide/notebook.html
* Bokeh examples: https://github.com/bokeh/bokeh/tree/1.0.4/examples/howto/notebook_comms

* Integrating your objects with IPython: https://ipython.readthedocs.io/en/stable/config/integrating.html
