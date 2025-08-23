# InputSource

Location or locations of data sources to parse for metadata.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anyof_schema_1_validator** | **str** |  | [optional] 
**anyof_schema_2_validator** | **str** |  | [optional] 
**anyof_schema_3_validator** | **List[str]** |  | [optional] 
**anyof_schema_4_validator** | **List[str]** |  | [optional] 
**actual_instance** | **object** |  | [optional] 
**any_of_schemas** | **List[str]** |  | [optional] [default to [str, List[str]]]

## Example

```python
from aind_metadata_service_async_client.models.input_source import InputSource

# TODO update the JSON string below
json = "{}"
# create an instance of InputSource from a JSON string
input_source_instance = InputSource.from_json(json)
# print the JSON string representation of the object
print(InputSource.to_json())

# convert the object into a dict
input_source_dict = input_source_instance.to_dict()
# create an instance of InputSource from a dict
input_source_from_dict = InputSource.from_dict(input_source_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


