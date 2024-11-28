import yaml
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dataclasses import dataclass, field
from typing import Union
from IPython.display import HTML

connection_registry = {}
dataset_registry = {}
chart_registry = {}
dashboard_registry = {}


@dataclass
class Connection:
    name: str
    description: str
    type: str
    config: dict
    engine: Engine = None

    def __post_init__(self):
        alchemy_string = self.config.get("url")

        if alchemy_string:
            self.engine = create_engine(alchemy_string)
        else:
            raise ValueError(
                f"Cannot create a connection to '{self.name}' using the following string: {self.alchemy_string}"
            )

        connection_registry[self.name] = self


@dataclass
class Dataset:
    name: str
    description: str
    query: str
    connection: Union[str, Connection]

    def __post_init__(self):
        try:
            self.connection = connection_registry[self.connection]
        except:
            raise ValueError(
                f"Cannot find '{self.connection}' connetion for '{self.name}' dataset"
            )

        dataset_registry[self.name] = self

    def execute_query(self) -> pd.DataFrame:
        with self.connection.engine.connect() as connection:
            df = pd.read_sql(text(self.query), con=connection)
        return df


@dataclass
class Chart:
    name: str
    description: str
    type: str
    dataset: Union[str, Dataset]

    def __post_init__(self):
        try:
            self.dataset = dataset_registry[self.dataset]
        except:
            raise ValueError(
                f"Cannot find '{self.dataset}' dataset for '{self.name}' chart"
            )

        chart_registry[self.name] = self

    def render(self):
        df = self.dataset.execute_query()
        css = """
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                font-family: Arial, sans-serif;
                font-size: 14px;
                margin: 20px 0;
            }
            thead {
                background-color: #f5f5f5;
                border-bottom: 2px solid #ddd;
            }
            thead th {
                padding: 10px;
                text-align: left;
                font-weight: bold;
                color: #333;
            }
            tbody tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tbody tr:hover {
                background-color: #f1f1f1;
            }
            tbody td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
                color: #555;
            }
            tbody td:first-child {
                font-weight: bold;
            }
        </style>
        """
        return css + df.to_html(index=False)


@dataclass
class Banner:
    text: str

    def render(self):
        css = """
        <style>
            body {
              font-family: "Arial", sans-serif;
            }
            .header {
              font-weight: bold;
              font-size: 18px;
              text-align: left;
              color: #333;
              background-color: #f8f9fa;
              padding: 10px 15px;
              border-bottom: 1px solid #e1e1e1; 
            }
        </style>
        """
        return f"""{css}\n<div class="header">{self.text}</div>"""


@dataclass
class Widget:
    type: str
    config: dict

    def render(self):
        if self.type == "banner":
            banner = Banner(**self.config)
            return banner.render()
        if self.type == "chart":
            chart = chart_registry[self.config["chart"]]
            return chart.render()
        else:
            return ""


@dataclass
class Dashboard:
    name: str
    description: str
    widgets: list

    def __post_init__(self):
        self.widgets = [Widget(**widget) for widget in self.widgets]
        dashboard_registry[self.name] = self

    def render(self):
        return "".join([widget.render() for widget in self.widgets])


@dataclass
class Config:
    path: str
    connections: [Connection] = field(default_factory=list)
    datasets: [Dataset] = field(default_factory=list)
    charts: [Chart] = field(default_factory=list)
    dashboard: [Dashboard] = field(default_factory=list)
    config: dict = field(default_factory=dict)

    def __post_init__(self):

        with open(self.path, "r") as file:
            self.config = yaml.safe_load(file)

        self.connections = [
            Connection(**connection) for connection in self.config["connections"]
        ]
        self.datasets = [Dataset(**dataset) for dataset in self.config["datasets"]]
        self.charts = [Chart(**chart) for chart in self.config["charts"]]
        self.dashboard = [
            Dashboard(**dashboard) for dashboard in self.config["dashboards"]
        ]

    def list(self):
        return {
            _type: [_config["name"] for _config in _configs]
            for _type, _configs in self.config.items()
        }

    def show_dataset(self, name):
        return dataset_registry[name].execute_query()

    def show_chart(self, name):
        return HTML(chart_registry[name].render())

    def show_dashboard(self, name):
        return HTML(dashboard_registry[name].render())
