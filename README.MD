# Motivation

Firefly represents my initiative to streamline Business Intelligence (BI) by adopting a more declarative, low-code, "everything-as-code" approach, something I believe is missing in the current BI landscape. I call this concept **reporting as code**. My key requirements are:

- Modern, visually appealing design.
- Flexibility to build any report.
- User-friendly for both engineers and end-users.
- Easily reviewable by team members.
- Seamlessly deployable.
- Version-controlled via Git.
- Fast time to market.
- Simple to develop locally.
- Strong emphasis on data quality.

While Superset shows promise, it is not without its limitations. It is highly UI-centric, which often limits its usability for engineers who prefer code-driven workflows. The goal is to shift the focus toward a more code-centric approach to reporting.

# POC Scope

The concept is straightforward: develop an application to parse YAML files and generate reports without relying on a user interface. Ideally, the UI should be optional. By "report," I mean we need to handle the following entities:

- Secrets (sensitive data)
- Connection (database connection details)
- Dataset (query definition)
- Representation (data visualization)
- Dashboard (a combination of visualizations)

This is quite similar to Superset's functionality, but the objective is to enhance the code-driven reporting aspect.

# Configuration example

## .env

```
order_test_db=test.db
```

## connection/order_test_db.yaml

```yaml
description: yet another DB connection
alchemy_string: "sqlite:///{order_test_db}" # {variable_name} will replace it with the corresponding .env value
```

## dataset/order_test_all.yaml

```yaml
description: yet another dataset
query: select * from order
database: order_test_db
```

## representation/order_test_table.yaml

```yaml
description: yet another table
type: table
dataset: order_test_all
```

## dashboard/order_summary.yaml

```yaml
description: yet another dashboard
# tbd
```

# Implementation

- Secrets will be stored in .env file.
- Connections will utilize SQLAlchemy.
- Datasets will be represented as Pandas dataframes.
- Representations and dashboards will be a mix of HTML and CSS.
- Jupyter Notebook will serve as the IDE for development.
