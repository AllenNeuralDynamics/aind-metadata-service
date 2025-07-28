# OutputDirectory

Location to metadata file data to. None to return object.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anyof_schema_1_validator** | **str** |  | [optional] 
**anyof_schema_2_validator** | **str** |  | [optional] 
**actual_instance** | **object** |  | [optional] 
**any_of_schemas** | **List[str]** |  | [optional] [default to [str]]

## Example

```python
from aind_metadata_service_client.models.output_directory import OutputDirectory

# TODO update the JSON string below
json = "{}"
# create an instance of OutputDirectory from a JSON string
output_directory_instance = OutputDirectory.from_json(json)
# print the JSON string representation of the object
print(OutputDirectory.to_json())

# convert the object into a dict
output_directory_dict = output_directory_instance.to_dict()
# create an instance of OutputDirectory from a dict
output_directory_from_dict = OutputDirectory.from_dict(output_directory_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


