import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from .callbacks import init as init_callbacks
from .layout import create_layout

load_figure_template(["flatly", "darkly"])

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="Déploiement de Personnel",
)

app.layout = create_layout()
init_callbacks()

if __name__ == "__main__":
    app.run(debug=True)
