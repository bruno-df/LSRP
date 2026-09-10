"""Contraexemplo acadêmico deliberado de backend sem SRP.

Este arquivo concentra responsabilidades diferentes para fins didáticos e não
deve ser usado como referência arquitetural.
"""

from datetime import datetime, timezone
from decimal import Decimal, localcontext
from enum import Enum
from threading import Lock
from typing import Annotated

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_serializer


InteiroEstrito = Annotated[int, Field(strict=True)]
InteiroPositivo = Annotated[int, Field(strict=True, gt=0)]
CENTAVOS = Decimal("0.01")


# Estados que delimitam o ciclo de vida permitido para um pedido.
class StatusPedido(str, Enum):
    RECEBIDO = "RECEBIDO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


# Responsabilidade de contratos HTTP, mantida no mesmo módulo das rotas.
# Contrato de saída de cada alimento do cardápio.
class ItemCardapioResposta(BaseModel):
    id: int
    nome: str
    preco: str


# Dados mínimos que o cliente pode fornecer para um item.
class ItemPedidoSolicitado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_cardapio_id: InteiroEstrito
    quantidade: InteiroPositivo


# Corpo estrito aceito na criação de pedidos.
class PedidoCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    numero_mesa: InteiroPositivo
    itens: list[ItemPedidoSolicitado] = Field(min_length=1)


# Corpo estrito aceito para avançar ou cancelar um pedido.
class AtualizacaoStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: StatusPedido


# Item enriquecido com nome e preço oficiais para a resposta.
class ItemPedidoResposta(BaseModel):
    item_cardapio_id: int
    nome: str
    quantidade: int
    preco_unitario: str


# Representação completa de um pedido exposta pela API.
class PedidoResposta(BaseModel):
    id: int
    numero_mesa: int
    itens: list[ItemPedidoResposta]
    status: StatusPedido
    total: str
    criado_em: datetime

    @field_serializer("criado_em", when_used="json")
    def serializar_criado_em(self, valor: datetime) -> str:
        """Normaliza a data em UTC e usa o sufixo ISO 8601 ``Z``."""

        return valor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# Responsabilidade de cardápio e preços concentrada neste arquivo. O ``dict``
# usa o ID como chave para localizar um alimento diretamente durante a criação.
_cardapio = {
    1: {"id": 1, "nome": "Hambúrguer", "preco": Decimal("20.00")},
    2: {"id": 2, "nome": "X-Salada", "preco": Decimal("23.00")},
    3: {"id": 3, "nome": "Cachorro-quente", "preco": Decimal("15.00")},
    4: {"id": 4, "nome": "Misto-quente", "preco": Decimal("12.00")},
    5: {"id": 5, "nome": "Batata frita", "preco": Decimal("14.00")},
    6: {"id": 6, "nome": "Porção de nuggets", "preco": Decimal("16.00")},
}

# Responsabilidade de persistência e geração de IDs também fica neste módulo.
# O ``dict`` associa cada ID ao pedido completo. Ele existe apenas na memória do
# processo: fechar ou reiniciar o Uvicorn elimina seus dados e reinicia os IDs.
_pedidos: dict[int, PedidoResposta] = {}
_proximo_id = 1
# O Lock protege o dicionário e o contador se requisições concorrentes tentarem
# criar ou atualizar pedidos ao mesmo tempo.
_estado_lock = Lock()

# Responsabilidade de regras de negócio misturada ao restante da aplicação.
_transicoes_permitidas = {
    StatusPedido.RECEBIDO: frozenset(
        {StatusPedido.EM_PREPARO, StatusPedido.CANCELADO}
    ),
    StatusPedido.EM_PREPARO: frozenset(
        {StatusPedido.PRONTO, StatusPedido.CANCELADO}
    ),
    StatusPedido.PRONTO: frozenset({StatusPedido.ENTREGUE}),
    StatusPedido.ENTREGUE: frozenset(),
    StatusPedido.CANCELADO: frozenset(),
}


# Responsabilidade de composição e HTTP no mesmo arquivo monolítico.
app = FastAPI(title="Pedidos da Lanchonete — Contraexemplo sem SRP")


@app.get("/api/cardapio", response_model=list[ItemCardapioResposta])
async def listar_cardapio() -> list[ItemCardapioResposta]:
    # Retorna os seis itens convertendo Decimal em string monetária.
    # A rota acessa e serializa diretamente o cardápio local.
    return [
        ItemCardapioResposta(
            id=item["id"],
            nome=item["nome"],
            preco=format(item["preco"], ".2f"),
        )
        for item in _cardapio.values()
    ]


@app.post(
    "/api/pedidos",
    response_model=PedidoResposta,
    status_code=status.HTTP_201_CREATED,
)
async def criar_pedido(dados: PedidoCriacao) -> PedidoResposta:
    # Esta rota valida, calcula, gera o ID e armazena o pedido, concentrando
    # tarefas separadas na versão com SRP. O ID só é consumido após a validação.
    global _proximo_id

    # Validação de negócio, composição dos itens e cálculo vivem na própria rota.
    itens_pedido: list[ItemPedidoResposta] = []
    for item_solicitado in dados.itens:
        item_cardapio = _cardapio.get(item_solicitado.item_cardapio_id)
        if item_cardapio is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item do cardápio não encontrado.",
            )

        itens_pedido.append(
            ItemPedidoResposta(
                item_cardapio_id=item_cardapio["id"],
                nome=item_cardapio["nome"],
                quantidade=item_solicitado.quantidade,
                preco_unitario=format(item_cardapio["preco"], ".2f"),
            )
        )

    # A precisão acompanha inteiros grandes para manter o cálculo exato.
    maior_quantidade = max(len(str(item.quantidade)) for item in itens_pedido)
    with localcontext() as contexto:
        contexto.prec = max(
            contexto.prec,
            maior_quantidade + len(str(len(itens_pedido))) + 8,
        )
        total = sum(
            (
                Decimal(item.preco_unitario) * item.quantidade
                for item in itens_pedido
            ),
            Decimal("0.00"),
        ).quantize(CENTAVOS)

    # O armazenamento e o contador são manipulados diretamente pela rota.
    with _estado_lock:
        pedido = PedidoResposta(
            id=_proximo_id,
            numero_mesa=dados.numero_mesa,
            itens=itens_pedido,
            status=StatusPedido.RECEBIDO,
            total=format(total, ".2f"),
            criado_em=datetime.now(timezone.utc),
        )
        _pedidos[_proximo_id] = pedido
        _proximo_id += 1

    return pedido


@app.get("/api/pedidos", response_model=list[PedidoResposta])
async def listar_pedidos() -> list[PedidoResposta]:
    # Lê o armazenamento em memória e devolve pedidos por ID crescente.
    # A rota consulta diretamente o dicionário que funciona como persistência.
    with _estado_lock:
        return [_pedidos[pedido_id] for pedido_id in sorted(_pedidos)]


@app.get("/api/pedidos/{pedido_id}", response_model=PedidoResposta)
async def buscar_pedido(pedido_id: int) -> PedidoResposta:
    # Busca diretamente no dicionário ou responde HTTP 404.
    with _estado_lock:
        pedido = _pedidos.get(pedido_id)
    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado.",
        )
    return pedido


@app.patch(
    "/api/pedidos/{pedido_id}/status",
    response_model=PedidoResposta,
)
async def atualizar_status(
    pedido_id: int,
    dados: AtualizacaoStatus,
) -> PedidoResposta:
    # Aplica idempotência e a tabela de transições ao pedido armazenado.
    # Busca, regra de transição, persistência e erro HTTP estão na mesma rota.
    with _estado_lock:
        pedido = _pedidos.get(pedido_id)
        if pedido is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado.",
            )

        if dados.status == pedido.status:
            return pedido
        if dados.status not in _transicoes_permitidas[pedido.status]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transição de status não permitida.",
            )

        pedido = pedido.model_copy(update={"status": dados.status})
        _pedidos[pedido_id] = pedido
        return pedido
