# Clarify (Backend)

Clarify is data for made easy for schools. The backend runs Django, see below for other packages included:

- Django 1.11
- django-cors-headers
- django-extensions
- django-debug-toolbar

You'll also need to ensure your environment is running **Python 3.6** or above. 

For macOS, you can use **[Homebrew](https://brew.sh)** to install Python 3. 

```
$ brew install python3
```

To check installation, run the following command and you should receive the path to Python 3:

```
$ which python3
>> /usr/local/bin/python3
```

## Getting Started

### Prerequisites

You'll either need an environment manager or VM to get started.

Recommended: **virtualenv** and **virtualenvwrapper**.

- **[virtualenv](https://virtualenv.pypa.io/en/stable/installation/)**
- **[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)**

Once you have those installed, you can run the following commands to create an environment:

```
$ mkvirtualenv clarify -p $(which python3)
```

To exit the environment, use `deactivate`, and with **virtualenvwrapper**, every time you start up the terminal, you can use the following command to activate the environment again:

```
$ workon clarify
```

You'll also need to have PostgreSQL installed. For macOS, [see here](http://postgresapp.com/). 

For this build, Clarify needs two databases: the Django database and the mirror (cache) database.

The default names are `clarify` and `clarifycache`.

Before creating the database, ensure that Postgres is running by opening the terminal and checking to see if you can enter the Postgres CLI by running the following command:

```
$ psql
```
This should take you to another CLI environment, but if it throws an error, Postgres is not running.

With PostgreSQL installed and running, the easiest way to create the database is to run the `createdb` command from the terminal:

( Note: This is from the terminal / from bash, _not_ the `psql` environment referenced above. )

```
$ createdb clarify
$ createdb clarifycache
```

It may be helpful to start with clean databases. If you already have existing databases, you'll want to `dropdb` first:

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
There are multiple `requirements/*.txt` files, but you only need to worry about `local` as it takes care of importing from the other files as needed.

From the root directory, you'll need to migrate the models into the database.

```
$ ./manage.py migrate
```

The final step is to load the Django models by running the following command.

```
$ ./manage.py pull_models_from_sis
```

This step may take up to 30 minutes or more. 

### Loading `clarify` database from dump file

Alternatively, if you have a Django database dump file (`clarify_dump.pgsql`), you can run the same command from earlier to load the data directly into Django instead. 

```
$ psql clarify < clarify_dump.pgsql
```
It's best to do this on a freshly created database, so go through the process under **Preqrequisites** to drop and create a new `clarify` database and **do not run** `migrate`.

### REPL

After the model pull completes, you can explore the models with `shell_plus` by running the following command from the project root:

```
$ ./manage.py shell_plus
```
`shell_plus` automatically imports all models from all apps, as well as some convenience features like `settings` and Django model helpers like `Avg`, `Case`, and more.  


## Running the tests

Let's hold off on this for a minute.

## Deployment

We're getting there. 

## Commit messages
Commit messages should be written in the imperative, sentance form. This makes the git history a list of statements of work that are easy to scan. E.g. "Change the base font size to 14px" is preferable to "base font changes". Include as many details as possible while maintaining a 50 character limit. This allows commit messages to display in most editors. If you can't limit yourself to 50 characters, that's a good indication that your commit is doing too much. Consider breaking it up into a few different commits each responsible for their own pieces of functionality.


## Branches and Pull Requests
Resist the urge to push directly to the `master` branch. For most organization members this functionality is disabled to encourage pull request-based review and development. PR's should be opened early and often during a workflow. Think of them as works in progress, even if there's only a skeleton initial commit. Tag or assign the PR to the relevent parties and use the description as a statement of intended work. That way the commits reflect the evolution of that work and tagged team members can validate or redirect as it progresses. 


