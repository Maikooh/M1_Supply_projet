import threading
import webbrowser

import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from src.optimisation_effectif.Dashboard.callbacks import init as init_callbacks
from src.optimisation_effectif.Dashboard.layout import create_layout

load_figure_template(["flatly", "darkly"])

PORT = 8050

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    title="Déploiement de Personnel",
)

app.layout = create_layout()
init_callbacks()

if __name__ == "__main__":
    threading.Timer(1.5, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    app.run(debug=True, use_reloader=False, port=PORT)
