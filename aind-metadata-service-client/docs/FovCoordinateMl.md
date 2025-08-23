# FovCoordinateMl

FovCoordinateMl

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**anyof_schema_1_validator** | [**AnyofSchema1Validator**](AnyofSchema1Validator.md) |  | [optional] 
**anyof_schema_2_validator** | **str** |  | [optional] 
**actual_instance** | **object** |  | [optional] 
**any_of_schemas** | **List[str]** |  | [optional] [default to [str, float]]

## Example

```python
from aind_metadata_service_client.models.fov_coordinate_ml import FovCoordinateMl

# TODO update the JSON string below
json = "{}"
# create an instance of FovCoordinateMl from a JSON string
fov_coordinate_ml_instance = FovCoordinateMl.from_json(json)
# print the JSON string representation of the object
print(FovCoordinateMl.to_json())

# convert the object into a dict
fov_coordinate_ml_dict = fov_coordinate_ml_instance.to_dict()
# create an instance of FovCoordinateMl from a dict
fov_coordinate_ml_from_dict = FovCoordinateMl.from_dict(fov_coordinate_ml_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


