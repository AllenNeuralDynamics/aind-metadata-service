"""Starts and runs a Flask Service"""

import os
from datetime import date
from typing import Any

from flask import Flask, jsonify, request
from flask.json import JSONEncoder

from aind_metadata_service.labtracks.client import LabTracksClient
from aind_metadata_service.labtracks.query_builder import LabTracksQueries


class CustomJSONEncoder(JSONEncoder):  # pragma: no cover
    """This class customizes the json returned by sqlserver.
    TODO: There is a warning that using JSONEncoder is deprecated?
    """

    def default(self, obj: Any) -> Any:
        """
        Formats date objects into iso standard.

        Parameters
        ----------
        obj : Any
            Some object in the json

        Returns
        -------
            Any
                Returns the original object if not type date, otherwise
                returns the date object formatted in iso standard.

        """

        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


if __name__ == "__main__":
    # TODO: Handle configs better?
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder

    driver = os.getenv("ODBC_DRIVER")
    server = os.getenv("LABTRACKS_SERVER")
    port = os.getenv("LABTRACKS_PORT")
    db = os.getenv("LABTRACKS_DATABASE")
    user = os.getenv("LABTRACKS_USER")
    password = os.getenv("LABTRACKS_PASSWORD")
    flask_host = os.getenv("FLASK_HOST")

    lb_client = LabTracksClient(
        driver=driver,
        server=server,
        port=port,
        db=db,
        user=user,
        password=password,
    )

    @app.route("/", methods=["GET"])
    def query_records():
        """
        Receives a GET request with parameters.
        Returns
        -------
            jsonify
                Appropriate records
        """
        specimen_id = request.args.get("specimen_id")
        query = LabTracksQueries.subject_from_specimen_id(specimen_id)
        session = lb_client.create_session()
        lb_response = lb_client.submit_query(session, query)
        lb_client.close_session(session)
        handled_response = lb_client.handle_response(lb_response)
        return handled_response

    app.run(host=flask_host)
