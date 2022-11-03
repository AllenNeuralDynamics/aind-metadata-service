import json
import unittest
from decimal import Decimal
import datetime

from aind_metadata_service.query_builder import LabTracksResponseHandler


class TestLabTracksClient(unittest.TestCase):

    test_response = (
        {'msg': [
            {'id': Decimal('625463'),
             'class_values':
                 '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  <Reserved_by>Anna Lakunina</Reserved_by>\r\n  <Reserve_Date>2022-07-21T00:00:00-07:00</Reserve_Date>\r\n  <Solution>1xPBS</Solution>\r\n  <Full_Genotype>Adora2a-Cre/wt</Full_Genotype>\r\n</MouseCustomClass>',
             'sex': 'M',
             'birth_date': datetime.datetime(2022, 3, 12, 0, 0),
             'mouse_comment': 'PF 10/7/22',
             'paternal_id': Decimal('617425'),
             'paternal_class_values': '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  <Reserved_by>Marie Desierto </Reserved_by>\r\n  <Reserve_Date>2022-06-27T00:00:00</Reserve_Date>\r\n  <Reason>EU-retire</Reason>\r\n  <Full_Genotype>Adora2a-Cre/wt</Full_Genotype>\r\n</MouseCustomClass>',
             'maternal_id': Decimal('618504'),
             'maternal_class_values': '<?xml version="1.0" encoding="utf-16"?>\r\n<MouseCustomClass xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  <Reserved_by>Marie Desierto </Reserved_by>\r\n  <Reserve_Date>2022-06-27T00:00:00</Reserve_Date>\r\n  <Reason>EU-retire</Reason>\r\n  <Full_Genotype>wt/wt</Full_Genotype>\r\n</MouseCustomClass>',
             'species_name': 'mouse'}]})

    expected_subject = json.dumps({
        "describedBy": "https://github.com/AllenNeuralDynamics/data_schema/blob/main/schemas/subject.py",
        "schema_version": "0.2.0",
        "species": "Mus musculus",
        "subject_id": "625463",
        "sex": "Male",
        "date_of_birth": "2022-03-12",
        "genotype": "Adora2a-Cre/wt",
        "maternal_id": "618504",
        "maternal_genotype": "wt/wt",
        "paternal_id": "617425",
        "paternal_genotype": "Adora2a-Cre/wt"})

    def test_map_response_to_subject(self):

        rh = LabTracksResponseHandler()

        actual_subject = rh.map_response_to_subject(self.test_response)

        print(actual_subject)

        self.assertEqual(json.loads(self.expected_subject), json.loads(actual_subject))



if __name__ == "__main__":
    unittest.main()
