import pytest
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine

from aind_metadata_service.backends.labtracks.models import (
    AnimalsCommon,
    Groups,
    MouseCustomClass,
    Species,
    Subject,
)
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import json
import os

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
TEST_DB_FILE = TEST_DIR / "resources" / "test_db.json"


@pytest.fixture(scope="module")
def test_subject():
    return Subject(
        id=Decimal("632269.0000000000"),
        class_values=MouseCustomClass(
            reserved_by="Anna Apple",
            reserved_date="2022-07-14T00:00:00-07:00",
            reason=None,
            solution="1xPBS",
            full_genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
            phenotype=(
                "P19: TSTW. Small body, large head, slightly dehydrated. "
                "3.78g. P22: 5.59g. P26: 8.18g. Normal body proportions. "
            ),
        ),
        sex="F",
        birth_date=datetime(2022, 5, 1, 0, 0),
        species_name="mouse",
        cage_id=Decimal("-99999999999999.0000000000"),
        room_id=Decimal("-99999999999999.0000000000"),
        paternal_id=Decimal("623236.0000000000"),
        paternal_class_values=MouseCustomClass(
            reserved_by="Person One ",
            reserved_date="2022-11-01T00:00:00",
            reason="eu-retire",
            solution=None,
            full_genotype="RCL-somBiPoles_mCerulean-WPRE/wt",
            phenotype="P87: F.G. P133: Barberer. ",
        ),
        maternal_id=Decimal("615310.0000000000"),
        maternal_class_values=MouseCustomClass(
            reserved_by="Person One ",
            reserved_date="2022-08-03T00:00:00",
            reason="Eu-retire",
            solution=None,
            full_genotype="Pvalb-IRES-Cre/wt",
            phenotype="P100: F.G.",
        ),
        group_name="Exp-ND-01-001-2109",
        group_description="test description 2",
    )


@pytest.fixture(scope="module")
def get_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=True,
    )
    SQLModel.metadata.create_all(engine)
    session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = session_local()
    # Load sqlite db with test data
    with open(TEST_DB_FILE, "r") as f:
        test_db = json.load(f)
    for ac_row in test_db["animals_common"]:
        ac = AnimalsCommon.model_validate(ac_row)
        session.add(ac)
    for g_row in test_db["groups"]:
        g = Groups.model_validate(g_row)
        session.add(g)
    for s_row in test_db["species"]:
        s = Species.model_validate(s_row)
        session.add(s)
    session.commit()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
