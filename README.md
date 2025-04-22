# aind-metadata-service

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)

REST service to retrieve metadata from various AIND databases hosted at http://aind-metadata-service/ . 
Spins up query-able endpoints for each database to fetch metadata. 

## User Installation & Usage
These instructions are for users at the Allen Institute using the [existing deployment](http://aind-metadata-service/). 

### Using the HTTP API 
To programatically interact with the HTTP API, you can use the `requests` library. For example, to fetch procedures for a particular subject_id: 

```python
import requests

subject_id = "000000"
url = f"http://aind-metadata-service/procedures/{subject_id}"
response = requests.get(url)
response.raise_for_status()
rj = response.json()

data = rj.get("data")
message = rj.get("message")
```
This can be done with any of the HTTP endpoints. More info about available endpoints and acceptable queries can be found [here](http:/aind-metadata-service/docs)


### Using the Metadata Service API Client

The client provides a simple interface to the API. It can be installed with pip:

```bash
pip install "aind-metadata-service[client]"
```

Once installed, you can use the provided `AindMetadataServiceClient` to fetch metadata.

```python
from aind_metadata_service.client import AindMetadataServiceClient

# Initialize client with the server domain
# If you're at the Allen Institute, use one of these domains:
client = AindMetadataServiceClient(domain="http://aind-metadata-service")  # production
# client = AindMetadataServiceClient(domain="http://aind-metadata-service-dev")  # development

# Subject and procedures
subject_data = client.get_subject("775745").json()
procedures_data = client.get_procedures("775745").json()

# Intended measurements and other data
measurements = client.get_intended_measurements("775745").json()
injection_materials = client.get_injection_materials("VT3214G").json()
ecephys_sessions = client.get_ecephys_sessions("775745").json()
perfusions = client.get_perfusions("775745").json()

# Protocol and funding information 
protocol_info = client.get_protocols("Protocol-123").json()
funding_info = client.get_funding("Project-ABC").json()
project_names = client.get_project_names().json()

# SLIMS data
imaging_data = client.get_smartspim_imaging(
    subject_id="775745",
    start_date_gte="2023-01-01",
    end_date_lte="2023-12-31"
).json()

histology_data = client.get_histology(subject_id="775745").json()
```

## Deployment 
Install the server to host your own metadata-service, whether locally for development or in a production environment. 
### Server Installation
The server can be pip installed using `pip install "aind-metadata-service[server]"`.

Installing `pyodbc`.
- You may need to install `unixodbc-dev`. You can follow this [https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16](link) for instructions depending on your os.

- You may need to run `docker system prune` before building the docker image if you're getting errors running apt-get:
```
#10 23.69 Err:1 http://deb.debian.org/debian bullseye/main amd64 libodbc1 amd64 2.3.6-0.1+b1
#10 23.69   Could not connect to debian.map.fastlydns.net:80 (146.75.42.132). - connect (111: Connection refused) Unable to connect to deb.debian.org:http:

```

## Development

Development dependencies can be pip installed using `pip install "aind-metadata-service[dev]"`.
Once the development environment is setup, use docker to run locally. 


### Running Locally with Docker

#### 1. Build the container
```bash
docker build . -t aind-metadata-service-local:latest
```

#### 2. Using AWS Credentials from Local Machine
If your AWS credentials are already configured on your machine (`~/.aws/credentials` on Linux/macOS or `%USERPROFILE%\.aws\credentials` on Windows), you can mount your credentials directly into the container:
1. Run the container with AWS credentials mounted:
```bash
docker run -v ~/.aws:/root/.aws -e AWS_PROFILE={profile} -e AWS_PARAM_STORE_NAME={param name} -p 58350:58350 -p 5000:5000 aind-metadata-service-local:latest
```
This allows the container to use your locally configured AWS credentials without needing to pass them explicitly.

This will start the service on port `5000`. You can access it at:
```
http://localhost:5000
```

2. If you run into errors reading from your aws configurations, explicitly set the region and aws config file path:
```bash
MSYS_NO_PATHCONV=1 docker run -v {aws_config_file_path} -e AWS_PROFILE={profile} -e AWS_PARAM_STORE_NAME={param name} -e AWS_DEFAULT_REGION={region} -p 58350:58350 -p 5000:5000 aind-metadata-service-local:latest
```

3. If your aws configurations are not setup, you can request credentials. 

#### 3. Using Environment File
You can also run the container with credentials defined in a `.env` file. Check the `.env.template` for required variables.

```bash
docker run -it -p 58350:58350 -p 5000:5000 --env-file=.env aind-metadata-service-local
```

## Contributing
### Linters and testing

There are several libraries used to run linters, check documentation, and run tests.

The following checks are enforced through GitHub Actions CI:
- **flake8** to check that code is up to standards (no unused imports, etc.)
- **interrogate** to check documentation coverage
- **coverage** for 100% test coverage requirement

Checks should ideally be run locally before pushing to github:

Test your changes using the **coverage** library, which will run the tests and log a coverage report:
```bash
coverage run -m unittest discover && coverage report
```

Use **interrogate** to check that modules, methods, etc. have been documented thoroughly:
```bash
interrogate --verbose .
```

Use **flake8** to check that code is up to standards (no unused imports, etc.):
```bash
flake8 .
```

Additional recommended but optional tools:

Use **black** to automatically format the code into PEP standards:
```bash
black .
```

Use **isort** to automatically sort import statements:
```bash
isort .
```

#### Optional: Pre-commit Hooks

To automatically run style checks before each commit (recommended but optional):

```bash
# Install pre-commit (already included in dev dependencies)
pre-commit install
```

The hooks will run automatically on each commit, but can be bypassed with `git commit --no-verify` if needed.

Code style specifications:
- Line length: 79 characters
- Python version: 3.10+
- Style guide: PEP 8 (enforced by flake8)

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

### API Response Codes
There are 6 possible status code responses for aind-metadata-service:
- **200**: successfully retrieved valid data without any problems.
- **406**: successfully retrieved some data, but failed to validate against pydantic models.
- **404**: found no data that matches query.
- **300**: queried the server, but more items were returned than expected.
- **503**: failed to connect to labtracks/sharepoint servers.
- **500**: successfully connected to labtracks/sharepoint, but some other server error occurred.
These status codes are defined in StatusCodes enum in response_handler.py

