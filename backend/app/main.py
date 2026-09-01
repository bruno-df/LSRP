"""Composição da aplicação e de suas dependências."""

from fastapi import FastAPI

from .cardapio import Cardapio
from .repository import RepositorioPedidosMemoria
from .routes import criar_router
from .service import ServicoPedidos


def criar_app() -> FastAPI:
    cardapio = Cardapio()
    repositorio = RepositorioPedidosMemoria()
    servico = ServicoPedidos(repositorio, cardapio)

    aplicacao = FastAPI(title="Pedidos da Lanchonete")
    aplicacao.include_router(criar_router(cardapio, servico))
    return aplicacao


app = criar_app()
