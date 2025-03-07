from datetime import datetime, timedelta

from flask import url_for

from server import app, find_competition_in_club_booking


def test_should_validate_credentials(client):
    response = client.post("/showSummary", data={"email": "john@simplylift.co"})
    assert response.status_code == 200
    assert "Welcome, john@simplylift.co" in response.data.decode()


def test_should_not_validate_credentials(client):
    response = client.post(
        "/showSummary", data={"email": "john@ift.co"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert "This email is not registered" in response.data.decode()


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_logout_page(client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_should_purchase_places(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    number_places = int(competitions[0]["numberOfPlaces"])

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 2},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert "Great-booking complete!" in data
    assert competition["numberOfPlaces"] == str(number_places - 2)


def test_should_not_purchase_too_many_places(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 15},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert f"Place must be between 0 and 12" in data


def test_should_not_purchase_more_places_than_left(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    competition["numberOfPlaces"] = 2
    number_places = int(competitions[0]["numberOfPlaces"])

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 5},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert "There is only {} places available".format(number_places) in data


def test_should_not_purchase_place_incorrect_club(client, fake_data):
    _, competitions = fake_data
    club = {"name": "test", "email": "test@test.com", "points": "5"}
    competition = competitions[0]
    competition["numberOfPlaces"] = 2

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 5},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert "This club is not registered" in data


def test_should_not_purchase_place_incorrect_competition(client, fake_data):
    clubs, _ = fake_data
    club = clubs[0]
    competition = {
        "name": "Test",
        "date": "2020-03-27 10:00:00",
        "numberOfPlaces": "25",
    }

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 5},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert "This competition is not registered" in data


def test_should_update_points(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    number_points = int(club["points"])

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 2},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert "Great-booking complete!" in data
    assert club["points"] == str(number_points - 2)
    booking = find_competition_in_club_booking(competition['name'], club)
    assert booking is not None
    assert booking[competition['name']] == 2


def test_should_not_update_points_not_enough(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    club["points"] = "1"
    number_points = int(club["points"])

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 2},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert "You have only {} points available".format(number_points) in data


def test_should_be_able_to_book(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    tomorrow = datetime.today() + timedelta(days=1)
    competition = competitions[0]
    competition["date"] = tomorrow.strftime("%Y-%m-%d %H:%M:%S")

    with app.test_request_context():
        url = url_for("book", competition=competition["name"])

    with client.session_transaction() as session:
        session["club"] = club

    response = client.get(url, data={"competition": competition["name"]})

    assert response.status_code == 200
    data = response.data.decode()
    assert "Places available: {}".format(competition["numberOfPlaces"]) in data


def test_should_not_be_able_to_book_athlete(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    tomorrow = datetime.today() + timedelta(days=1)
    competition = competitions[0]
    competition["date"] = tomorrow.strftime("%Y-%m-%d %H:%M:%S")
    club["bookings"].append({competition['name']: 12})

    with client.session_transaction() as session:
        session["club"] = club

    response = client.post(
        "/purchasePlaces",
        data={"competition": competition["name"], "places": 2},
        follow_redirects=True,
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert ("You have already 12 athletes registered for this "
            "competition") in data


def test_should_not_be_able_to_book(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]

    with app.test_request_context():
        url = url_for("book", competition=competition["name"])

    with client.session_transaction() as session:
        session["club"] = club

    response = client.get(
        url, data={"competition": competition["name"]}, follow_redirects=True
    )

    assert response.status_code == 200
    data = response.data.decode()
    assert "Welcome, {}".format(club["email"]) in data


def test_should_display_points(client, fake_data):
    clubs, _ = fake_data
    clubs.append(
        {"name": "Simply Lifty", "email": "john@simplylift.coo", "points": "15"}
    )
    response = client.get("/points", data={"clubs": clubs})
    assert response.status_code == 200
    data = response.data.decode()
    assert "<td>Simply Lift</td>" in data
    assert "<td>20</td>" in data
    assert "<td>Simply Lifty</td>" in data
    assert "<td>15</td>" in data
