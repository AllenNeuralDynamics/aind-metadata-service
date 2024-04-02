# aind-metadata-service

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)

REST service to retrieve metadata from databases.

## Installation

### Server Installation

Can be pip installed using `pip install aind-metadata-service[server]`.

Installing `pyodbc`.
- You may need to install `unixodbc-dev`. You can follow this [https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16](link) for instructions depending on your os.

- You may need to run `docker system prune` before building the docker image if you're getting erros running apt-get:
```
#10 23.69 Err:1 http://deb.debian.org/debian bullseye/main amd64 libodbc1 amd64 2.3.6-0.1+b1
#10 23.69   Could not connect to debian.map.fastlydns.net:80 (146.75.42.132). - connect (111: Connection refused) Unable to connect to deb.debian.org:http:

```

### Client Installation

Can be pip installed with `pip install aind-metadata-service[client]`

### For Development

In the root directory, run
```
pip install -e .[dev]
```

## Contributing

### Linters and testing

There are several libraries used to run linters, check documentation, and run tests.

- Please test your changes using the **coverage** library, which will run the tests and log a coverage report:

```
coverage run -m unittest discover && coverage report
```

- Use **interrogate** to check that modules, methods, etc. have been documented thoroughly:

```
interrogate .
```

- Use **flake8** to check that code is up to standards (no unused imports, etc.):
```
flake8 .
```

- Use **black** to automatically format the code into PEP standards:
```
black .
```

- Use **isort** to automatically sort import statements:
```
isort .
```

### Pull requests

For internal members, please create a branch. For external members, please fork the repo and open a pull request from the fork. We'll primarily use [Angular](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit) style for commit messages. Roughly, they should follow the pattern:
```
<type>(<scope>): <short summary>
```

where scope (optional) describes the packages affected by the code changes and type (mandatory) is one of:

- **build**: Changes that affect the build system or external dependencies (example scopes: pyproject.toml, setup.py)
- **ci**: Changes to our CI configuration files and scripts (examples: .github/workflows/ci.yml)
- **docs**: Documentation only changes
- **feat**: A new feature
- **fix**: A bug fix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests

### Documentation
To generate the rst files source files for documentation, run
```
sphinx-apidoc -o doc_template/source/ src 
```
Then to create the documentation html files, run
```
sphinx-build -b html doc_template/source/ doc_template/build/html
```
More info on sphinx installation can be found here: https://www.sphinx-doc.org/en/master/usage/installation.html

### Responses
There are 6 possible status code responses for aind-metadata-service:
- **200**: successfully retrieved valid data without any problems. 
- **406**: successfully retrieved some data, but failed to validate against pydantic models.
- **404**: found no data that matches query.
- **300**: queried the server, but more items were returned than expected.
- **503**: failed to connect to labtracks/sharepoint servers.
- **500**: successfully connected to labtracks/sharepoint, but some other server error occurred.
These status codes are defined in StatusCodes enum in response_handler.py
