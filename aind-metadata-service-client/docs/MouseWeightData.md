# MouseWeightData

Class for Mouse Weight Data with proper datetime info

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**record_id** | **str** |  | [optional] 
**mouse_id** | **str** |  | [optional] 
**weight** | **float** |  | [optional] 
**weight_datetime** | **datetime** |  | [optional] 
**is_baseline_weight** | **bool** |  | [optional] 
**operator** | **str** |  | [optional] 
**workstation** | **str** |  | [optional] 
**software_version** | **str** |  | [optional] 
**software_source** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**notes** | **str** |  | [optional] 

## Example

```python
from aind_metadata_service_client.models.mouse_weight_data import MouseWeightData

# TODO update the JSON string below
json = "{}"
# create an instance of MouseWeightData from a JSON string
mouse_weight_data_instance = MouseWeightData.from_json(json)
# print the JSON string representation of the object
print(MouseWeightData.to_json())

# convert the object into a dict
mouse_weight_data_dict = mouse_weight_data_instance.to_dict()
# create an instance of MouseWeightData from a dict
mouse_weight_data_from_dict = MouseWeightData.from_dict(mouse_weight_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


