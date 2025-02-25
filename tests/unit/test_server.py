from datetime import datetime, timedelta

from server import (find_competition_by_name, find_club_by_name, find_club_by_email,
                    validate_places, enough_places, enough_points, book_places, is_past)


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
    assert club['points'] == '16'
    assert competition['numberOfPlaces'] == '21'


def test_book_places_wrong(fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    book_places(club, competition, 4)
    assert not club['points'] == '20'
    assert not competition['numberOfPlaces'] == '25'


def test_is_past():
    assert is_past('2020-03-27 10:00:00')


def test_is_past_wrong():
    tomorrow = datetime.today() + timedelta(days=1)
    assert not is_past(tomorrow.strftime("%Y-%m-%d %H:%M:%S"))
