"""Unit tests"""


def test_filter_valid_request(client):
    """Body of request does not pass pydantic validation, should be bad request"""
    body = {
        "gender": "Men",
        "foo": 3213,
        "bar": "JA",
    }
    response = client.post("/filter", json=body)
    assert response.status_code == 200


def test_filter_invalid_request(client):
    """Body of request does not pass pydantic validation because gender is mandatory,
    should be bad request
    """
    body = {
        "foo": 3213,
        "bar": "JA",
    }
    response = client.post("/filter", json=body)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "gender"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
