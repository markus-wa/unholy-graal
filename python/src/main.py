import polyglot
import plotly_express as px
import plotly.io as pio
import pandas as pd

pio.renderers.default = "firefox"

@polyglot.export_value
def python_method():
    data = pd.read_csv('data.csv')

    fig = px.box(data, x="some", y="data")
    fig.show()

    return "Hello from Python!"
