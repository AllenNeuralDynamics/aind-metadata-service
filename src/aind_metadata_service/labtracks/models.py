from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
import xml.etree.ElementTree as ET
from datetime import datetime

RAW_RESPONSE_EXAMPLE = [
    {'id': Decimal('632269'),
     'class_values': (
         '<?xml version="1.0" encoding="utf-16"?>\r\n'
         '<MouseCustomClass xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  '
         '<Reserved_by>Anna Apple</Reserved_by>\r\n  '
         '<Reserve_Date>2022-07-14T00:00:00-07:00</Reserve_Date>\r\n  '
         '<Solution>1xPBS</Solution>\r\n  '
         '<Full_Genotype>'
         'Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt'
         '</Full_Genotype>\r\n  '
         '<Phenotype>P19: TSTW. Small body, large head, slightly '
         'dehydrated. 3.78g. P22: 5.59g. P26: 8.18g. '
         'Normal body proportions. '
         '</Phenotype>\r\n'
         '</MouseCustomClass>'
     ),
     'sex': 'F',
     'birth_date': datetime(2022, 5, 1, 0, 0),
     'paternal_id': Decimal('623236'),
     'paternal_class_values': (
         '<?xml version="1.0" encoding="utf-16"?>\r\n'
         '<MouseCustomClass xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  '
         '<Reserved_by>Jane Smith </Reserved_by>\r\n  '
         '<Reserve_Date>2022-11-01T00:00:00</Reserve_Date>\r\n  '
         '<Reason>eu-retire</Reason>\r\n  '
         '<Full_Genotype>'
         'RCL-somBiPoles_mCerulean-WPRE/wt'
         '</Full_Genotype>\r\n  '
         '<Phenotype>P87: F.G. P133: Barberer. '
         '</Phenotype>\r\n'
         '</MouseCustomClass>'
     ),
     'maternal_id': Decimal('615310'),
     'maternal_class_values': (
         '<?xml version="1.0" encoding="utf-16"?>\r\n'
         '<MouseCustomClass xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
         'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\r\n  '
         '<Reserved_by>Jane Smith </Reserved_by>\r\n  '
         '<Reserve_Date>2022-08-03T00:00:00</Reserve_Date>\r\n  '
         '<Reason>Eu-retire</Reason>\r\n  '
         '<Full_Genotype>Pvalb-IRES-Cre/wt</Full_Genotype>\r\n  '
         '<Phenotype>P100: F.G.</Phenotype>\r\n</MouseCustomClass>'
     ),
     'species_name': 'mouse',
     'group_name': 'Pvalb-IRES-Cre;RCL-somBiPoles_mCerulean-WPRE(ND)',
     'group_description': None,
     'cage_id': Decimal('-99999999999999'),
     'room_id': Decimal('-99999999999999')}]


class SubjectResponse(BaseModel):
    """Expected response for subject query"""

    id: Decimal = Field(...)
    class_values: Optional[str] = Field(None)
    sex: Optional[str] = Field(None)
    birth_date: Optional[datetime] = Field(None)
    paternal_id: Optional[Decimal] = Field(None)
    paternal_class_values = Field(None)
    maternal_id: Optional[Decimal] = Field(None)
    maternal_class_values: Optional[str] = Field(None)
    species_name: Optional[str] = Field(None)
    group_name: Optional[str] = Field(None)
    group_description: Optional[str] = Field(None)
    cage_id: Optional[Decimal] = Field(None)
    room_id: Optional[Decimal] = Field(None)


class MouseCustomClass(BaseModel):
    """Some class_values fields are XML strings"""

    reserved_by: Optional[str] = Field(None)
    reserved_date: Optional[datetime] = Field(None)
    reason: Optional[str] = Field(None)
    full_genotype: Optional[str] = Field(None)
    phenotype: Optional[str] = Field(None)

    @classmethod
    def from_xml_string(cls, xml_string: str):
        root = ET.fromstring(xml_string)


    '<Reserved_by>Jane Smith </Reserved_by>\r\n  '
    '<Reserve_Date>2022-08-03T00:00:00</Reserve_Date>\r\n  '
    '<Reason>Eu-retire</Reason>\r\n  '
    '<Full_Genotype>Pvalb-IRES-Cre/wt</Full_Genotype>\r\n  '
    '<Phenotype>P100: F.G.</Phenotype>\r\n</MouseCustomClass>'
