"""Set up fixtures to be used across all test modules."""

import json
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from requests import Response
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine

from aind_metadata_service.backends.labtracks.models import (
    AnimalsCommon,
    Groups,
    MouseCustomClass,
    Species,
    Subject,
)
from aind_metadata_service.backends.labtracks.session import (
    get_session as get_lb_session,
)
from aind_metadata_service.server import app

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


@pytest.fixture(scope="module")
def test_lab_tracks_subject():
    """A common lab_tracks subject pulled from their db"""
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
        group_description="BALB/c",
    )


@pytest.fixture(scope="module")
def example_200_subject_response():
    """Expected response when a user requests a subject."""
    with open(RESOURCES_DIR / "subject_responses" / "response_200.json") as f:
        contents = json.load(f)
    return contents


@pytest.fixture()
def mock_get_raw_funding_sheet(mocker):
    """Expected raw funding sheet."""
    with open(RESOURCES_DIR / "backends" / "smartsheet" / "funding.json") as f:
        contents = json.load(f)
    mock_get = mocker.patch(
        "aind_smartsheet_api.client.SmartsheetClient.get_raw_sheet"
    )
    mock_get.return_value = json.dumps(contents)
    return mock_get


@pytest.fixture()
def mock_get_raw_perfusions_sheet(mocker):
    """Expected raw perfusions sheet."""
    with open(
        RESOURCES_DIR / "backends" / "smartsheet" / "perfusions.json"
    ) as f:
        contents = json.load(f)
    mock_get = mocker.patch(
        "aind_smartsheet_api.client.SmartsheetClient.get_raw_sheet"
    )
    mock_get.return_value = json.dumps(contents)
    return mock_get


@pytest.fixture()
def mock_get_raw_protocols_sheet(mocker):
    """Expected raw protocols sheet."""
    with open(
        RESOURCES_DIR / "backends" / "smartsheet" / "protocols.json"
    ) as f:
        contents = json.load(f)
    mock_get = mocker.patch(
        "aind_smartsheet_api.client.SmartsheetClient.get_raw_sheet"
    )
    mock_get.return_value = json.dumps(contents)
    return mock_get


@pytest.fixture()
def mock_get_access_token(mocker):
    """Mock getting a bearer token."""
    mock_get = mocker.patch(
        "aind_metadata_service.backends.tars.configs.Settings.get_bearer_token"
    )
    mock_get.return_value = ("abc123def456", 1733101170)
    return mock_get


@pytest.fixture()
def mock_get_raw_prep_lot_response(mocker):
    """Mock raw prep_lot response"""
    with open(
        RESOURCES_DIR / "backends" / "tars" / "raw_prep_lot_response.json"
    ) as f:
        contents = json.load(f)
    mock_get = mocker.patch(
        "aind_metadata_service.backends.tars.handler.SessionHandler"
        "._get_raw_prep_lot_response"
    )
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps(contents).encode("utf-8")
    mock_get.return_value = mock_response


@pytest.fixture()
def mock_get_raw_molecule_response(mocker):
    """Mock raw molecule response"""
    with open(
        RESOURCES_DIR / "backends" / "tars" / "raw_molecules_response.json"
    ) as f:
        contents = json.load(f)
    mock_get = mocker.patch(
        "aind_metadata_service.backends.tars.handler.SessionHandler"
        "._get_raw_molecules_response"
    )
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = json.dumps(contents).encode("utf-8")
    mock_get.return_value = mock_response


@pytest.fixture(scope="session")
def get_lab_tracks_session():
    """Generate a sqlite database to query lab_tracks data."""
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
    with open(RESOURCES_DIR / "test_db.json", "r") as f:
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


@pytest.fixture(scope="session")
def client(get_lab_tracks_session):
    """Override a dependency required by the FastAPI app."""

    def override_get_lb_session():
        """Override standard session with the one for tests."""
        yield get_lab_tracks_session

    app.dependency_overrides[get_lb_session] = override_get_lb_session
    FastAPICache.init(InMemoryBackend())
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
