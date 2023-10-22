"""Module to contain SLIMS db models"""

from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from pydantic.typing import Literal
from slims.internal import Record


class ContentsTableColumnInfo(BaseModel):
    """A record pulled from slims has info attached to the columns."""

    datatype: Literal[
        "BOOLEAN",
        "DATE",
        "ENUM",
        "FLOAT",
        "FOREIGN_KEY",
        "INTEGER",
        "QUANTITY",
        "STRING",
    ]
    dateFormat: Optional[str]
    displayField: Optional[str]
    displayValue: Optional[str]
    editable: bool
    foreignDisplayColumn: Optional[str]
    foreignTable: Optional[str]
    hidden: bool
    name: str
    position: int
    subType: Optional[str]
    timeZone: Optional[str]
    title: str
    unit: Optional[str]
    value: Union[int, bool, str, None]

    def _map_bool_to_field_str(self):
        """Map BOOLEAN to a string representing the pydantic field"""
        field_str = (
            f'{self.name}: Optional[bool] = Field(None, title="{self.title}")'
        )
        return field_str

    def _map_date_to_field_str(self):
        """Map DATE to a string representing the pydantic field"""
        if self.subType is None or self.subType == "datetime":
            field_type = "Optional[datetime]"
        else:
            field_type = "Optional[date]"
        if self.timeZone is None:
            field_str = (
                f"{self.name}: {field_type} = Field(None, "
                f'title="{self.title}")'
            )
        else:
            field_str = (
                f"{self.name}: Optional[{field_type}] = Field(None, "
                f'title="{self.title}", '
                f'description="timeZone: {self.timeZone}")'
            )
        return field_str

    def _map_enum_to_field_str(self):
        """Maps an enum to a field. There doesn't seem to be a way to retrieve
        the enum values, so we're just mapping to a string for now."""
        field_str = (
            f'{self.name}: Optional[str] = Field(None, title="{self.title}")'
        )
        return field_str

    def _map_float_to_field_str(self):
        """Map FLOAT to a string representing the pydantic field"""
        field_str = (
            f'{self.name}: Optional[float] = Field(None, title="{self.title}")'
        )
        return field_str

    def _map_foreign_key_to_field_str(self):
        """Map FOREIGN_KEY to a string representing the pydantic field"""
        field_str = (
            f'{self.name}: Optional[str] = Field(None, title="{self.title}")'
        )
        return field_str

    def _map_int_to_field_str(self):
        """Map INTEGER to a string representing the pydantic field"""
        field_str = (
            f'{self.name}: Optional[int] = Field(None, title="{self.title}")'
        )
        return field_str

    def _map_quantity_to_field_str(self):
        """Map QUANTITY to a string representing the pydantic field"""
        if self.unit is not None:
            field_str = (
                f"{self.name}: Optional[float] = Field(None, "
                f'title={self.title}, description="Unit: {self.unit}")'
            )
        else:
            field_str = (
                f"{self.name}: Optional[float] = Field(None, "
                f'title="{self.title}")'
            )
        return field_str

    def _map_str_to_field_str(self):
        """Map STRING to a string representing the pydantic field"""
        field_str = (
            f'{self.name}: Optional[str] = Field(None, title="{self.title}")'
        )
        return field_str

    def map_to_field_str(self):
        """Map field to a string representing the pydantic field"""
        if self.datatype == "BOOLEAN":
            return self._map_bool_to_field_str()
        elif self.datatype == "DATE":
            return self._map_date_to_field_str()
        elif self.datatype == "ENUM":
            return self._map_enum_to_field_str()
        elif self.datatype == "FLOAT":
            return self._map_float_to_field_str()
        elif self.datatype == "FOREIGN_KEY":
            return self._map_foreign_key_to_field_str()
        elif self.datatype == "INTEGER":
            return self._map_int_to_field_str()
        elif self.datatype == "QUANTITY":
            return self._map_quantity_to_field_str()
        else:
            return self._map_str_to_field_str()


class ContentsTableRow(BaseModel):
    """A record pulled from slims Contents Table."""

    cntn_fk_originalContent: Optional[str] = Field(
        None, title="Original Content"
    )
    icon: Optional[str] = Field(None, title="Icon")
    containerIcon: Optional[str] = Field(None, title="Container icon")
    cntn_fk_category: Optional[str] = Field(None, title="Category")
    cntn_fk_contentType: Optional[str] = Field(None, title="Type")
    cntn_barCode: Optional[str] = Field(None, title="Barcode")
    cntn_fk_containerContentType: Optional[str] = Field(
        None, title="Container type"
    )
    cntn_cf_mass: Optional[float] = Field(
        None, title="Mass", description="Unit: &mu;g"
    )
    cntn_id: Optional[str] = Field(None, title="ID")
    cntn_cf_contactPerson: Optional[str] = Field(None, title="Contact Person")
    cntn_dilutionFactor: Optional[float] = Field(None, title="Dilution Factor")
    cntn_status: Optional[str] = Field(None, title="Status")
    cntn_fk_status: Optional[str] = Field(None, title="Status")
    cntn_fk_user: Optional[str] = Field(None, title="User")
    cntn_cf_lotNumber: Optional[str] = Field(None, title="Lot number")
    cntn_fk_group: Optional[str] = Field(None, title="Group")
    cntn_fk_source: Optional[str] = Field(None, title="Source")
    cntn_position_row: Optional[str] = Field(None, title="Located at row")
    cntn_fk_location: Optional[str] = Field(None, title="Location")
    cntn_fk_location_recursive: Optional[str] = Field(
        None, title="Location (including sublocations)"
    )
    locationPath: Optional[str] = Field(None, title="Location path")
    cntn_position_column: Optional[str] = Field(
        None, title="Located at column"
    )
    cntn_cf_dateOfBirth: Optional[date] = Field(
        None,
        title="Date of birth",
        description="timeZone: America/Los_Angeles",
    )
    cntn_cf_dateRangeStart: Optional[datetime] = Field(
        None,
        title="Date range start",
        description="timeZone: America/Los_Angeles",
    )
    cntn_cf_fk_fundingCode: Optional[str] = Field(None, title="Funding Code")
    cntn_cf_genotype: Optional[str] = Field(None, title="Genotype")
    cntn_cf_iacucProtocol: Optional[str] = Field(None, title="IACUC Protocol")
    cntn_cf_institution: Optional[str] = Field(None, title="Institution")
    cntn_cf_labtracksGroup: Optional[str] = Field(
        None, title="LabTracks Group"
    )
    cntn_cf_labtracksId: Optional[str] = Field(None, title="Labtracks ID")
    cntn_cf_lightcycle: Optional[str] = Field(None, title="LightCycle")
    cntn_cf_mouseAge: Optional[int] = Field(None, title="Mouse age (mo)")
    cntn_cf_name: Optional[str] = Field(None, title="Name")
    cntn_cf_parentBarcode: Optional[str] = Field(None, title="Parent barcode")
    cntn_cf_pedigreeName: Optional[str] = Field(None, title="Pedigree Name")
    cntn_cf_sex: Optional[str] = Field(None, title="Sex")
    cntn_cf_slideBarcode: Optional[str] = Field(None, title="Slide barcode")
    cntn_cf_strain: Optional[str] = Field(None, title="Strain")
    cntn_fk_product_strain: Optional[str] = Field(
        None, title="Product (filtering without version)"
    )
    relationToProband: Optional[str] = Field(None, title="Relation to proband")
    father: Optional[str] = Field(None, title="Father")
    mother: Optional[str] = Field(None, title="Mother")
    derivedCount: Optional[int] = Field(None, title="Derivation count")
    ingredientCount: Optional[int] = Field(None, title="Ingredient count")
    mixCount: Optional[int] = Field(None, title="Mix count")
    cntn_createdBy: Optional[str] = Field(None, title="Created by")
    cntn_createdOn: Optional[datetime] = Field(
        None, title="Created on", description="timeZone: America/Los_Angeles"
    )
    cntn_modifiedBy: Optional[str] = Field(None, title="Modified by")
    cntn_modifiedOn: Optional[datetime] = Field(
        None, title="Modified on", description="timeZone: America/Los_Angeles"
    )
    flags: Optional[str] = Field(None, title="Flags")
    previousFlags: Optional[str] = Field(None, title="Previous flags")
    cntn_externalId: Optional[str] = Field(None, title="External Id")
    lctn_barCode: Optional[str] = Field(None, title="Barcode")
    diss_name: Optional[str] = Field(None, title="Name")
    cntp_name: Optional[str] = Field(None, title="Name")
    stts_name: Optional[str] = Field(None, title="Name")
    father_display: Optional[str] = Field(None, title="father_display")
    lctp_positionLess: Optional[bool] = Field(
        None, title="Don't require positions"
    )
    cntp_slimsGeneratesBarcode: Optional[bool] = Field(
        None, title="SLIMS generates a barcode for content of this type"
    )
    xprs_input: Optional[int] = Field(None, title="xprs_input")
    grps_groupName: Optional[str] = Field(None, title="Name")
    lctn_columns: Optional[str] = Field(None, title="Columns")
    isNaFilter: Optional[str] = Field(None, title="Field is N/A")
    xprs_output: Optional[int] = Field(None, title="xprs_output")
    cntn_pk: Optional[int] = Field(None, title="cntn_pk")
    cntp_useBarcodeAsId: Optional[bool] = Field(
        None, title="Use barcode as id"
    )
    lctn_rows: Optional[str] = Field(None, title="Rows")
    prvd_name: Optional[str] = Field(None, title="Name")
    cntp_canEnrollInStudy: Optional[bool] = Field(
        None, title="Can enroll in a study"
    )
    cntp_containerType: Optional[bool] = Field(
        None, title="Is a container type"
    )
    isNotNaFilter: Optional[str] = Field(None, title="Field is not N/A")
    lctn_name: Optional[str] = Field(None, title="Name")
    mother_display: Optional[str] = Field(None, title="mother_display")
    attachmentCount: Optional[int] = Field(None, title="attachmentCount")
    sorc_name: Optional[str] = Field(None, title="Name")
    user_userName: Optional[str] = Field(None, title="User name")
    cntn_originalContentBarCode: Optional[str] = Field(
        None, title="Original content barcode"
    )

    @staticmethod
    def map_record_to_model_string(record: Record) -> List[str]:
        """
        Utility method to parse the information from a slims record into
        pydantic fields.
        Parameters
        ----------
        record : Record
          A record pulled from the slims db. Easiest way to pull a record is
          using:
          record = slims.fetch(
                   "Content", is_not_null("cntn_id"), start=0, end=1
          )[0]

        Returns
        -------
        List[str]
          A list of string representations of pydantic fields

        """
        columns_info = [
            ContentsTableColumnInfo.parse_obj(c)
            for c in record.json_entity["columns"]
        ]
        return [c.map_to_field_str() for c in columns_info]

    @classmethod
    def from_record(cls, record: Record):
        """Create a ContentsTableRow from a SLIMS Record"""
        field_names = cls.__fields__
        field_values = {}
        for field_name in field_names:
            record_value = getattr(record, field_name, None)
            if record_value is not None:
                record_value = record_value.value
            field_values[field_name] = record_value
        return cls(**field_values)
