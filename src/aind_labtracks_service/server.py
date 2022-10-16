from flask import Flask, request, jsonify
from client import LabTracksClient
import query_builder
import os

app = Flask(__name__)
app.json_encoder = LabTracksClient.CustomJSONEncoder

driver = os.getenv('ODBC_DRIVER')
server = os.getenv('LABTRACKS_SERVER')
port = os.getenv('LABTRACKS_PORT')
db = os.getenv('LABTRACKS_DATABASE')
user = os.getenv('LABTRACKS_USER')
password = os.getenv('LABTRACKS_PASSWORD')
flask_host = os.getenv('FLASK_HOST')

lb_client = LabTracksClient(driver=driver,
                            server=server,
                            port=port,
                            db=db,
                            user=user,
                            password=password)


@app.route('/', methods=['GET'])
def query_records():
    species_id = request.args.get('species_id')
    query = query_builder.subject_from_species_id(species_id)
    session = lb_client.create_session()
    lb_response = lb_client.submit_query(session, query)
    lb_client.close_session(session)
    return jsonify(lb_response)


if __name__ == "__main__":
    app.run(host=flask_host)
