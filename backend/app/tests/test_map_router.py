def test_get_dump_data_returns_successful_response(client):
    response = client.post(
        "/api/map/dump-data",
        json={
            "city": "Bochum",
            "country": "Germany",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_item = data[0]
    assert first_item["city"] == "Bochum"
    assert first_item["country"] == "Germany"
    assert "latitude" in first_item
    assert "longitude" in first_item
    assert "label" in first_item
    assert "category" in first_item
    assert "confidence" in first_item
    assert "imgUrl" in first_item
