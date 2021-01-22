## Glossary

- Jinja2
  Template system https://jinja2docs.readthedocs.io/en/stable/

- Flask
  Microframework that takes care of changing code into a web page https://flask.palletsprojects.com/en/1.1.x/

- Pip
  Takes care of fetching python packages from internet and installing them. https://pypi.org/project/pip/
  `$ pip install <package-name>`

- Decorators
  Special functions that envelopes/wraps function around another function. Used generally to separate business-, and administrative logic. 
  ```
  @app.route('/')  # app is instance of Flask, and route is decorator function
  def home():
  ```

- Iterators:
  Things that can be iterated / looped. Lists are iteratable, but iterators aren't lists.
  ```
  for item in iterator:
    print(item)
  ```

- NoSQL / BASE:
  Way of storing key/value pairs in the cloud.

- Datastore:
  Google specific implementation of NoSQL.

## Tutorials and guides

Interactive python tutorial:
https://www.learnpython.org/

Step-by-step guide of creating Flask application:
https://flask.palletsprojects.com/en/1.1.x/tutorial/

Setting up environment variables to run flask in development mode:
Windows:
`set FLASK_ENV=development`
Linux:
`export FLASK_ENV=development`

Leaflet (mapping library) tutorial:
https://leafletjs.com/examples/quick-start/
