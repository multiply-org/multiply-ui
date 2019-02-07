from setuptools import setup, find_packages

version = None
with open('muimock/version.py') as f:
    exec(f.read())

setup(
    name="muimock",
    version=version,
    description='A GUI mock for the Multiply project based on Jupyter Notebook',
    license='MIT',
    author='Norman Fomferra',
    packages=find_packages(exclude=["test", "test.*"]),
    install_requires=[
        'ipywidgets',
        'jupyterlab',
        'tornado',
    ],
)
