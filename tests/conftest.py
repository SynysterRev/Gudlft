import pytest

from server import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def fake_data(mocker):
    clubs = [{"name": "Simply Lift", "email": "john@simplylift.co", "points": "20",
              "bookings" : []}]
    competitions = [
        {
            "name": "Spring Festival",
            "date": "2024-10-22 13:00:00",
            "numberOfPlaces": "25",
        }
    ]
    mocker.patch("server.clubs", clubs)
    mocker.patch("server.competitions", competitions)
    mocker.patch("server.update_clubs", return_value=None)
    mocker.patch("server.update_competitions", return_value=None)
    return clubs, competitions
