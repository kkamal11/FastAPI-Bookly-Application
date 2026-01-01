from database.auth.schema import UserCreateModel

auth_prefix = "/api/vi/auth"

def test_user_creation(fake_session, fake_user_service, test_client):
    user_data = {
            "email":"kishorkamal7091@gmail.com",
            "username":"Kamal_1",
            "password":"12345678",
            "first_name":"Kamal",
            "last_name":"kishor"
        }
    response = test_client.post(
        url=f"{auth_prefix}/register",
        json=user_data
    )
    user_data = UserCreateModel(**user_data)
    assert fake_user_service.check_user_exists_called_once()
    assert fake_user_service.check_user_exists_called_once("kishorkamal7091@gmail.com", fake_session)
    assert fake_user_service.register_user_called_once()
    assert fake_user_service.register_user_called_once(user_data, fake_session)

