# aind_metadata_service_async_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_procedures**](DefaultApi.md#get_procedures) | **GET** /api/v2/procedures/{subject_id} | Get Procedures
[**get_subject**](DefaultApi.md#get_subject) | **GET** /api/v2/subject/{subject_id} | Get Subject
[**get_v1_bergamo_session**](DefaultApi.md#get_v1_bergamo_session) | **POST** /bergamo_session | Get V1 Bergamo Session
[**get_v1_funding**](DefaultApi.md#get_v1_funding) | **GET** /funding/{project_name} | Get V1 Funding
[**get_v1_injection_materials**](DefaultApi.md#get_v1_injection_materials) | **GET** /tars_injection_materials/{prep_lot_number} | Get V1 Injection Materials
[**get_v1_instrument**](DefaultApi.md#get_v1_instrument) | **GET** /instrument/{instrument_id} | Get V1 Instrument
[**get_v1_intended_measurements**](DefaultApi.md#get_v1_intended_measurements) | **GET** /intended_measurements/{subject_id} | Get V1 Intended Measurements
[**get_v1_mgi_allele**](DefaultApi.md#get_v1_mgi_allele) | **GET** /mgi_allele/{allele_name} | Get V1 Mgi Allele
[**get_v1_perfusions**](DefaultApi.md#get_v1_perfusions) | **GET** /perfusions/{subject_id} | Get V1 Perfusions
[**get_v1_procedures**](DefaultApi.md#get_v1_procedures) | **GET** /procedures/{subject_id} | Get V1 Procedures
[**get_v1_project_names**](DefaultApi.md#get_v1_project_names) | **GET** /project_names | Get V1 Project Names
[**get_v1_protocols**](DefaultApi.md#get_v1_protocols) | **GET** /protocols/{protocol_name} | Get V1 Protocols
[**get_v1_rig**](DefaultApi.md#get_v1_rig) | **GET** /rig/{rig_id} | Get V1 Rig
[**get_v1_slims_workflow**](DefaultApi.md#get_v1_slims_workflow) | **GET** /slims/{workflow} | Get V1 Slims Workflow
[**get_v1_subject**](DefaultApi.md#get_v1_subject) | **GET** /subject/{subject_id} | Get V1 Subject
[**index**](DefaultApi.md#index) | **GET** / | Index


# **get_procedures**
> object get_procedures(subject_id)

Get Procedures

## Procedures
Return Procedure metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    subject_id = '823508' # str | 

    try:
        # Get Procedures
        api_response = await api_instance.get_procedures(subject_id)
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

# **get_subject**
> object get_subject(subject_id)

Get Subject

## Subject
Return Subject metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    subject_id = '632269' # str | 

    try:
        # Get Subject
        api_response = await api_instance.get_subject(subject_id)
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

# **get_v1_bergamo_session**
> object get_v1_bergamo_session(request_body)

Get V1 Bergamo Session

## Session
Return session metadata computed from aind-metadata-mapper.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    request_body = None # Dict[str, object] | 

    try:
        # Get V1 Bergamo Session
        api_response = await api_instance.get_v1_bergamo_session(request_body)
        print("The response of DefaultApi->get_v1_bergamo_session:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_bergamo_session: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  | 

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

# **get_v1_funding**
> object get_v1_funding(project_name)

Get V1 Funding

## Procedures V1
Return Procedure metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    project_name = 'Discovery-Neuromodulator circuit dynamics during foraging' # str | 

    try:
        # Get V1 Funding
        api_response = await api_instance.get_v1_funding(project_name)
        print("The response of DefaultApi->get_v1_funding:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_funding: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **project_name** | **str**|  | 

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

# **get_v1_injection_materials**
> object get_v1_injection_materials(prep_lot_number)

Get V1 Injection Materials

## Injection Materials V1
Return Injection Materials metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    prep_lot_number = 'VT3214G' # str | 

    try:
        # Get V1 Injection Materials
        api_response = await api_instance.get_v1_injection_materials(prep_lot_number)
        print("The response of DefaultApi->get_v1_injection_materials:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_injection_materials: %s\n" % e)
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

# **get_v1_instrument**
> object get_v1_instrument(instrument_id, partial_match=partial_match)

Get V1 Instrument

## Instrument v1
Return an Instrument.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    instrument_id = '440_SmartSPIM1_20240327' # str | 
    partial_match = False # bool |  (optional) (default to False)

    try:
        # Get V1 Instrument
        api_response = await api_instance.get_v1_instrument(instrument_id, partial_match=partial_match)
        print("The response of DefaultApi->get_v1_instrument:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_instrument: %s\n" % e)
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

# **get_v1_intended_measurements**
> object get_v1_intended_measurements(subject_id)

Get V1 Intended Measurements

## Intended Measurements V1
Return Intended Measurements metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    subject_id = '775745' # str | 

    try:
        # Get V1 Intended Measurements
        api_response = await api_instance.get_v1_intended_measurements(subject_id)
        print("The response of DefaultApi->get_v1_intended_measurements:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_intended_measurements: %s\n" % e)
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

# **get_v1_mgi_allele**
> object get_v1_mgi_allele(allele_name)

Get V1 Mgi Allele

## MGI Allele
Return MGI Allele metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    allele_name = 'Parvalbumin-IRES-Cre' # str | 

    try:
        # Get V1 Mgi Allele
        api_response = await api_instance.get_v1_mgi_allele(allele_name)
        print("The response of DefaultApi->get_v1_mgi_allele:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_mgi_allele: %s\n" % e)
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

# **get_v1_perfusions**
> object get_v1_perfusions(subject_id)

Get V1 Perfusions

## Perfusions V1
Return Perfusions metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    subject_id = '689418' # str | 

    try:
        # Get V1 Perfusions
        api_response = await api_instance.get_v1_perfusions(subject_id)
        print("The response of DefaultApi->get_v1_perfusions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_perfusions: %s\n" % e)
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

# **get_v1_procedures**
> object get_v1_procedures(subject_id)

Get V1 Procedures

## Procedures V1
Return Procedure metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    subject_id = '632269' # str | 

    try:
        # Get V1 Procedures
        api_response = await api_instance.get_v1_procedures(subject_id)
        print("The response of DefaultApi->get_v1_procedures:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_procedures: %s\n" % e)
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

# **get_v1_project_names**
> object get_v1_project_names()

Get V1 Project Names

Get a list of project names from the Smartsheet API.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)

    try:
        # Get V1 Project Names
        api_response = await api_instance.get_v1_project_names()
        print("The response of DefaultApi->get_v1_project_names:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_project_names: %s\n" % e)
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

# **get_v1_protocols**
> object get_v1_protocols(protocol_name)

Get V1 Protocols

## Protocols
Return Protocols metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    protocol_name = 'Tetrahydrofuran and Dichloromethane Delipidation of a Whole Mouse Brain' # str | 

    try:
        # Get V1 Protocols
        api_response = await api_instance.get_v1_protocols(protocol_name)
        print("The response of DefaultApi->get_v1_protocols:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_protocols: %s\n" % e)
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

# **get_v1_rig**
> object get_v1_rig(rig_id, partial_match=partial_match)

Get V1 Rig

## Rig V1
Return a Rig.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    rig_id = '323_EPHYS1_20250205' # str | 
    partial_match = False # bool |  (optional) (default to False)

    try:
        # Get V1 Rig
        api_response = await api_instance.get_v1_rig(rig_id, partial_match=partial_match)
        print("The response of DefaultApi->get_v1_rig:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_rig: %s\n" % e)
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

# **get_v1_slims_workflow**
> object get_v1_slims_workflow(workflow, subject_id=subject_id, session_name=session_name, start_date_gte=start_date_gte, end_date_lte=end_date_lte)

Get V1 Slims Workflow

## SLIMS V1
Return information from SLIMS.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.models.slims_workflow import SlimsWorkflow
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    workflow = aind_metadata_service_async_client.SlimsWorkflow() # SlimsWorkflow | The SLIMS workflow to query.
    subject_id = '744742' # str | Subject ID to filter the data. (optional)
    session_name = 'session_name_example' # str | Name of the session (only for ecephys sessions). (optional)
    start_date_gte = '2025-02-12' # str | Experiment run created on or after. (ISO format) (optional)
    end_date_lte = '2025-02-13' # str | Experiment run created on or before. (ISO format) (optional)

    try:
        # Get V1 Slims Workflow
        api_response = await api_instance.get_v1_slims_workflow(workflow, subject_id=subject_id, session_name=session_name, start_date_gte=start_date_gte, end_date_lte=end_date_lte)
        print("The response of DefaultApi->get_v1_slims_workflow:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_slims_workflow: %s\n" % e)
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

# **get_v1_subject**
> object get_v1_subject(subject_id)

Get V1 Subject

## Subject V1
Return Subject metadata.

### Example


```python
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)
    subject_id = '632269' # str | 

    try:
        # Get V1 Subject
        api_response = await api_instance.get_v1_subject(subject_id)
        print("The response of DefaultApi->get_v1_subject:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_v1_subject: %s\n" % e)
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
import aind_metadata_service_async_client
from aind_metadata_service_async_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = aind_metadata_service_async_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with aind_metadata_service_async_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = aind_metadata_service_async_client.DefaultApi(api_client)

    try:
        # Index
        api_response = await api_instance.index()
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

