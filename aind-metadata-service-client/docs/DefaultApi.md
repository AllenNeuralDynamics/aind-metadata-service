# aind_metadata_service_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_bergamo_session**](DefaultApi.md#get_bergamo_session) | **POST** /bergamo_session | Get Bergamo Session
[**get_funding**](DefaultApi.md#get_funding) | **GET** /funding/{project_name} | Get Funding
[**get_injection_materials**](DefaultApi.md#get_injection_materials) | **GET** /tars_injection_materials/{prep_lot_number} | Get Injection Materials
[**get_instrument**](DefaultApi.md#get_instrument) | **GET** /instrument/{instrument_id} | Get Instrument
[**get_intended_measurements**](DefaultApi.md#get_intended_measurements) | **GET** /intended_measurements/{subject_id} | Get Intended Measurements
[**get_mgi_allele**](DefaultApi.md#get_mgi_allele) | **GET** /mgi_allele/{allele_name} | Get Mgi Allele
[**get_perfusions**](DefaultApi.md#get_perfusions) | **GET** /perfusions/{subject_id} | Get Perfusions
[**get_procedures**](DefaultApi.md#get_procedures) | **GET** /procedures/{subject_id} | Get Procedures
[**get_project_names**](DefaultApi.md#get_project_names) | **GET** /project_names | Get Project Names
[**get_protocols**](DefaultApi.md#get_protocols) | **GET** /protocols/{protocol_name} | Get Protocols
[**get_rig**](DefaultApi.md#get_rig) | **GET** /rig/{rig_id} | Get Rig
[**get_slims_workflow**](DefaultApi.md#get_slims_workflow) | **GET** /slims/{workflow} | Get Slims Workflow
[**get_subject**](DefaultApi.md#get_subject) | **GET** /subject/{subject_id} | Get Subject
[**index**](DefaultApi.md#index) | **GET** / | Index


# **get_bergamo_session**
> object get_bergamo_session(job_settings)

Get Bergamo Session

## Session
Return session metadata computed from aind-metadata-mapper.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.models.job_settings import JobSettings
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    job_settings = aind_metadata_service_client.JobSettings() # JobSettings | 

    try:
        # Get Bergamo Session
        api_response = api_instance.get_bergamo_session(job_settings)
        print("The response of DefaultApi->get_bergamo_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_bergamo_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_settings** | [**JobSettings**](JobSettings.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_funding**
> object get_funding(project_name, subproject=subproject)

Get Funding

## Funding
Return Funding metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    project_name = 'Discovery-Neuromodulator circuit dynamics during foraging' # str | 
    subproject = 'Subproject 2 Molecular Anatomy Cell Types' # str |  (optional)

    try:
        # Get Funding
        api_response = api_instance.get_funding(project_name, subproject=subproject)
        print("The response of DefaultApi->get_funding:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_funding: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**|  | 
 **subproject** | **str**|  | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_injection_materials**
> object get_injection_materials(prep_lot_number)

Get Injection Materials

## Injection Materials
Return Injection Materials metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    prep_lot_number = 'VT3214G' # str | 

    try:
        # Get Injection Materials
        api_response = api_instance.get_injection_materials(prep_lot_number)
        print("The response of DefaultApi->get_injection_materials:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_injection_materials: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prep_lot_number** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_instrument**
> object get_instrument(instrument_id, partial_match=partial_match)

Get Instrument

## Instrument
Return an Instrument.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    instrument_id = '440_SmartSPIM1_20240327' # str | 
    partial_match = False # bool |  (optional) (default to False)

    try:
        # Get Instrument
        api_response = api_instance.get_instrument(instrument_id, partial_match=partial_match)
        print("The response of DefaultApi->get_instrument:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_instrument: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **instrument_id** | **str**|  | 
 **partial_match** | **bool**|  | [optional] [default to False]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_intended_measurements**
> object get_intended_measurements(subject_id)

Get Intended Measurements

## Intended Measurements
Return Intended Measurements metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    subject_id = '775745' # str | 

    try:
        # Get Intended Measurements
        api_response = api_instance.get_intended_measurements(subject_id)
        print("The response of DefaultApi->get_intended_measurements:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_intended_measurements: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subject_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_mgi_allele**
> object get_mgi_allele(allele_name)

Get Mgi Allele

## MGI Allele
Return MGI Allele metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    allele_name = 'Parvalbumin-IRES-Cre' # str | 

    try:
        # Get Mgi Allele
        api_response = api_instance.get_mgi_allele(allele_name)
        print("The response of DefaultApi->get_mgi_allele:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_mgi_allele: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **allele_name** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_perfusions**
> object get_perfusions(subject_id)

Get Perfusions

## Perfusions
Return Perfusions metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    subject_id = '689418' # str | 

    try:
        # Get Perfusions
        api_response = api_instance.get_perfusions(subject_id)
        print("The response of DefaultApi->get_perfusions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_perfusions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subject_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_procedures**
> object get_procedures(subject_id)

Get Procedures

## Procedures
Return Procedure metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    subject_id = '632269' # str | 

    try:
        # Get Procedures
        api_response = api_instance.get_procedures(subject_id)
        print("The response of DefaultApi->get_procedures:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_procedures: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subject_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_project_names**
> object get_project_names()

Get Project Names

Get a list of project names from the Smartsheet API.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)

    try:
        # Get Project Names
        api_response = api_instance.get_project_names()
        print("The response of DefaultApi->get_project_names:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_project_names: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_protocols**
> object get_protocols(protocol_name)

Get Protocols

## Protocols
Return Protocols metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    protocol_name = 'Tetrahydrofuran and Dichloromethane Delipidation of a Whole Mouse Brain' # str | 

    try:
        # Get Protocols
        api_response = api_instance.get_protocols(protocol_name)
        print("The response of DefaultApi->get_protocols:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_protocols: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **protocol_name** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_rig**
> object get_rig(rig_id, partial_match=partial_match)

Get Rig

## Rig
Return a Rig.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    rig_id = '323_EPHYS1_20250205' # str | 
    partial_match = False # bool |  (optional) (default to False)

    try:
        # Get Rig
        api_response = api_instance.get_rig(rig_id, partial_match=partial_match)
        print("The response of DefaultApi->get_rig:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_rig: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rig_id** | **str**|  | 
 **partial_match** | **bool**|  | [optional] [default to False]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_slims_workflow**
> object get_slims_workflow(workflow, subject_id=subject_id, session_name=session_name, start_date_gte=start_date_gte, end_date_lte=end_date_lte)

Get Slims Workflow

## SLIMS
Return information from SLIMS.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.models.slims_workflow import SlimsWorkflow
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    workflow = aind_metadata_service_client.SlimsWorkflow() # SlimsWorkflow | The SLIMS workflow to query.
    subject_id = '744742' # str | Subject ID to filter the data. (optional)
    session_name = 'session_name_example' # str | Name of the session (only for ecephys sessions). (optional)
    start_date_gte = '2025-02-12' # str | Experiment run created on or after. (ISO format) (optional)
    end_date_lte = '2025-02-13' # str | Experiment run created on or before. (ISO format) (optional)

    try:
        # Get Slims Workflow
        api_response = api_instance.get_slims_workflow(workflow, subject_id=subject_id, session_name=session_name, start_date_gte=start_date_gte, end_date_lte=end_date_lte)
        print("The response of DefaultApi->get_slims_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_slims_workflow: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow** | [**SlimsWorkflow**](.md)| The SLIMS workflow to query. | 
 **subject_id** | **str**| Subject ID to filter the data. | [optional] 
 **session_name** | **str**| Name of the session (only for ecephys sessions). | [optional] 
 **start_date_gte** | **str**| Experiment run created on or after. (ISO format) | [optional] 
 **end_date_lte** | **str**| Experiment run created on or before. (ISO format) | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_subject**
> object get_subject(subject_id)

Get Subject

## Subject
Return Subject metadata.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)
    subject_id = '632269' # str | 

    try:
        # Get Subject
        api_response = api_instance.get_subject(subject_id)
        print("The response of DefaultApi->get_subject:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_subject: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subject_id** | **str**|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **index**
> object index()

Index

Returns the index page with search UIs for enabled endpoints.

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with aind_metadata_service_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_client.DefaultApi(api_client)

    try:
        # Index
        api_response = api_instance.index()
        print("The response of DefaultApi->index:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->index: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

