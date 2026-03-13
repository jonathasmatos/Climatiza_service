from app.core.states import (
    OrdemStatus,
    can_transition_ordem_status,
    ensure_valid_ordem_status,
    normalize_ordem_status,
)


def test_normaliza_status_legado():
    assert normalize_ordem_status("aberta") == OrdemStatus.NOVO.value
    assert normalize_ordem_status("concluida") == OrdemStatus.RESOLVIDO.value


def test_valida_status_invalido():
    try:
        ensure_valid_ordem_status("qualquer")
    except ValueError as exc:
        assert "Status inválido" in str(exc)
    else:
        raise AssertionError("Era esperado ValueError para status inválido")


def test_transicoes_validas_e_invalidas():
    assert can_transition_ordem_status(OrdemStatus.NOVO.value, OrdemStatus.AGENDADO.value)
    assert not can_transition_ordem_status(OrdemStatus.NOVO.value, OrdemStatus.FECHADO.value)
