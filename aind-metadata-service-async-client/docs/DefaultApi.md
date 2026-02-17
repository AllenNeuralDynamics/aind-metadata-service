# aind_metadata_service_async_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_dataverse_table**](DefaultApi.md#get_dataverse_table) | **GET** /api/v2/dataverse/tables/{entity_set_table_name} | Get Dataverse Table
[**get_dataverse_table_info**](DefaultApi.md#get_dataverse_table_info) | **GET** /api/v2/dataverse/tables | Get Dataverse Table Info
[**get_funding**](DefaultApi.md#get_funding) | **GET** /api/v2/funding/{project_name} | Get Funding
[**get_injection_materials**](DefaultApi.md#get_injection_materials) | **GET** /api/v2/tars_injection_materials/{prep_lot_number} | Get Injection Materials
[**get_instrument**](DefaultApi.md#get_instrument) | **GET** /api/v2/instrument/{instrument_id} | Get Instrument
[**get_intended_measurements**](DefaultApi.md#get_intended_measurements) | **GET** /api/v2/intended_measurements/{subject_id} | Get Intended Measurements
[**get_investigators**](DefaultApi.md#get_investigators) | **GET** /api/v2/investigators/{project_name} | Get Investigators
[**get_labtracks_subject**](DefaultApi.md#get_labtracks_subject) | **GET** /api/v2/labtracks/subject | Get Labtracks Subject
[**get_mgi_allele**](DefaultApi.md#get_mgi_allele) | **GET** /api/v2/mgi_allele/{allele_name} | Get Mgi Allele
[**get_perfusions**](DefaultApi.md#get_perfusions) | **GET** /api/v2/perfusions/{subject_id} | Get Perfusions
[**get_procedures**](DefaultApi.md#get_procedures) | **GET** /api/v2/procedures/{subject_id} | Get Procedures
[**get_project_names**](DefaultApi.md#get_project_names) | **GET** /api/v2/project_names | Get Project Names
[**get_protocols**](DefaultApi.md#get_protocols) | **GET** /api/v2/protocols/{protocol_name} | Get Protocols
[**get_rig**](DefaultApi.md#get_rig) | **GET** /api/v2/rig/{rig_id} | Get Rig
[**get_slims_workflow**](DefaultApi.md#get_slims_workflow) | **GET** /api/v2/slims/{workflow} | Get Slims Workflow
[**get_smartsheet_funding**](DefaultApi.md#get_smartsheet_funding) | **GET** /api/v2/smartsheet/funding | Get Smartsheet Funding
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
[**post_instrument**](DefaultApi.md#post_instrument) | **POST** /api/v2/instrument | Post Instrument


# **get_dataverse_table**
> object get_dataverse_table(entity_set_table_name)

Get Dataverse Table

## Table Data
Retrieves data for a specific entity table in Dataverse.

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
    entity_set_table_name = 'cr138_projects' # str | The entity set name of the table to fetch

    try:
        # Get Dataverse Table
        api_response = await api_instance.get_dataverse_table(entity_set_table_name)
        print("The response of DefaultApi->get_dataverse_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_dataverse_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **entity_set_table_name** | **str**| The entity set name of the table to fetch | 

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

# **get_dataverse_table_info**
> object get_dataverse_table_info()

Get Dataverse Table Info

## Entity table identifying information
Retrieves identifying information for all table entities in Dataverse.

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
        # Get Dataverse Table Info
        api_response = await api_instance.get_dataverse_table_info()
        print("The response of DefaultApi->get_dataverse_table_info:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_dataverse_table_info: %s\n" % e)
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

# **get_funding**
> object get_funding(project_name)

Get Funding

## Funding
Return Funding metadata.

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
    project_name = 'Thalamus in the middle - Project 1 Mesoscale thalamic circuits' # str | 

    try:
        # Get Funding
        api_response = await api_instance.get_funding(project_name)
        print("The response of DefaultApi->get_funding:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_funding: %s\n" % e)
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

# **get_injection_materials**
> object get_injection_materials(prep_lot_number)

Get Injection Materials

## Injection Materials
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
        # Get Injection Materials
        api_response = await api_instance.get_injection_materials(prep_lot_number)
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
        # Get Instrument
        api_response = await api_instance.get_instrument(instrument_id, partial_match=partial_match)
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
        # Get Intended Measurements
        api_response = await api_instance.get_intended_measurements(subject_id)
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

# **get_investigators**
> object get_investigators(project_name)

Get Investigators

## Funding
Return Funding metadata.

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
    project_name = 'Thalamus in the middle - Project 1 Mesoscale thalamic circuits' # str | 

    try:
        # Get Investigators
        api_response = await api_instance.get_investigators(project_name)
        print("The response of DefaultApi->get_investigators:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_investigators: %s\n" % e)
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

# **get_labtracks_subject**
> object get_labtracks_subject(subject_id)

Get Labtracks Subject

## LabTracks Subject
Return LabTracks Subject metadata.

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
        # Get Labtracks Subject
        api_response = await api_instance.get_labtracks_subject(subject_id)
        print("The response of DefaultApi->get_labtracks_subject:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_labtracks_subject: %s\n" % e)
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
        # Get Mgi Allele
        api_response = await api_instance.get_mgi_allele(allele_name)
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
        # Get Perfusions
        api_response = await api_instance.get_perfusions(subject_id)
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

# **get_project_names**
> object get_project_names()

Get Project Names

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
        # Get Project Names
        api_response = await api_instance.get_project_names()
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
        # Get Protocols
        api_response = await api_instance.get_protocols(protocol_name)
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
        # Get Rig
        api_response = await api_instance.get_rig(rig_id, partial_match=partial_match)
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
        # Get Slims Workflow
        api_response = await api_instance.get_slims_workflow(workflow, subject_id=subject_id, session_name=session_name, start_date_gte=start_date_gte, end_date_lte=end_date_lte)
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

# **get_smartsheet_funding**
> object get_smartsheet_funding()

Get Smartsheet Funding

Get raw funding data from Smartsheet.

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
        # Get Smartsheet Funding
        api_response = await api_instance.get_smartsheet_funding()
        print("The response of DefaultApi->get_smartsheet_funding:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_smartsheet_funding: %s\n" % e)
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

Return funding metadata for a given project.

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

# **post_instrument**
> object post_instrument(request_body, replace=replace)

Post Instrument

## Instrument
Save an instrument to a database.

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
    replace = False # bool |  (optional) (default to False)

    try:
        # Post Instrument
        api_response = await api_instance.post_instrument(request_body, replace=replace)
        print("The response of DefaultApi->post_instrument:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->post_instrument: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  | 
 **replace** | **bool**|  | [optional] [default to False]

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

