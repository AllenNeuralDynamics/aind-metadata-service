Contributor Guidelines
======================

This document will go through best practices for contributing to this project.
We welcome and appreciate contributions or ideas for improvement.

- `Bug Reports and Feature Requests <#bug-reports-and-feature-requests>`__
- `Local Installation for Development <#local-installation-for-development>`__
- `Branches and Pull Requests <#branches-and-pull-requests>`__
- `Release Cycles <#release-cycles>`__

Bug Reports and Feature Requests
---------------------------------

Before creating a pull request, we ask contributors to please open a bug
report or feature request first:
`issues <https://github.com/AllenNeuralDynamics/aind-metadata-service/issues/new/choose>`__

We will do our best to monitor and maintain the backlog of issues.

Local Installation for Development
------------------------------------

For development,

- For new features or non-urgent bug fixes, create a branch off of ``dev``
- For an urgent hotfix to our production environment, create a branch off of ``main``

Consult the `Branches and Pull Requests <#branches-and-pull-requests>`__
and `Release Cycles <#release-cycles>`__ sections for more details.

Running a Local Server
~~~~~~~~~~~~~~~~~~~~~~

The service and all its backend microservices are orchestrated with Docker
Compose. From the repo root:

1. Create an ``env/`` directory (gitignored):

.. code:: bash

   mkdir -p env

2. Populate the required ``.env`` files — one per backend microservice:

.. code:: text

   env/
   ├── webapp.env
   ├── labtracks.env
   ├── sharepoint.env
   ├── smartsheet.env
   ├── tars.env
   ├── dataverse.env
   ├── mgi.env
   └── active_directory.env

Each file sets the permissions for each of the backend microservices. 
The ``webapp.env`` file is required for the main service and sets the host URL for that backend. The main service reads the
following environment variables (all prefixed ``AIND_METADATA_SERVICE_``):

- ``AIND_METADATA_SERVICE_LABTRACKS_HOST``
- ``AIND_METADATA_SERVICE_MGI_HOST``
- ``AIND_METADATA_SERVICE_SMARTSHEET_HOST``
- ``AIND_METADATA_SERVICE_TARS_HOST``
- ``AIND_METADATA_SERVICE_SESSION_JSON_HOST``
- ``AIND_METADATA_SERVICE_SHAREPOINT_HOST``
- ``AIND_METADATA_SERVICE_DATAVERSE_HOST``
- ``AIND_METADATA_SERVICE_ACTIVE_DIRECTORY_HOST``
- ``AIND_METADATA_SERVICE_DOCDB_API_HOST``
- ``AIND_METADATA_SERVICE_AIND_DATA_SCHEMA_V1_HOST``

3. Build and start all services:

.. code:: bash

   docker compose up --build

You can now access aind-metadata-service at ``http://localhost:5000``.
The interactive Swagger UI is at ``http://localhost:5000/docs``.

Branches and Pull Requests
---------------------------

Branch Naming Conventions
~~~~~~~~~~~~~~~~~~~~~~~~~~

Name your branch using the following format:
``<type>-<issue_number>-<short_summary>``

where:

``<type>`` is one of:

- **build**: Changes that affect the build system or external dependencies (e.g., pyproject.toml, setup.py)
- **ci**: Changes to our CI configuration files and scripts (examples: .github/workflows/ci.yml)
- **docs**: Changes to our documentation
- **feat**: A new feature
- **fix**: A bug fix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature, but will make the codebase easier to maintain
- **test**: Adding missing tests or correcting existing tests
- **hotfix**: An urgent bug fix to our production code

``<issue_number>`` references the GitHub issue this branch will close

``<short_summary>`` is a brief description that shouldn't be more than 3 words.

Some examples:

- ``feat-12-adds-subject-endpoint``
- ``fix-27-corrects-mapper``
- ``test-43-updates-route-test``

We ask that a separate issue and branch are created if code is added outside
the scope of the reference issue.

Commit Messages
~~~~~~~~~~~~~~~

Please format your commit messages as ``<type>: <short summary>`` where
``<type>`` is from the list above and the short summary is one or two sentences.

Testing and Docstrings
~~~~~~~~~~~~~~~~~~~~~~

We strive for complete code coverage and docstrings, and we also run code
format checks. Install the server package in editable mode with dev
dependencies to run them locally:

.. code:: bash

   cd aind-metadata-service-server
   pip install -e ".[dev]"

- To run the code format check:

.. code:: bash

   flake8 .

- There are some helpful libraries that will automatically format the code and
  import statements:

.. code:: bash

   black .

and

.. code:: bash

   isort .

Strings that exceed the maximum line length may still need to be formatted
manually.

- To run the docstring coverage check and report:

.. code:: bash

   interrogate -v .

This project requires 100% docstring coverage.

- To run the unit test coverage check and report:

.. code:: bash

   coverage run -m pytest && coverage report

- To view a more detailed HTML version of the report, run:

.. code:: bash

   coverage run -m pytest
   coverage html

and then open ``htmlcov/index.html`` in a browser.

This project enforces 100% test coverage. All new code must be covered by tests.

Adding a New Endpoint
~~~~~~~~~~~~~~~~~~~~~

Contributors work inside the ``aind-metadata-service-server`` package. Each new
data source requires its own microservice — a separate repo built from the
`aind-service-template <https://github.com/AllenNeuralDynamics/aind-service-template>`_
— which is published as an async client package. Once the async client exists:

1. **Add the async client as a dependency** in
   ``aind-metadata-service-server/pyproject.toml``.
2. **Add a session** in ``src/aind_metadata_service_server/sessions.py`` —
   an async generator yielding a configured client instance, wired as a FastAPI
   dependency.
3. **Add a mapper** (when mapping to ``aind-data-schema``) — a new file in
   ``src/aind_metadata_service_server/mappers/`` that transforms the raw client
   response into the target model. If no transformation is needed, the response
   can be returned directly.
4. **Add a route** — a new file in
   ``src/aind_metadata_service_server/routes/``, registered in ``main.py``.
5. **Add tests** under ``tests/test_mappers/`` and ``tests/test_routes/`` to
   maintain 100% coverage.

Pull Requests
~~~~~~~~~~~~~

Pull requests and reviews are required before merging code into this project.
You may open a ``Draft`` pull request and ask for a preliminary review on code
that is currently a work-in-progress.

Before requesting a review on a finalized pull request, please verify that the
automated checks have passed first.

Release Cycles
--------------

For this project, we have adopted the `Git Flow <https://www.gitkraken.com/learn/git/git-flow>`__
system. Releases and version bumps are automated via
`semantic-release <https://semantic-release.gitbook.io/>`__ (``feat`` → minor
bump, ``fix`` → patch bump). The rough workflow is:

Hotfixes
~~~~~~~~

- A ``hotfix`` branch is created off of ``main``
- A Pull Request into ``main`` is opened, reviewed, and merged into ``main``
- A new ``tag`` with a patch bump is created automatically and a new release is deployed
- The ``main`` branch is merged into all other branches

Feature Branches and Bug Fixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- A new branch is created off of ``dev``
- A Pull Request into ``dev`` is opened, reviewed, and merged

Release Branch
~~~~~~~~~~~~~~

- A new branch ``release-v{new_tag}`` is created
- Documentation updates and bug fixes are created off of the ``release-v{new_tag}`` branch
- Commits added to ``release-v{new_tag}`` are also merged into ``dev``
- Once ready for release, a Pull Request from ``release-v{new_tag}`` into ``main`` is opened for final review
- A new tag will automatically be generated
- Once merged, a new GitHub Release is created manually

Pre-Release Checklist
~~~~~~~~~~~~~~~~~~~~~

- ☐ Run linters, unit tests, and integration tests

  .. code:: bash

     flake8 .
     interrogate .
     coverage run -m pytest && coverage report

- ☐ Verify the service is deployed and tested in the staging environment

- ☐ Update documentation and rebuild:

  .. code:: bash

     sphinx-build -b html docs/source/ docs/build/html

- ☐ Update architecture diagrams in ``docs/diagrams/`` if any service topology changed

Post-Release Checklist
~~~~~~~~~~~~~~~~~~~~~~

- ☐ Merge ``main`` into ``dev`` and feature branches
- ☐ Edit release notes if needed
- ☐ Post announcement
