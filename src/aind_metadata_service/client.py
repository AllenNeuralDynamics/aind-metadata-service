import pyodbc
from flask.json import JSONEncoder
from datetime import date


class LabTracksClient:

    class CustomJSONEncoder(JSONEncoder):
        def default(self, obj):
            try:
                if isinstance(obj, date):
                    return obj.isoformat()
                iterable = iter(obj)
            except TypeError:
                pass
            else:
                return list(iterable)
            return JSONEncoder.default(self, obj)

    def __init__(self, driver, server, port, db, user, password):
        self.driver = driver
        self.server = server
        self.port = port
        self.db = db
        self.user = user
        self.password = password
        self.connection_str = (f"Driver={driver};"
                               f"Server={server};"
                               f"Port={port};"
                               f"Database={db};"
                               f"UID={user};"
                               f"PWD={password};")

    def create_session(self):
        return pyodbc.connect(self.connection_str)

    @staticmethod
    def submit_query(session, query):
        try:
            cursor = session.cursor()
            cursor.execute(query)
            columns = [column[0].lower() for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return {'msg': results}
        except pyodbc.ProgrammingError:
            return {'msg': "Something went wrong"}

    @staticmethod
    def close_session(session):
        session.close()

    @staticmethod
    def handle_response(response):
        msg = response['msg']
        if msg != "Something went wrong":
            return msg[0]
        else:
            return msg
