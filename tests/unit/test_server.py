def test_should_validate_credentials(client):
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200

def test_should_not_validate_credentials(client):
    response = client.post('/showSummary', data={'email': 'john@ift.co'})
    assert response.status_code == 200
    assert "This email is not registered" in response.data.decode()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200