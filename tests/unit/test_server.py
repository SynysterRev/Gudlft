def test_should_validate_credentials(client):
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert "Welcome, john@simplylift.co" in response.data.decode()


def test_should_not_validate_credentials(client):
    response = client.post('/showSummary', data={'email': 'john@ift.co'})
    assert response.status_code == 200
    assert "This email is not registered" in response.data.decode()


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_should_purchase_places(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    number_places = int(competitions[0]['numberOfPlaces'])
    response = client.post('/purchasePlaces', data={'club': club['name'],
                                                    'competition': competition['name'],
                                                    'places': 2})
    assert response.status_code == 200
    data = response.data.decode()
    assert 'Great-booking complete!' in data
    assert competition['numberOfPlaces'] == number_places - 2


def test_should_not_purchase_too_many_places(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    response = client.post('/purchasePlaces', data={'club': club['name'],
                                                    'competition': competition[
                                                        'name'], 'places': 15})
    assert response.status_code == 200
    data = response.data.decode()
    assert f"Place must be between 0 and 12" in data


def test_should_not_purchase_more_places_than_left(client, fake_data):
    clubs, competitions = fake_data
    club = clubs[0]
    competition = competitions[0]
    competition['numberOfPlaces'] = 2
    number_places = int(competitions[0]['numberOfPlaces'])
    response = client.post('/purchasePlaces', data={'club': club['name'],
                                                    'competition': competition[
                                                        'name'], 'places': 5})
    assert response.status_code == 200
    data = response.data.decode()
    assert "There is only {} places available".format(number_places) in data


def test_should_not_purchase_place_incorrect_club(client, fake_data):
    _, competitions = fake_data
    club = {'name': 'test', 'email': 'test@test.com', 'points': '5'}
    competition = competitions[0]
    competition['numberOfPlaces'] = 2
    response = client.post('/purchasePlaces', data={'club': club['name'],
                                                    'competition': competition[
                                                        'name'], 'places': 5})
    assert response.status_code == 200
    data = response.data.decode()
    assert "This club is not registered" in data


def test_should_not_purchase_place_incorrect_competition(client, fake_data):
    clubs, _ = fake_data
    club = clubs[0]
    competition = {
        "name": "Test",
        "date": "2020-03-27 10:00:00",
        "numberOfPlaces": "25"
    }
    response = client.post('/purchasePlaces', data={'club': club['name'],
                                                    'competition': competition[
                                                        'name'], 'places': 5})
    assert response.status_code == 200
    data = response.data.decode()
    assert "This competition is not registered" in data
