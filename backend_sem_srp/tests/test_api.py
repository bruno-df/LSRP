from collections.abc import AsyncIterator
from datetime import datetime, timedelta

import httpx
import pytest

import main


pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def reiniciar_estado() -> None:
    with main._estado_lock:
        main._pedidos.clear()
        main._proximo_id = 1


@pytest.fixture
async def cliente() -> AsyncIterator[httpx.AsyncClient]:
    transporte = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(
        transport=transporte,
        base_url="http://teste",
    ) as cliente_teste:
        yield cliente_teste


async def criar_pedido(
    cliente: httpx.AsyncClient,
    *,
    numero_mesa: int = 1,
    item_cardapio_id: int = 1,
    quantidade: int = 1,
) -> httpx.Response:
    return await cliente.post(
        "/api/pedidos",
        json={
            "numero_mesa": numero_mesa,
            "itens": [
                {
                    "item_cardapio_id": item_cardapio_id,
                    "quantidade": quantidade,
                }
            ],
        },
    )


async def test_cardapio_tem_os_seis_itens_e_precos(
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


async def test_listagem_comeca_vazia(cliente: httpx.AsyncClient) -> None:
    resposta = await cliente.get("/api/pedidos")

    assert resposta.status_code == 200
    assert resposta.json() == []


async def test_criacao_retorna_201_total_e_status_inicial(
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


async def test_itens_repetidos_permanecem_na_ordem_recebida(
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


@pytest.mark.parametrize("item_cardapio_id", [-1, 0, 7, 999])
async def test_item_inexistente_retorna_400(
    cliente: httpx.AsyncClient,
    item_cardapio_id: int,
) -> None:
    resposta = await criar_pedido(
        cliente,
        item_cardapio_id=item_cardapio_id,
    )

    assert resposta.status_code == 400
    assert resposta.json() == {
        "detail": "Item do cardápio não encontrado."
    }


async def test_pedido_invalido_nao_e_salvo_nem_consome_id(
    cliente: httpx.AsyncClient,
) -> None:
    falha = await criar_pedido(cliente, item_cardapio_id=999)
    lista_apos_falha = await cliente.get("/api/pedidos")
    sucesso = await criar_pedido(cliente)

    assert falha.status_code == 400
    assert lista_apos_falha.json() == []
    assert sucesso.status_code == 201
    assert sucesso.json()["id"] == 1


@pytest.mark.parametrize(
    "corpo",
    [
        {
            "numero_mesa": 0,
            "itens": [{"item_cardapio_id": 1, "quantidade": 1}],
        },
        {
            "numero_mesa": -1,
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
                {"item_cardapio_id": 1, "quantidade": 1, "nome": "Outro"}
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
        {
            "numero_mesa": 1,
            "itens": [{"item_cardapio_id": "1", "quantidade": 1}],
        },
        {
            "numero_mesa": 1,
            "itens": [{"item_cardapio_id": 1, "quantidade": "1"}],
        },
    ],
)
async def test_formato_campo_ou_tipo_invalido_retorna_422(
    cliente: httpx.AsyncClient,
    corpo: dict[str, object],
) -> None:
    resposta = await cliente.post("/api/pedidos", json=corpo)

    assert resposta.status_code == 422


async def test_listagem_mantem_ordem_crescente_de_id(
    cliente: httpx.AsyncClient,
) -> None:
    for numero_mesa in (10, 20, 30):
        resposta = await criar_pedido(cliente, numero_mesa=numero_mesa)
        assert resposta.status_code == 201

    resposta = await cliente.get("/api/pedidos")

    assert resposta.status_code == 200
    assert [pedido["id"] for pedido in resposta.json()] == [1, 2, 3]


async def test_consulta_pedido_existente(cliente: httpx.AsyncClient) -> None:
    criacao = await criar_pedido(cliente, numero_mesa=8)

    resposta = await cliente.get(f"/api/pedidos/{criacao.json()['id']}")

    assert resposta.status_code == 200
    assert resposta.json() == criacao.json()


async def test_consulta_pedido_inexistente_retorna_404(
    cliente: httpx.AsyncClient,
) -> None:
    resposta = await cliente.get("/api/pedidos/999")

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Pedido não encontrado."}


@pytest.mark.parametrize(
    ("caminho", "proximo_status"),
    [
        ([], "EM_PREPARO"),
        ([], "CANCELADO"),
        (["EM_PREPARO"], "PRONTO"),
        (["EM_PREPARO"], "CANCELADO"),
        (["EM_PREPARO", "PRONTO"], "ENTREGUE"),
    ],
)
async def test_transicoes_permitidas(
    cliente: httpx.AsyncClient,
    caminho: list[str],
    proximo_status: str,
) -> None:
    criacao = await criar_pedido(cliente)
    pedido_id = criacao.json()["id"]
    for status_intermediario in caminho:
        intermediaria = await cliente.patch(
            f"/api/pedidos/{pedido_id}/status",
            json={"status": status_intermediario},
        )
        assert intermediaria.status_code == 200

    resposta = await cliente.patch(
        f"/api/pedidos/{pedido_id}/status",
        json={"status": proximo_status},
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == proximo_status


@pytest.mark.parametrize(
    ("caminho", "status_proibido"),
    [
        ([], "PRONTO"),
        ([], "ENTREGUE"),
        (["EM_PREPARO"], "RECEBIDO"),
        (["EM_PREPARO", "PRONTO"], "CANCELADO"),
        (["EM_PREPARO", "PRONTO", "ENTREGUE"], "PRONTO"),
        (["CANCELADO"], "RECEBIDO"),
    ],
)
async def test_transicoes_proibidas_retorna_400_e_nao_altera_pedido(
    cliente: httpx.AsyncClient,
    caminho: list[str],
    status_proibido: str,
) -> None:
    criacao = await criar_pedido(cliente)
    pedido_id = criacao.json()["id"]
    for status_intermediario in caminho:
        await cliente.patch(
            f"/api/pedidos/{pedido_id}/status",
            json={"status": status_intermediario},
        )
    antes = (await cliente.get(f"/api/pedidos/{pedido_id}")).json()

    resposta = await cliente.patch(
        f"/api/pedidos/{pedido_id}/status",
        json={"status": status_proibido},
    )
    depois = (await cliente.get(f"/api/pedidos/{pedido_id}")).json()

    assert resposta.status_code == 400
    assert resposta.json() == {
        "detail": "Transição de status não permitida."
    }
    assert depois == antes


@pytest.mark.parametrize(
    "caminho",
    [
        [],
        ["EM_PREPARO"],
        ["EM_PREPARO", "PRONTO"],
        ["EM_PREPARO", "PRONTO", "ENTREGUE"],
        ["CANCELADO"],
    ],
)
async def test_repetir_status_atual_e_idempotente(
    cliente: httpx.AsyncClient,
    caminho: list[str],
) -> None:
    pedido = (await criar_pedido(cliente)).json()
    for proximo_status in caminho:
        pedido = (
            await cliente.patch(
                f"/api/pedidos/{pedido['id']}/status",
                json={"status": proximo_status},
            )
        ).json()

    repeticao = await cliente.patch(
        f"/api/pedidos/{pedido['id']}/status",
        json={"status": pedido["status"]},
    )

    assert repeticao.status_code == 200
    assert repeticao.json() == pedido


async def test_atualizacao_de_pedido_inexistente_retorna_404(
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
async def test_atualizacao_de_status_invalida_retorna_422(
    cliente: httpx.AsyncClient,
    corpo: dict[str, str],
) -> None:
    pedido = (await criar_pedido(cliente)).json()

    resposta = await cliente.patch(
        f"/api/pedidos/{pedido['id']}/status",
        json=corpo,
    )

    assert resposta.status_code == 422


async def test_valores_monetarios_sao_strings_com_duas_casas(
    cliente: httpx.AsyncClient,
) -> None:
    cardapio = (await cliente.get("/api/cardapio")).json()
    pedido = (await criar_pedido(cliente, item_cardapio_id=2, quantidade=3)).json()

    assert all(
        isinstance(item["preco"], str) and item["preco"].endswith(".00")
        for item in cardapio
    )
    assert pedido["itens"][0]["preco_unitario"] == "23.00"
    assert pedido["total"] == "69.00"


async def test_total_grande_permanece_exato(cliente: httpx.AsyncClient) -> None:
    quantidade = 10**100

    resposta = await criar_pedido(cliente, quantidade=quantidade)

    assert resposta.status_code == 201
    assert resposta.json()["total"] == f"{20 * quantidade}.00"


async def test_openapi_expoe_somente_as_cinco_operacoes(
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
