# aind-metadata-service-server

[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)
![Code Style](https://img.shields.io/badge/code%20style-black-black)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Python](https://img.shields.io/badge/python->=3.10-blue?logo=python)

REST service to retrieve data from backends and create aind-data-schema models.

## Deprecation Notice

**SLIMS Integration Disabled (2026-08-19)**

The SLIMS data provider has been shut down and all SLIMS-related functionality has been disabled. This includes:
- SLIMS API endpoints (`/api/v2/slims/*`) - routes commented out in main.py
- Rig and instrument endpoints that depended on SLIMS data - routes commented out in main.py
- SLIMS data mapping in procedures and specimen procedures - code commented out
- Water restriction and histology data from SLIMS - not fetched

Files/code commented out for potential future removal:
- `src/aind_metadata_service_server/routes/slims.py` (route file)
- `src/aind_metadata_service_server/routes/rig_and_instrument.py` (route file)
- `src/aind_metadata_service_server/mappers/specimen_procedures.py` (mapper)
- `tests/test_routes/test_slims.py` (tests skipped)
- `tests/test_routes/test_rig_and_instrument.py` (tests skipped)
- SLIMS-related imports/code in various mapper and route files

## Local Development

Requires docker and docker compose to build and run package locally.

- From the root aind-metadata-service directory:
  - Create a folder called env if it doesn't exist.
  - Create a file called env/webapp.env with appropriate env variables.
  - Create a file called env/labtracks.env with appropriate env variables for labtracks service.
  - Repeat the previous step for the rest of the database sources.
- After creating the files, your env directory should look like this:
  - webapp.env
  - labtracks.env
  - sharepoint.env
  - ~~slims.env~~ (DEPRECATED - no longer needed)
  - smartsheet.env
  - tars.env
- Run `docker compose up --build`
- Service will be available at `http://localhost:5000`
- Check docs at `http://localhost:5000/docs`

### Linters and testing

There are several libraries used to run linters, check documentation, and run
 tests.

- Please test your changes using the **coverage** library, which will run the
 tests and log a coverage report:

```
coverage run -m pytest && coverage report
```

- Use **interrogate** to check that modules, methods, etc. have been documented
 thoroughly:

```
interrogate .
```

- Use **flake8** to check that code is up to standards
 (no unused imports, etc.):
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

For internal members, please create a branch. For external members, please fork
 the repo and open a pull request from the fork. We'll primarily use
 [Angular](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
  style for commit messages. Roughly, they should follow the pattern:
```
<type>(<scope>): <short summary>
```

where scope (optional) describes the packages affected by the code changes and
type (mandatory) is one of:

- **build**: Changes that affect the build system or external dependencies
 (example scopes: pyproject.toml, setup.py)
- **ci**: Changes to our CI configuration files and scripts
 (examples: .github/workflows/ci.yml)
- **docs**: Documentation only changes
- **feat**: A new feature
- **fix**: A bug fix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
