# Flask Scotch

Tape a REST API with a local database

## Key Features

- Represent remote model in the form of a python class to be able to manipuldate easily
- Fetch objects from the database or from the remote API using the attributes of the declared models
- Update/delete/create object on the remote API using the declared models

## Install

TODO

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
all_items = await Item.api.all()

nw_item = Item(name='pen', description='a green pen to write things')

final_item = await Item.api.create(nw_item)

final_item.name = 'green pen'
await final_item.update()
await final_item.delete()
```
