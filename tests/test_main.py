# The `client` fixture comes from conftest.py — pytest finds it automatically
# just by name, no import needed. It gives you a TestClient wired up to a
# fresh in-memory database for this test only.


# --- Worked example ---
def test_add_book(client):
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "status": "to_read"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"
    assert data["id"] is not None  # SQLite should have assigned one


# --- TODO: your turn ---
def test_get_book_not_found(client):
    # A GET for a book id that doesn't exist should 404.
    response = client.get(
        "/books/12345"
    )
    assert response.status_code == 404


# --- TODO: your turn ---
def test_get_book_found(client):
    # POST a book first (like the worked example above), then GET it by
    # the id that came back, and check the fields match what you sent.
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "status": "to_read"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"

    get_response = client.get(f"/books/{data['id']}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["title"] == "Dune"
    assert data["id"] == 1


# --- TODO: your turn ---
def test_delete_book(client):
    # POST a book, DELETE it, then GET it again and confirm it's a 404.
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "status": "to_read"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"

    delete = client.delete(
        f"/books/{data['id']}"
    )
    assert delete.status_code == 200

    get_response = client.get(f"/books/{data['id']}")
    assert get_response.status_code == 404


# --- TODO: your turn ---
def test_replace_book(client):
    # POST a book, PUT a full replacement over it, check the fields changed.
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "status": "to_read"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"

    replace = client.put(f"/books/{data['id']}", json={
        "title": "Dune Two", "author": "Frank Herbert", "status": "reading"
    })
    assert replace.status_code == 200

    get_response = client.get((f"/books/{data['id']}"))
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["title"] == "Dune Two"


# --- TODO: your turn ---
def test_update_book_partial(client):
    # POST a book, PATCH just one field (e.g. rating), then confirm the
    # other fields are unchanged and only the patched field updated.
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "status": "to_read"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"

    patch_response = client.patch(
        f"/books/{data['id']}",
        json={"rating": 3},
    )
    assert patch_response.status_code == 200

    get_response = client.get((f"/books/{data['id']}"))
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["rating"] == patch_response.json()["rating"]
    assert data["title"] == "Dune"



# --- TODO: your turn ---
def test_list_books_filters_by_status(client):
    # POST a couple of books with different statuses, GET /books?status=...,
    # and check only the matching ones come back.
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "status": "to_read"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"

    response = client.post(
        "/books",
        json={"title": "Til Death do we Parent", "author": "Jess Hilarious", "status": "reading"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Til Death do we Parent"

    get_response = client.get(
        "/books?status=to_read"
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data[0]["title"] == "Dune"
    assert len(data) == 1


# --- TODO: your turn ---
def test_list_books_pagination(client):
    # POST several books, then check that limit/offset slice the results
    # the way you'd expect.
    response = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "status": "to_read"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Dune"

    response = client.post(
        "/books",
        json={"title": "Til Death do we Parent", "author": "Jess Hilarious", "status": "reading"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Til Death do we Parent"

    response = client.post(
        "/books",
        json={"title": "This is America", "author": "Childish Gambino", "status": "finished"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "This is America"

    response = client.post(
        "/books",
        json={"title": "FIFA: A Corrupt entity", "author": "Childish Gambino", "status": "finished"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "FIFA: A Corrupt entity"

    get_response = client.get(
        "/books?limit=2&offset=1"
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Til Death do we Parent"
    assert data[1]["title"] == "This is America"
