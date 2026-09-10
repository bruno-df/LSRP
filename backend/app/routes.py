"""Rotas HTTP e tradução dos erros da aplicação."""

from fastapi import APIRouter, HTTPException, status

from .cardapio import Cardapio
from .schemas import (
    AtualizacaoStatus,
    ItemCardapioResposta,
    PedidoCriacao,
    PedidoResposta,
)
from .service import (
    ItemCardapioNaoEncontrado,
    PedidoNaoEncontrado,
    ServicoPedidos,
    TransicaoStatusInvalida,
)


def criar_router(cardapio: Cardapio, servico: ServicoPedidos) -> APIRouter:
    """Cria as rotas HTTP conectadas às dependências recebidas."""

    router = APIRouter(prefix="/api")

    @router.get("/cardapio", response_model=list[ItemCardapioResposta])
    async def listar_cardapio() -> list[ItemCardapioResposta]:
        # Lista o catálogo convertendo domínio em objetos de resposta.
        return [
            ItemCardapioResposta.de_dominio(item) for item in cardapio.listar()
        ]

    @router.post(
        "/pedidos",
        response_model=PedidoResposta,
        status_code=status.HTTP_201_CREATED,
    )
    async def criar_pedido(dados: PedidoCriacao) -> PedidoResposta:
        # Encaminha a criação ao serviço e converte erro de item em HTTP 400.
        try:
            pedido = servico.criar_pedido(
                numero_mesa=dados.numero_mesa,
                itens=[
                    (item.item_cardapio_id, item.quantidade)
                    for item in dados.itens
                ],
            )
        except ItemCardapioNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(erro),
            ) from erro
        return PedidoResposta.de_dominio(pedido)

    @router.get("/pedidos", response_model=list[PedidoResposta])
    async def listar_pedidos() -> list[PedidoResposta]:
        # Lista todos os pedidos usando o formato público da API.
        return [
            PedidoResposta.de_dominio(pedido)
            for pedido in servico.listar_pedidos()
        ]

    @router.get("/pedidos/{pedido_id}", response_model=PedidoResposta)
    async def buscar_pedido(pedido_id: int) -> PedidoResposta:
        # Consulta um pedido e devolve HTTP 404 quando ele não existe.
        try:
            pedido = servico.buscar_pedido(pedido_id)
        except PedidoNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro
        return PedidoResposta.de_dominio(pedido)

    @router.patch(
        "/pedidos/{pedido_id}/status",
        response_model=PedidoResposta,
    )
    async def atualizar_status(
        pedido_id: int,
        dados: AtualizacaoStatus,
    ) -> PedidoResposta:
        # Atualiza o status e traduz falhas de negócio para erros HTTP.
        try:
            pedido = servico.atualizar_status(pedido_id, dados.status)
        except PedidoNaoEncontrado as erro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(erro),
            ) from erro
        except TransicaoStatusInvalida as erro:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(erro),
            ) from erro
        return PedidoResposta.de_dominio(pedido)

    return router
