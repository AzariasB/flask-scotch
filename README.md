# Flask Scotch

Tape a REST API with a local database

## Key Features

- Represent remote model in the form of a python class to be able to manipuldate easily
- Fetch objects from the database or from the remote API using the attributes of the declared models
- Update/delete/create object on the remote API using the declared models

## Install

`pip install flask-scotch`

## Getting started

First, you need to register the extension in flask

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
from flask_scotch import RemoteModel, LocalRelationship, LocalModel, RemoteRelationship
import sqlalchemy as sa

db = sa.create_engine()


class Item(LocalModel, db.Model):
    __remote_directory__ = 'items'

    id: int
    name: str
    description: str
    storage_id: int

    storage = RemoteRelationship("Storage")


class Storage(RemoteModel):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

    items = LocalRelationship("Item")


# You can then use this model to fetch data from the remote api:


all_items = Storage.api.all()

my_storage = Storage(id=10, name='pen')

final_storage = Storage.api.create(my_storage)

final_storage.name = 'green pen'
final_storage.update()

items = [Item(storage_id=10, name="item1"), Item(storage_id=10, name="item2")]
db.session.add(*items)
db.session.commit()

# Can now access the local items from
# the storage object
for item in my_storage.items:
    print(item)

final_storage.delete()
```

## TODO

- [x] ForeignModel: to be able to access an object from the API when it's accessed from a local model
    - [x] Handle 1:1 relations
    - [ ] Handle 1:N relations
- [x] LocalModel:
    - [x] Handle 1:1 relations
    - [x] Handle 1:N relations
- [x] ForeignModel and LocalModel: ability to reference a class with a string, rather than with the class directly
- [ ] LocalModel, propagates changes when added to list, so that sqlAlchemy updates the id when necessary (maybe
  using [InstrumentedList](https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/orm/collections.py) can
  help)
- [ ] Improve handling of return values from the API, and throw error based on the HTTP code returned
- [ ] Improve typing of all public functions and classes
- [ ] Automatically detect cross-referencing PartialModels and RemoteModel to avoid having to declare everything
- [ ] Have a 100% code coverage
