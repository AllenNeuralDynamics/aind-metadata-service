"""Tests sharepoint utils package"""

import unittest
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, WrapValidator

from aind_metadata_service.sharepoint.utils import optional_enum


class TestOptionalEnumWrapper(unittest.TestCase):
    """Tests optional enum wrapper function"""

    def test_valid_case(self):
        """Tests case where a valid enum value is input"""

        class MyEnum(str, Enum):
            """Test enum"""

            FIRST = "first"

        class MyModel(BaseModel):
            """Test class"""

            num1: Annotated[MyEnum, WrapValidator(optional_enum)] = Field(
                default=None
            )
            num2: Annotated[MyEnum, WrapValidator(optional_enum)] = Field(
                default=None
            )

        my_model = MyModel(num1="first")
        self.assertEqual(MyEnum.FIRST, my_model.num1)
        self.assertIsNone(my_model.num2)

    def test_invalid_case(self):
        """Tests case where an invalid enum value is input"""

        class MyEnum(str, Enum):
            """Test enum"""

            FIRST = "first"

        class MyModel(BaseModel):
            """Test class"""

            num: Annotated[MyEnum, WrapValidator(optional_enum)] = Field(
                default=None
            )

        my_model = MyModel(num="second?")
        self.assertIsNone(my_model.num)


if __name__ == "__main__":
    unittest.main()
