"""Models and schema definitions for LabTracks backend data structures"""

import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from xml.etree.ElementTree import ParseError

from pydantic import ValidationError, field_validator
from pydantic_xml import BaseXmlModel, ParsingError, element
from sqlmodel import Field, SQLModel


class SexNames(str, Enum):
    """How LabTracks labels the sex of the species."""

    MALE = "M"
    FEMALE = "F"


class SpeciesNames(str, Enum):
    """How LabTracks stores the name of the species."""

    MOUSE = "mouse"
    RAT = "rat"


class BgStrains(str, Enum):
    """How LabTracks labels its strains"""

    C57BL_6J = "C57BL/6J"
    # noinspection SpellCheckingInspection
    BALB_C = "BALB/c"


class AnimalsCommon(SQLModel, table=True):
    """AnimalsCommon Table schema auto generated from script"""

    # Actual table name has an underscore
    # noinspection SpellCheckingInspection
    __tablename__ = "Animals_Common"

    id: Decimal = Field(..., alias="ID", primary_key=True)
    class_def_id: Optional[Decimal] = Field(default=None, alias="Class_Def_ID")
    class_values: Optional[str] = Field(default=None, alias="Class_Values")
    animal_class: Optional[str] = Field(default=None, alias="Animal_Class")
    group_id: Optional[Decimal] = Field(default=None, alias="Group_ID")
    facility_id: Optional[Decimal] = Field(default=None, alias="Facility_ID")
    rent_item_id: Optional[Decimal] = Field(default=None, alias="Rent_Item_ID")
    is_hidden: Optional[str] = Field(default=None, alias="Is_Hidden")
    shipping_status: Optional[str] = Field(
        default=None, alias="Shipping_Status"
    )
    animal_status: Optional[str] = Field(default=None, alias="Animal_Status")
    pedigree_number: Optional[Decimal] = Field(
        default=None, alias="Pedigree_Number"
    )
    pedigree_prefix: Optional[str] = Field(
        default=None, alias="Pedigree_Prefix"
    )
    pedigree_suffix: Optional[str] = Field(
        default=None, alias="Pedigree_Suffix"
    )
    # noinspection SpellCheckingInspection
    composite_pednum: Optional[str] = Field(
        default=None, alias="Composite_Pednum"
    )
    order_id: Optional[Decimal] = Field(default=None, alias="Order_ID")
    vendor_id: Optional[Decimal] = Field(default=None, alias="Vendor_ID")
    arrival_date: Optional[datetime] = Field(
        default=None, alias="Arrival_Date"
    )
    g_user_1: Optional[str] = Field(default=None, alias="G_User_1")
    g_user_2: Optional[str] = Field(default=None, alias="G_User_2")
    g_user_3: Optional[str] = Field(default=None, alias="G_User_3")
    g_user_4: Optional[str] = Field(default=None, alias="G_User_4")
    # noinspection SpellCheckingInspection
    tailtip_date: Optional[datetime] = Field(
        default=None, alias="Tailtip_Date"
    )
    wean_date: Optional[datetime] = Field(default=None, alias="Wean_Date")
    biopsy_date: Optional[datetime] = Field(default=None, alias="Biopsy_Date")
    gc_number: Optional[str] = Field(default=None, alias="GC_Number")
    filial_generation: Optional[str] = Field(
        default=None, alias="Filial_Generation"
    )
    # noinspection SpellCheckingInspection
    filial_backcross: Optional[str] = Field(
        default=None, alias="Filial_Backcross"
    )
    bkg_percent: Optional[Decimal] = Field(default=None, alias="Bkg_Percent")
    breeding_start: Optional[datetime] = Field(
        default=None, alias="Breeding_Start"
    )
    breeding_end: Optional[datetime] = Field(
        default=None, alias="Breeding_End"
    )
    investigator_id: Optional[Decimal] = Field(
        default=None, alias="Investigator_ID"
    )
    grant_id: Optional[Decimal] = Field(default=None, alias="Grant_Id")
    # noinspection SpellCheckingInspection
    acuc_link_id: Optional[Decimal] = Field(default=None, alias="ACUC_Link_ID")
    usda_code: Optional[str] = Field(default=None, alias="USDA_Code")
    species_id: Optional[Decimal] = Field(default=None, alias="Species_ID")
    mouse_comment: Optional[str] = Field(default=None, alias="Mouse_Comment")
    paternal_index: Optional[Decimal] = Field(
        default=None, alias="Paternal_Index"
    )
    maternal_index: Optional[Decimal] = Field(
        default=None, alias="Maternal_Index"
    )
    paternal_number: Optional[str] = Field(
        default=None, alias="Paternal_Number"
    )
    maternal_number: Optional[str] = Field(
        default=None, alias="Maternal_Number"
    )
    litter_history_id: Optional[Decimal] = Field(
        default=None, alias="Litter_History_ID"
    )
    foster_female_id: Optional[Decimal] = Field(
        default=None, alias="Foster_Female_ID"
    )
    # noinspection SpellCheckingInspection
    vasectomized_male_id: Optional[Decimal] = Field(
        default=None, alias="Vasectomized_Male_ID"
    )
    age: Optional[Decimal] = Field(default=None, alias="Age")
    birth_date: Optional[datetime] = Field(default=None, alias="Birth_Date")
    late_birth_date: Optional[datetime] = Field(
        default=None, alias="Late_Birth_Date"
    )
    is_dead: Optional[str] = Field(default=None, alias="Is_Dead")
    death_date: Optional[datetime] = Field(default=None, alias="Death_Date")
    death_cause: Optional[str] = Field(default=None, alias="Death_Cause")
    coat_color: Optional[str] = Field(default=None, alias="Coat_Color")
    sex: Optional[str] = Field(default=None, alias="Sex")
    disposition: Optional[str] = Field(default=None, alias="Disposition")
    disposition_date: Optional[datetime] = Field(
        default=None, alias="Disposition_Date"
    )
    transponder_code: Optional[str] = Field(
        default=None, alias="Transponder_Code"
    )
    ear_code: Optional[str] = Field(default=None, alias="Ear_Code")
    strain_id: Optional[Decimal] = Field(default=None, alias="Strain_ID")
    strain_code: Optional[str] = Field(default=None, alias="Strain_Code")
    tattoo: Optional[str] = Field(default=None, alias="Tattoo")
    study_number: Optional[str] = Field(default=None, alias="Study_Number")
    other_value: Optional[str] = Field(default=None, alias="Other_Value")
    genotype: Optional[str] = Field(default=None, alias="Genotype")
    genotype_source: Optional[str] = Field(
        default=None, alias="Genotype_Source"
    )
    implantation_date: Optional[datetime] = Field(
        default=None, alias="Implantation_Date"
    )
    ho_origin: Optional[str] = Field(default=None, alias="HO_Origin")
    ho_genetic_status: Optional[str] = Field(
        default=None, alias="HO_Genetic_Status"
    )
    ho_new_genetic_line: Optional[str] = Field(
        default=None, alias="HO_New_Genetic_Line"
    )
    ho_purpose: Optional[str] = Field(default=None, alias="HO_Purpose")
    cage_id: Optional[Decimal] = Field(default=None, alias="Cage_ID")
    cage_number: Optional[str] = Field(default=None, alias="Cage_Number")
    room_id: Optional[Decimal] = Field(default=None, alias="Room_ID")
    rack_id: Optional[Decimal] = Field(default=None, alias="Rack_ID")
    scanned_row: Optional[Decimal] = Field(default=None, alias="Scanned_Row")
    scanned_col: Optional[Decimal] = Field(default=None, alias="Scanned_Col")
    scanned_side: Optional[Decimal] = Field(default=None, alias="Scanned_Side")
    animal_disposal_rent_item_id: Optional[Decimal] = Field(
        default=None, alias="Animal_Disposal_Rent_Item_ID"
    )
    animal_transfer_rent_item_id: Optional[Decimal] = Field(
        default=None, alias="Animal_Transfer_Rent_Item_ID"
    )
    external_comments: Optional[str] = Field(
        default=None, alias="External_Comments"
    )
    generation: Optional[Decimal] = Field(default=None, alias="Generation")
    row_created: Optional[datetime] = Field(default=None, alias="Row_Created")
    row_modified: Optional[datetime] = Field(
        default=None, alias="Row_Modified"
    )
    created_by: Optional[Decimal] = Field(default=None, alias="Created_By")
    modified_by: Optional[Decimal] = Field(default=None, alias="Modified_By")


class Groups(SQLModel, table=True):
    """Groups Table schema auto generated from script"""

    id: Decimal = Field(..., alias="ID", primary_key=True)
    facility_id: Optional[Decimal] = Field(default=None, alias="Facility_ID")
    species_id: Optional[Decimal] = Field(default=None, alias="Species_ID")
    # noinspection SpellCheckingInspection
    acuc_link_id: Optional[Decimal] = Field(default=None, alias="ACUC_Link_ID")
    group_name: Optional[str] = Field(default=None, alias="group_name")
    group_type: Optional[str] = Field(default=None, alias="group_type")
    is_hidden: Optional[str] = Field(default=None, alias="Is_Hidden")
    group_description: Optional[str] = Field(
        default=None, alias="Group_Description"
    )
    group_comments: Optional[str] = Field(default=None, alias="Group_Comments")
    generation: Optional[Decimal] = Field(default=None, alias="Generation")
    row_created: Optional[datetime] = Field(default=None, alias="Row_Created")
    row_modified: Optional[datetime] = Field(
        default=None, alias="Row_Modified"
    )
    created_by: Optional[Decimal] = Field(default=None, alias="Created_By")
    modified_by: Optional[Decimal] = Field(default=None, alias="Modified_By")
    investigator_id: Optional[Decimal] = Field(
        default=None, alias="Investigator_ID"
    )
    group_number: Optional[str] = Field(default=None, alias="Group_Number")
    stock_number: Optional[str] = Field(default=None, alias="Stock_Number")
    project_id: Optional[Decimal] = Field(default=None, alias="Project_ID")
    cost_service_id: Optional[Decimal] = Field(
        default=None, alias="Cost_Service_Id"
    )
    rent_item_id: Optional[Decimal] = Field(default=None, alias="Rent_Item_ID")
    grant_id: Optional[Decimal] = Field(default=None, alias="Grant_Id")
    individual_animal_billing: Optional[str] = Field(
        default=None, alias="Individual_Animal_Billing"
    )
    class_def_id: Optional[Decimal] = Field(default=None, alias="Class_Def_ID")
    class_values: Optional[str] = Field(default=None, alias="Class_Values")
    breeder_limit: Optional[Decimal] = Field(
        default=None, alias="Breeder_Limit"
    )
    breeder_limit_is_age: Optional[str] = Field(
        default=None, alias="Breeder_Limit_Is_Age"
    )
    wean_rent_item_id: Optional[Decimal] = Field(
        default=None, alias="Wean_Rent_Item_ID"
    )
    animal_disposal_rent_item_id: Optional[Decimal] = Field(
        default=None, alias="Animal_Disposal_Rent_Item_ID"
    )
    animal_transfer_rent_item_id: Optional[Decimal] = Field(
        default=None, alias="Animal_Transfer_Rent_Item_ID"
    )
    cage_disposal_rent_item_id: Optional[Decimal] = Field(
        default=None, alias="Cage_Disposal_Rent_Item_ID"
    )
    cage_transfer_rent_item_id: Optional[Decimal] = Field(
        default=None, alias="Cage_Transfer_Rent_Item_ID"
    )
    use_animal_rate_as_disposal: Optional[str] = Field(
        default=None, alias="Use_Animal_Rate_As_Disposal"
    )
    use_animal_rate_as_transfer: Optional[str] = Field(
        default=None, alias="Use_Animal_Rate_As_Transfer"
    )
    use_cage_rate_as_disposal: Optional[str] = Field(
        default=None, alias="Use_Cage_Rate_As_Disposal"
    )
    use_cage_rate_as_transfer: Optional[str] = Field(
        default=None, alias="Use_Cage_Rate_As_Transfer"
    )


class Species(SQLModel, table=True):
    """Species Table schema auto generated from script"""

    id: Decimal = Field(..., alias="ID", primary_key=True)
    is_usda: Optional[str] = Field(default=None, alias="Is_USDA")
    species_name: Optional[str] = Field(default=None, alias="Species_Name")
    generation: Optional[Decimal] = Field(default=None, alias="Generation")
    row_created: Optional[datetime] = Field(default=None, alias="Row_Created")
    row_modified: Optional[datetime] = Field(
        default=None, alias="Row_Modified"
    )
    created_by: Optional[Decimal] = Field(default=None, alias="Created_By")
    modified_by: Optional[Decimal] = Field(default=None, alias="Modified_By")
    animal_class_def_id: Optional[Decimal] = Field(
        default=None, alias="Animal_Class_Def_ID"
    )
    background_animal_class_def_id: Optional[Decimal] = Field(
        default=None, alias="Background_Animal_Class_Def_ID"
    )
    is_hidden: Optional[str] = Field(default=None, alias="Is_Hidden")
    males_per_cage: Optional[Decimal] = Field(
        default=None, alias="Males_Per_Cage"
    )
    females_per_cage: Optional[Decimal] = Field(
        default=None, alias="Females_Per_Cage"
    )
    animal_class_type: Optional[str] = Field(
        default=None, alias="Animal_Class_Type"
    )
    is_imported: Optional[str] = Field(default=None, alias="Is_Imported")
    weight_units: Optional[str] = Field(default=None, alias="Weight_Units")


class MouseCustomClass(
    BaseXmlModel, extra="allow", arbitrary_types_allowed=True
):
    """Schema for MouseCustomClass that will be parsed from XML"""

    reserved_by: Optional[str] = element(
        tag="Reserved_by", default=None, unordered=True
    )
    reserved_date: Optional[str] = element(
        tag="Reserve_Date", default=None, unordered=True
    )
    reason: Optional[str] = element(tag="Reason", default=None, unordered=True)
    solution: Optional[str] = element(
        tag="Solution", default=None, unordered=True
    )
    full_genotype: Optional[str] = element(
        tag="Full_Genotype", default=None, unordered=True
    )
    phenotype: Optional[str] = element(
        tag="Phenotype", default=None, unordered=True
    )


class Subject(SQLModel):
    """Expected Subject view of joined tables"""

    id: Decimal = Field(...)
    class_values: Optional[MouseCustomClass] = Field(default=None)
    sex: Optional[str] = Field(default=None)
    birth_date: Optional[datetime] = Field(default=None)
    species_name: Optional[str] = Field(default=None)
    cage_id: Optional[Decimal] = Field(default=None)
    room_id: Optional[Decimal] = Field(default=None)
    paternal_id: Optional[Decimal] = Field(default=None)
    paternal_class_values: Optional[MouseCustomClass] = Field(default=None)
    maternal_id: Optional[Decimal] = Field(default=None)
    maternal_class_values: Optional[MouseCustomClass] = Field(default=None)
    group_name: Optional[str] = Field(default=None)
    group_description: Optional[str] = Field(default=None)

    # noinspection PyNestedDecorators
    @field_validator(
        "class_values",
        "paternal_class_values",
        "maternal_class_values",
        mode="before",
    )
    @classmethod
    def parse_xml_string(cls, v: Any):
        """Parse xml string Decimalo a model. Only xml strings are expected
        for field construction."""
        if isinstance(v, str):
            try:
                return MouseCustomClass.from_xml(v)
            except ValidationError as e:
                logging.warning(f"Pydantic validation error: {e.json()}")
                return None
            except (ParseError, ParsingError) as e:
                logging.warning(f"XML parsing error: {e.msg}")
                return None
            except Exception as e:
                logging.error(f"Something went wrong parsing {v}: {e.args}")
                return None
        elif isinstance(v, MouseCustomClass):
            return v
        else:
            return None
