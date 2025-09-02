# aind_metadata_service_client.HealthcheckApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_health**](HealthcheckApi.md#get_health) | **GET** /api/v2/healthcheck | Perform a Health Check


# **get_health**
> HealthCheck get_health()

Perform a Health Check

## Endpoint to perform a healthcheck on.

Returns:
    HealthCheck: Returns a JSON response with the health status

### Example


```python
import aind_metadata_service_client
from aind_metadata_service_client.models.health_check import HealthCheck
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
    api_instance = aind_metadata_service_client.HealthcheckApi(api_client)

    try:
        # Perform a Health Check
        api_response = api_instance.get_health()
        print("The response of HealthcheckApi->get_health:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthcheckApi->get_health: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HealthCheck**](HealthCheck.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return HTTP Status Code 200 (OK) |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

