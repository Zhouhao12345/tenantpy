Tenant Management For Web Application
====
* Database Tenant Isolation
* Cache Tenant Isolation
* Customize Addons Tenant Meta Data Inject

e.g:
```
import flask
from flask import Flask
import json
import peewee

from tenantpy.contrib import flask as flask_tenc

app = Flask(__name__)

class User(flask_tenc.BaseModel):
    englishName = peewee.CharField()
    email = peewee.CharField()


class ConfigManager(flask_tenc.ConfigManager):

    def get_config(self, key: flask_tenc.ConfigKeys):
        # get config by any
        

@app.route("/random")
def random_pet():
    """A cute furry animal endpoint.
    ---
    get:
      description: Get a random pet
      security:
        - ApiKeyAuth: []
      responses:
        200:
          description: Return a pet
          content:
            application/json:
              schema: PetSchema
    """
    # Hardcoded example data
    flask.g.database.begin()
    ins = User.get()
    flask.g.database.rollback()
    pet_data = {
        "name": ins.englishName,
    }
    return flask.Response(json.dumps(pet_data), content_type="application/json")


flask_tenc.init_app(app, ConfigManager())
app.run()

```