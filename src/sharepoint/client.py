"""Module to create client to connect to sharepoint database"""

import sharepy


class SharePointClient:
    """This class contains the api to connect to Sharepoint NSB Database"""

    def __init__(
        self,
        server: str,
        db: str,
        user: str,
        password: str
    ) -> None:
        self.server = server
        self.db = db
        self.user = user
        self.password = password

    def create_session(self) -> sharepy.connection:
        """
        Initiates sharepoint session.

        Parameters
        ----------
        self.server: example.sharepoint.com
        """
        return sharepy.connect(self.server)

    def api_call(self, session: sharepy.connection):
        """
        Makes API Call

        Parameters
        ----------
        session: sharepoint session
        self.db: https://alleninstitute.sharepoint.com/BrainScience/IVS/Neurosurgery-Behavior/Lists/SWR%202018Present/New%20Request.aspx

        Returns
        -------
        Requests response object
        """
        return session.get(self.db)





