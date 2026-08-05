from api.services.users import UserRepository


def test_user_repository_creates_member_once_for_same_openid(tmp_path):
    repository = UserRepository(tmp_path / "users.sqlite3")

    first = repository.get_or_create("member-openid", admin_openids=set())
    second = repository.get_or_create("member-openid", admin_openids=set())

    assert first.role == "member"
    assert second.role == "member"
    assert second.id == first.id


def test_user_repository_assigns_configured_openid_administrator_role(tmp_path):
    repository = UserRepository(tmp_path / "users.sqlite3")

    user = repository.get_or_create("admin-openid", admin_openids={"admin-openid"})

    assert user.role == "admin"
