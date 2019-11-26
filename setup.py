from setuptools import setup, find_packages

version = None
with open('multiply_ui/version.py') as f:
    exec(f.read())

setup(
    name="multiply_ui",
    version=version,
    description='A GUI for the Multiply project based on Jupyter Notebook',
    license='MIT',
    author='Norman Fomferra',
    packages=find_packages(exclude=["test", "test.*"]),
    include_package_data=True,
    data_files=[('multiply_ui', ['multiply_ui/server/resources/processing-parameters.json',
                                 'multiply_ui/server/resources/pm_request_template.json',
                                 'multiply_ui/server/resources/scripts/*.py',
                                 'multiply_ui/server/resources/templates/*.json',
                                 'multiply_ui/server/resources/workflows/*.py',
                                 ])],
    entry_points={
        'console_scripts': [
            'mui-server = multiply_ui.server.cli:main',
        ]},
    install_requires=[
        'click',
        'ipywidgets',
        'jupyterlab',
        'numpy',
        'tornado',
        'xarray'
    ],
)
