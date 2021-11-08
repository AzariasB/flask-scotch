# Flask Scotch

Tape a REST API with a local database

## Key Features

- Represent remote model in the form of a python class to be able to manipuldate easily
- Fetch objects from the database or from the remote API using the attributes of the declared models
- Update/delete/create object on the remote API using the declared models

## Install

`pip install flask-scotch`

## Getting started

Firs, you need to register the extension in flask

```python
from flask_scotch import FlaskScotch
from flask import Flask

# Configure the URL of the remote API with the configuration
# SCOTCH_API_URL='https://mysite.com/api/v1'

# Register the sqlAlchemy engine with flask-sqlalchemy, or provide it directly
# in the constructor

scotch = FlaskScotch()

app = Flask()

scotch.init_app(app)
```

Then, you can declare the "remote model", that is, the model present on the remote server.

```python
from flask_scotch import RemoteModel


class Item(RemoteModel):
    __remote_directory__ = 'items'

    id: int
    name: str
    description: str


# You can then use this model to fetch data from the remote api:
all_items = Item.api.all()

nw_item = Item(name='pen', description='a green pen to write things')

final_item = Item.api.create(nw_item)

final_item.name = 'green pen'
final_item.update()
final_item.delete()
```

## TODO

- [] ForeignModel: to be able to access an object from the API when it's accessed from a local model
    - [] Handle 1:1 relations
    - [] Handle 1:N relations
- [] LocalModel:
- [] ForeignModel and LocalModel: ability to reference a class with a string, rather than with the class directly
- [] LocalModel, propagates changes when added to list, so that sqlAlchemy updates the id when necessary (maybe using [InstrumentedList](https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/orm/collections.py) can help)
- [] Improve handling of return values from the API, and throw error based on the HTTP code returned
- [] Improve typing of all public functions and classes
- [] Have a 100% code coverage
