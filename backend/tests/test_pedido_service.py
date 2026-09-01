from datetime import timedelta
from decimal import Decimal

import pytest

from app.cardapio import Cardapio
from app.models import Pedido, StatusPedido
from app.repository import RepositorioPedidosMemoria
from app.service import ServicoPedidos


_CAMINHOS_PARA_STATUS = {
    StatusPedido.RECEBIDO: (),
    StatusPedido.EM_PREPARO: (StatusPedido.EM_PREPARO,),
    StatusPedido.PRONTO: (StatusPedido.EM_PREPARO, StatusPedido.PRONTO),
    StatusPedido.ENTREGUE: (
        StatusPedido.EM_PREPARO,
        StatusPedido.PRONTO,
        StatusPedido.ENTREGUE,
    ),
    StatusPedido.CANCELADO: (StatusPedido.CANCELADO,),
}
_TRANSICOES_PERMITIDAS = {
    StatusPedido.RECEBIDO: (StatusPedido.EM_PREPARO, StatusPedido.CANCELADO),
    StatusPedido.EM_PREPARO: (StatusPedido.PRONTO, StatusPedido.CANCELADO),
    StatusPedido.PRONTO: (StatusPedido.ENTREGUE,),
    StatusPedido.ENTREGUE: (),
    StatusPedido.CANCELADO: (),
}


@pytest.fixture
def servico() -> ServicoPedidos:
    return ServicoPedidos(
        repositorio=RepositorioPedidosMemoria(),
        cardapio=Cardapio(),
    )


def _criar_pedido_no_status(
    servico: ServicoPedidos,
    status: StatusPedido,
) -> Pedido:
    pedido = servico.criar_pedido(numero_mesa=1, itens=[(1, 1)])
    for proximo_status in _CAMINHOS_PARA_STATUS[status]:
        pedido = servico.atualizar_status(pedido.id, proximo_status)
    return pedido


def test_criacao_define_status_inicial_e_total_correto(
    servico: ServicoPedidos,
) -> None:
    pedido = servico.criar_pedido(
        numero_mesa=7,
        itens=[(1, 2), (5, 1)],
    )

    assert pedido.id == 1
    assert pedido.numero_mesa == 7
    assert pedido.status is StatusPedido.RECEBIDO
    assert pedido.total == Decimal("54.00")
    assert str(pedido.total) == "54.00"
    assert pedido.criado_em.tzinfo is not None
    assert pedido.criado_em.utcoffset() == timedelta(0)


def test_preco_e_nome_sao_obtidos_do_cardapio_pelo_backend(
    servico: ServicoPedidos,
) -> None:
    pedido = servico.criar_pedido(numero_mesa=3, itens=[(2, 1)])

    assert len(pedido.itens) == 1
    assert pedido.itens[0].item_cardapio_id == 2
    assert pedido.itens[0].nome == "X-Salada"
    assert pedido.itens[0].preco_unitario == Decimal("23.00")
    assert str(pedido.itens[0].preco_unitario) == "23.00"


def test_item_do_cardapio_inexistente_e_rejeitado(
    servico: ServicoPedidos,
) -> None:
    with pytest.raises(
        ValueError,
        match=r"^Item do cardápio não encontrado\.$",
    ):
        servico.criar_pedido(numero_mesa=2, itens=[(999, 1)])


def test_consulta_de_pedido_inexistente_falha(
    servico: ServicoPedidos,
) -> None:
    with pytest.raises(LookupError, match=r"^Pedido não encontrado\.$"):
        servico.buscar_pedido(999)


@pytest.mark.parametrize(
    ("status_atual", "novo_status"),
    [
        (status_atual, novo_status)
        for status_atual, novos_status in _TRANSICOES_PERMITIDAS.items()
        for novo_status in novos_status
    ],
)
def test_transicoes_de_status_permitidas(
    servico: ServicoPedidos,
    status_atual: StatusPedido,
    novo_status: StatusPedido,
) -> None:
    pedido = _criar_pedido_no_status(servico, status_atual)

    atualizado = servico.atualizar_status(pedido.id, novo_status)

    assert atualizado.status is novo_status
    assert servico.buscar_pedido(pedido.id).status is novo_status


@pytest.mark.parametrize(
    ("status_atual", "novo_status"),
    [
        (status_atual, novo_status)
        for status_atual, novos_status in _TRANSICOES_PERMITIDAS.items()
        for novo_status in StatusPedido
        if novo_status != status_atual and novo_status not in novos_status
    ],
)
def test_transicoes_de_status_proibidas_nao_alteram_o_pedido(
    servico: ServicoPedidos,
    status_atual: StatusPedido,
    novo_status: StatusPedido,
) -> None:
    pedido = _criar_pedido_no_status(servico, status_atual)

    with pytest.raises(
        ValueError,
        match=r"^Transição de status não permitida\.$",
    ):
        servico.atualizar_status(pedido.id, novo_status)

    assert servico.buscar_pedido(pedido.id) == pedido


@pytest.mark.parametrize("status_atual", list(StatusPedido))
def test_repeticao_do_status_atual_e_idempotente_em_todos_os_estados(
    servico: ServicoPedidos,
    status_atual: StatusPedido,
) -> None:
    pedido = _criar_pedido_no_status(servico, status_atual)
    criado_em = pedido.criado_em

    atualizado = servico.atualizar_status(pedido.id, status_atual)

    assert atualizado == pedido
    assert atualizado.status is status_atual
    assert atualizado.criado_em == criado_em
    assert servico.buscar_pedido(pedido.id) == pedido


def test_total_continua_exato_sem_limite_arbitrario_de_quantidade(
    servico: ServicoPedidos,
) -> None:
    quantidade = 10**100

    pedido = servico.criar_pedido(numero_mesa=1, itens=[(1, quantidade)])

    assert pedido.total == Decimal(quantidade) * Decimal("20.00")
    assert str(pedido.total).endswith(".00")
