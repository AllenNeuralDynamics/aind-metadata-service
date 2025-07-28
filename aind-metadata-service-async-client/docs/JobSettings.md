# JobSettings

Data that needs to be input by user. Can be pulled from env vars with BERGAMO prefix or set explicitly.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_settings_name** | **str** |  | [optional] 
**input_source** | [**InputSource**](InputSource.md) |  | [optional] 
**output_directory** | [**OutputDirectory**](OutputDirectory.md) |  | [optional] 
**user_settings_config_file** | [**UserSettingsConfigFile**](UserSettingsConfigFile.md) |  | [optional] 
**experimenter_full_name** | **List[str]** |  | 
**subject_id** | **str** |  | 
**imaging_laser_wavelength** | **int** |  | 
**fov_imaging_depth** | **int** |  | 
**fov_targeted_structure** | **str** |  | 
**notes** | **str** |  | 
**mouse_platform_name** | **str** |  | [optional] 
**active_mouse_platform** | **bool** |  | [optional] 
**session_type** | **str** |  | [optional] 
**iacuc_protocol** | **str** |  | [optional] 
**rig_id** | **str** |  | [optional] 
**behavior_camera_names** | **List[str]** |  | [optional] 
**ch1_filter_names** | **List[str]** |  | [optional] 
**ch1_detector_name** | **str** |  | [optional] 
**ch1_daq_name** | **str** |  | [optional] 
**ch2_filter_names** | **List[str]** |  | [optional] 
**ch2_detector_name** | **str** |  | [optional] 
**ch2_daq_name** | **str** |  | [optional] 
**imaging_laser_name** | **str** |  | [optional] 
**photostim_laser_name** | **str** |  | [optional] 
**stimulus_device_names** | **List[str]** |  | [optional] 
**photostim_laser_wavelength** | **int** |  | [optional] 
**fov_coordinate_ml** | [**FovCoordinateMl**](FovCoordinateMl.md) |  | [optional] 
**fov_coordinate_ap** | [**FovCoordinateAp**](FovCoordinateAp.md) |  | [optional] 
**fov_reference** | **str** |  | [optional] 
**starting_lickport_position** | [**List[JobSettingsStartingLickportPositionInner]**](JobSettingsStartingLickportPositionInner.md) |  | [optional] 
**behavior_task_name** | **str** |  | [optional] 
**hit_rate_trials_0_10** | [**HitRateTrials010**](HitRateTrials010.md) |  | [optional] 
**hit_rate_trials_20_40** | [**HitRateTrials2040**](HitRateTrials2040.md) |  | [optional] 
**total_hits** | [**TotalHits**](TotalHits.md) |  | [optional] 
**average_hit_rate** | [**AverageHitRate**](AverageHitRate.md) |  | [optional] 
**trial_num** | [**TrialNum**](TrialNum.md) |  | [optional] 
**timezone** | **str** |  | [optional] 
**additional_properties** | **Dict[str, object]** |  | [optional] 

## Example

```python
from aind_metadata_service_async_client.models.job_settings import JobSettings

# TODO update the JSON string below
json = "{}"
# create an instance of JobSettings from a JSON string
job_settings_instance = JobSettings.from_json(json)
# print the JSON string representation of the object
print(JobSettings.to_json())

# convert the object into a dict
job_settings_dict = job_settings_instance.to_dict()
# create an instance of JobSettings from a dict
job_settings_from_dict = JobSettings.from_dict(job_settings_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


