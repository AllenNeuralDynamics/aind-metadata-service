User Guide
==========

This guide covers how to query the AIND Metadata Service from your own code.

Access and Connectivity
-----------------------

The metadata service runs on the Allen Institute's internal infrastructure.
**You must be on the VPN (or on-site) to reach it.**

The base URL for the service is:

.. code:: text

   http://aind-metadata-service

An interactive API reference (Swagger UI) listing every endpoint, its
parameters, and example responses is available at:

.. code:: text

   http://aind-metadata-service/docs

Making Requests
---------------

There are three ways to query the service:

1. `Plain HTTP requests`_ — use any HTTP library; good for quick scripts or
   languages other than Python.
2. `Python sync client`_ — a typed, auto-generated client; suitable for scripts
   and notebooks.
3. `Python async client`_ — same as the sync client but ``aiohttp``-based;
   suitable for async applications.

Plain HTTP Requests
~~~~~~~~~~~~~~~~~~~

Using `requests <https://requests.readthedocs.io/>`__:

.. code:: python

   import requests

   BASE_URL = "http://aind-metadata-service"

   # Fetch procedures for a subject
   response = requests.get(f"{BASE_URL}/api/v2/procedures/123456")
   response.raise_for_status()
   data = response.json()

   # Fetch subject metadata
   response = requests.get(f"{BASE_URL}/api/v2/subject/123456")
   response.raise_for_status()
   subject = response.json()

Python Sync Client
~~~~~~~~~~~~~~~~~~

Install the client:

.. code:: bash

   pip install aind-metadata-service-client

Example usage:

.. code:: python

   from aind_metadata_service_client import ApiClient, Configuration
   from aind_metadata_service_client.api import DefaultApi

   config = Configuration(host="http://aind-metadata-service")

   with ApiClient(config) as client:
       api = DefaultApi(client)

       # Fetch procedures for a subject
       procedures = api.get_procedures_api_v2_procedures_subject_id_get(
           subject_id="123456"
       )

       # Fetch subject metadata
       subject = api.get_subject_api_v2_subject_subject_id_get(
           subject_id="123456"
       )

Python Async Client
~~~~~~~~~~~~~~~~~~~

Install the async client:

.. code:: bash

   pip install aind-metadata-service-async-client

Example usage:

.. code:: python

   import asyncio
   from aind_metadata_service_async_client import ApiClient, Configuration
   from aind_metadata_service_async_client.api import DefaultApi

   async def main():
       config = Configuration(host="http://aind-metadata-service")

       async with ApiClient(config) as client:
           api = DefaultApi(client)

           # Fetch procedures for a subject
           procedures = await api.get_procedures_api_v2_procedures_subject_id_get(
               subject_id="123456"
           )

           # Fetch subject metadata
           subject = await api.get_subject_api_v2_subject_subject_id_get(
               subject_id="123456"
           )

   asyncio.run(main())

Available Endpoints
-------------------

Browse the live Swagger UI at
``http://aind-metadata-service/docs`` for interactive exploration with
example responses.
