# Clarify (Backend)

Clarify is data for made easy for schools. The backend runs Django, see below for other packages included:

- Django 1.11
- django-cors-headers
- django-extensions
- django-debug-toolbar

You'll also need to ensure your environment is running **Python 3.6** or above. 

## Getting Started

### Prerequisites

You'll either need an environment manager or VM to get started.

Recommended: virtualenv and virtualenvwrapper.

- [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
- [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)

You'll also need to have PostgreSQL installed. For macOS, [see here](http://postgresapp.com/). 

Clarify needs two databases: the Django database and the mirror (cache) database.

The default names are `clarify` and `clarifycache`.


With PostgreSQL installed and running, the easiest way to create the database is to run the `createdb` command from the command line:

```
$ createdb clarify
$ createdb clarifycache
```

Note: it may be helpful to start with clean databases. If you already have existing databases, you'll want to `dropdb` first:

```
$ dropdb clarify; dropdb clarifycache
$ createdb clarify; createdb clarifycache
```

Download the mirror database dump file (should be called `clarifycachedump.pgsql`), and from its containing directory, run the following command to load the mirror database into an empty `clarifycache` database.

```
$ psql clarifycache < clarifycachedump.pgsql
```

### Installing

To get started, activate your virtual environment and install the requirements.

```
$ pip install -r requirements/local.txt
```

From the root directory, you'll need to migrate the models into the database. 

```
./manage.py migrate
```

The final step is to load the Django models by running the following command.

```
./manage.py pull_models_from_sis
```

This step may take up to 30 minutes or more. 

### REPL

After the model pull completes, you can explore the models with `shell_plus` by running the following command from the project root:

```
./manage.py shell_plus
```
`shell_plus` automatically imports all models from all apps, as well as some convenience features like `settings` and Django model helpers like `Avg`, `Case`, and more.  


## Running the tests

Let's hold off on this for a minute.

## Deployment

We're getting there. 
