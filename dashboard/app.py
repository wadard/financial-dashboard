import dash_bootstrap_components as dbc
from dash import Dash

from dashboard.callbacks import DashboardCallbacks
from dashboard.layout import DashboardLayout


class TransactionAnalyticsApp:
    def __init__(self):
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
        self.app.title = "Transaction Analytics"
        self.app.layout = DashboardLayout().create()
        DashboardCallbacks().register(self.app)

    def run(self):
        self.app.run_server(debug=True)


if __name__ == "__main__":
    TransactionAnalyticsApp().run()
