import json
from datetime import datetime, timedelta

import pytest

from server import (
    find_competition_by_name,
    find_club_by_name,
    find_club_by_email,
    validate_places,
    enough_places,
    enough_points,
    book_places,
    is_past,
    load_clubs,
    load_competitions,
    update_clubs,
    update_competitions,
    too_much_athlete,
    update_booking, find_competition_in_club_booking
)


def test_find_competition_by_name():
    competition = find_competition_by_name("Spring Festival")
    assert competition is not None


def test_find_competition_by_name_wrong():
    competition = find_competition_by_name("Spring Feval")
    assert competition is None


def test_find_club_by_name():
    club = find_club_by_name("Simply Lift")
    assert club is not None


def test_find_club_by_name_wrong():
    club = find_club_by_name("Simply t")
    assert club is None


def test_find_club_by_email():
    club = find_club_by_email("john@simplylift.co")
    assert club is not None


def test_find_club_by_email_wrong():
    club = find_club_by_email("john@simplylift")
    assert club is None


def test_validate_places():
    assert validate_places(0)
    assert validate_places(12)
    assert validate_places(5)


def test_validate_places_wrong():
    assert not validate_places(-2)
    assert not validate_places(15)


def test_enough_places(fake_data):
    _, competitions = fake_data
    competition = competitions[0]
    assert enough_places(competition, 5)
    assert enough_places(competition, 0)


def test_enough_places_wrong(fake_data):
    _, competitions = fake_data
    competition = competitions[0]
    assert not enough_places(competition, 36)


def test_enough_points(fake_data):
    clubs, _ = fake_data
    club = clubs[0]
    assert enough_points(club, 5)
    assert enough_points(club, 0)


def test_enough_points_wrong(fake_data):
    clubs, _ = fake_data
    club = clubs[0]
    assert not enough_points(club, 36)


def test_book_places(fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    book_places(club, competition, 4)
    assert club["points"] == "16"
    assert competition["numberOfPlaces"] == "21"


def test_book_places_wrong(fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    book_places(club, competition, 4)
    assert not club["points"] == "20"
    assert not competition["numberOfPlaces"] == "25"


def test_is_past():
    assert is_past("2020-03-27 10:00:00")


def test_is_past_wrong():
    tomorrow = datetime.today() + timedelta(days=1)
    assert not is_past(tomorrow.strftime("%Y-%m-%d %H:%M:%S"))


def test_loading_clubs(tmp_path):
    club_data = {
        "clubs": [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        ]
    }
    file = tmp_path / "clubs.json"
    file.write_text(json.dumps(club_data))
    assert load_clubs(file) == club_data["clubs"]


def test_loading_clubs_wrong_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_clubs(tmp_path / "wrong.json")


def test_loading_clubs_invalid_json(tmp_path):
    file = tmp_path / "clubs.json"
    file.write_text("{invalid}")
    with pytest.raises(json.JSONDecodeError):
        load_clubs(file)


def test_loading_competitions(tmp_path):
    competition_data = {
        "competitions": [
            {
                "name": "Spring Festival",
                "date": "2020-03-27 10:00:00",
                "numberOfPlaces": "25",
            }
        ]
    }
    file = tmp_path / "competitions.json"
    file.write_text(json.dumps(competition_data))
    assert load_competitions(file) == competition_data["competitions"]


def test_loading_competitions_wrong_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_competitions(tmp_path / "wrong.json")


def test_loading_competitions_invalid_json(tmp_path):
    file = tmp_path / "competitions.json"
    file.write_text("{invalid}")
    with pytest.raises(json.JSONDecodeError):
        load_competitions(file)


def test_update_clubs(tmp_path, mocker):
    club_data = {
        "clubs": [
            {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
        ]
    }
    mocker.patch("server.clubs", club_data["clubs"])
    file = tmp_path / "clubs.json"
    file.write_text(json.dumps(club_data))
    club_data["clubs"][0]["points"] = "16"
    update_clubs(file)
    assert load_clubs(file) == club_data["clubs"]


def test_update_competitions(tmp_path, mocker):
    competition_data = {
        "competitions": [
            {
                "name": "Spring Festival",
                "date": "2020-03-27 10:00:00",
                "numberOfPlaces": "25",
            }
        ]
    }
    mocker.patch("server.competitions", competition_data["competitions"])
    file = tmp_path / "competitions.json"
    file.write_text(json.dumps(competition_data))
    competition_data["competitions"][0]["numberOfPlaces"] = "16"
    update_competitions(file)
    assert load_competitions(file) == competition_data["competitions"]


def test_too_much_athlete(fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    assert too_much_athlete(club, competition, 5) == False


def test_too_much_athlete_wrong(fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    club["bookings"].append({competition['name'] : 12})
    assert too_much_athlete(club, competition, 5) == True


def test_update_booking(fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    update_booking(club, competition['name'], 5)
    booking = find_competition_in_club_booking(competition['name'], club)
    assert booking[competition['name']] == 5


def test_update_booking_already_exists(fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    club["bookings"].append({competition['name']: 5})
    update_booking(club, competition['name'], 5)
    booking = find_competition_in_club_booking(competition['name'], club)
    assert booking[competition['name']] == 10
