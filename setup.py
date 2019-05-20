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
