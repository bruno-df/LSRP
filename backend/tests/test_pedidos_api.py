"""Testes de integração do contrato HTTP da versão organizada com SRP."""

from datetime import datetime, timedelta
from collections.abc import AsyncIterator

import httpx
import pytest

from app.main import criar_app


pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    """Seleciona asyncio como executor dos testes assíncronos."""

    return "asyncio"


@pytest.fixture
async def cliente() -> AsyncIterator[httpx.AsyncClient]:
    """Cria uma aplicação e um cliente HTTP isolados para cada teste."""

    transporte = httpx.ASGITransport(app=criar_app())
    async with httpx.AsyncClient(
        transport=transporte,
        base_url="http://teste",
    ) as cliente_teste:
        yield cliente_teste


async def test_lista_os_seis_itens_do_cardapio(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.get("/api/cardapio")

    assert resposta.status_code == 200
    assert resposta.json() == [
        {"id": 1, "nome": "Hambúrguer", "preco": "20.00"},
        {"id": 2, "nome": "X-Salada", "preco": "23.00"},
        {"id": 3, "nome": "Cachorro-quente", "preco": "15.00"},
        {"id": 4, "nome": "Misto-quente", "preco": "12.00"},
        {"id": 5, "nome": "Batata frita", "preco": "14.00"},
        {"id": 6, "nome": "Porção de nuggets", "preco": "16.00"},
    ]


async def test_lista_de_pedidos_comeca_vazia(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.get("/api/pedidos")

    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_cria_pedido_com_http_201_e_formato_esperado(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": 7,
            "itens": [
                {"item_cardapio_id": 1, "quantidade": 2},
                {"item_cardapio_id": 5, "quantidade": 1},
            ],
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    criado_em = corpo.pop("criado_em")
    assert corpo == {
        "id": 1,
        "numero_mesa": 7,
        "itens": [
            {
                "item_cardapio_id": 1,
                "nome": "Hambúrguer",
                "quantidade": 2,
                "preco_unitario": "20.00",
            },
            {
                "item_cardapio_id": 5,
                "nome": "Batata frita",
                "quantidade": 1,
                "preco_unitario": "14.00",
            },
        ],
        "status": "RECEBIDO",
        "total": "54.00",
    }
    instante = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
    assert instante.utcoffset() == timedelta(0)


async def test_lista_pedidos_em_ordem_crescente_de_id(
    cliente: httpx.AsyncClient,
) -> None:
    for numero_mesa in (10, 20, 30):
        resposta_criacao = await cliente.post(
            "/api/pedidos",
            json={
                "numero_mesa": numero_mesa,
                "itens": [{"item_cardapio_id": 1, "quantidade": 1}],
            },
        )
        assert resposta_criacao.status_code == 201

    resposta = await cliente.get("/api/pedidos")

    assert resposta.status_code == 200
    assert [pedido["id"] for pedido in resposta.json()] == [1, 2, 3]


async def test_consulta_pedido_inexistente_retorna_http_404(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.get("/api/pedidos/999")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Pedido não encontrado."}


@pytest.mark.parametrize(
    "corpo",
    [
        {
            "numero_mesa": 0,
            "itens": [{"item_cardapio_id": 1, "quantidade": 1}],
        },
        {"numero_mesa": 1, "itens": []},
        {
            "numero_mesa": 1,
            "itens": [{"item_cardapio_id": 1, "quantidade": 0}],
        },
        {
            "numero_mesa": 1,
            "itens": [
                {
                    "item_cardapio_id": 1,
                    "quantidade": 1,
                    "nome": "Preço controlado pelo cliente",
                }
            ],
        },
        {
            "numero_mesa": 1,
            "itens": [{"item_cardapio_id": 1, "quantidade": 1}],
            "total": "20.00",
        },
        {
            "numero_mesa": "1",
            "itens": [{"item_cardapio_id": 1, "quantidade": 1}],
        },
    ],
)
async def test_requisicoes_de_criacao_invalidas_retornam_http_422(
    cliente: httpx.AsyncClient,
    corpo: dict[str, object],
) -> None:
    resposta = await cliente.post("/api/pedidos", json=corpo)

    assert resposta.status_code == 422


@pytest.mark.parametrize("item_cardapio_id", [-1, 0, 7, 999])
async def test_item_do_cardapio_inexistente_retorna_http_400(
    cliente: httpx.AsyncClient,
    item_cardapio_id: int,
) -> None:
    resposta = await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": 1,
            "itens": [
                {
                    "item_cardapio_id": item_cardapio_id,
                    "quantidade": 1,
                }
            ],
        },
    )

    assert resposta.status_code == 400
    assert resposta.json() == {
        "detail": "Item do cardápio não encontrado."
    }


async def test_criacao_falha_nao_consome_id(
    cliente: httpx.AsyncClient,
) -> None:
    falha = await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": 1,
            "itens": [{"item_cardapio_id": 999, "quantidade": 1}],
        },
    )
    sucesso = await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": 1,
            "itens": [{"item_cardapio_id": 1, "quantidade": 1}],
        },
    )

    assert falha.status_code == 400
    assert sucesso.status_code == 201
    assert sucesso.json()["id"] == 1


async def test_mudanca_de_status_valida_e_invalida(
    cliente: httpx.AsyncClient,
) -> None:
    criacao = await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": 8,
            "itens": [{"item_cardapio_id": 4, "quantidade": 1}],
        },
    )
    pedido_id = criacao.json()["id"]

    resposta_valida = await cliente.patch(
        f"/api/pedidos/{pedido_id}/status",
        json={"status": "EM_PREPARO"},
    )
    resposta_invalida = await cliente.patch(
        f"/api/pedidos/{pedido_id}/status",
        json={"status": "ENTREGUE"},
    )

    assert resposta_valida.status_code == 200
    assert resposta_valida.json()["status"] == "EM_PREPARO"
    assert resposta_invalida.status_code == 400
    assert resposta_invalida.json() == {
        "detail": "Transição de status não permitida."
    }


async def test_mudanca_de_status_de_pedido_inexistente_retorna_http_404(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.patch(
        "/api/pedidos/999/status",
        json={"status": "EM_PREPARO"},
    )

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Pedido não encontrado."}


@pytest.mark.parametrize(
    "corpo",
    [
        {"status": "DESCONHECIDO"},
        {"status": "EM_PREPARO", "total": "0.00"},
        {},
    ],
)
async def test_atualizacoes_de_status_invalidas_retornam_http_422(
    cliente: httpx.AsyncClient,
    corpo: dict[str, str],
) -> None:
    criacao = await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": 1,
            "itens": [{"item_cardapio_id": 1, "quantidade": 1}],
        },
    )

    resposta = await cliente.patch(
        f"/api/pedidos/{criacao.json()['id']}/status",
        json=corpo,
    )

    assert resposta.status_code == 422


async def test_ordem_e_repeticao_dos_itens_sao_preservadas(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": 2,
            "itens": [
                {"item_cardapio_id": 5, "quantidade": 1},
                {"item_cardapio_id": 1, "quantidade": 2},
                {"item_cardapio_id": 5, "quantidade": 3},
            ],
        },
    )

    assert resposta.status_code == 201
    assert [
        item["item_cardapio_id"] for item in resposta.json()["itens"]
    ] == [5, 1, 5]
    assert resposta.json()["total"] == "96.00"


async def test_openapi_expoe_somente_os_cinco_endpoints_de_negocio(
    cliente: httpx.AsyncClient,
) -> None:
    esquema = (await cliente.get("/openapi.json")).json()
    operacoes = {
        (metodo.upper(), rota)
        for rota, metodos in esquema["paths"].items()
        for metodo in metodos
    }

    assert operacoes == {
        ("GET", "/api/cardapio"),
        ("POST", "/api/pedidos"),
        ("GET", "/api/pedidos"),
        ("GET", "/api/pedidos/{pedido_id}"),
        ("PATCH", "/api/pedidos/{pedido_id}/status"),
    }
