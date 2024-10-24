from aind_metadata_service.slims.client import SlimsSettings, SlimsHandler

settings = SlimsSettings(
    username="general_aind",
    password='Jm0G8Z1fp>&".354',
    host="https://aind-test.us.slims.agilent.com/slimsrest/",
    db="test"
)
h = SlimsHandler(settings)

model_response = h.get_sessions_model_response(subject_id="725804")

print(model_response.status_code)
print(model_response.aind_models)