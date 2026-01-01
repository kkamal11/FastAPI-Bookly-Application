
book_prefix = "/api/vi/books"


def test_get_all_books(fake_session, fake_book_service, test_client):
    books = {
        "title": "A song of Ice and Fire 2",
        "author": "George R. R. Martin k",
        "published_date": "1996-08-06",
        "publisher": "Bantam Books",
        "page_count": 694,
        "language": "English"
    }
    response = test_client.get(
        url=f"{book_prefix}"
    )

    assert fake_book_service.get_all_books_called_once()
    assert fake_book_service.get_all_books_called_once(fake_session)

