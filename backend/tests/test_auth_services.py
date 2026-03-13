from app.auth.services import create_user, login


def test_login_retorna_tokens_para_usuario_ativo(db_session):
    create_user(db_session, "Teste", "login@test.local", "senha12345", "ADMIN")

    result = login(db_session, "login@test.local", "senha12345")

    assert result["access_token"]
    assert result["expires_in"] > 0
    assert result["perfil"] == "ADMIN"


def test_login_falha_com_senha_incorreta(db_session):
    create_user(db_session, "Teste", "falha@test.local", "senha12345", "ADMIN")

    result = login(db_session, "falha@test.local", "senha-errada")

    assert result == {}
