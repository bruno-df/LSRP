"""Composição da aplicação e de suas dependências."""

from fastapi import FastAPI

from .cardapio import Cardapio
from .repository import RepositorioPedidosMemoria
from .routes import criar_router
from .service import ServicoPedidos


def criar_app() -> FastAPI:
    """Monta uma aplicação independente e conecta suas camadas.

    Cada chamada cria um repositório em memória novo. Isso é útil nos testes,
    pois cada aplicação começa sem pedidos e com o contador de IDs em ``1``.
    """

    cardapio = Cardapio()
    repositorio = RepositorioPedidosMemoria()
    servico = ServicoPedidos(repositorio, cardapio)

    aplicacao = FastAPI(title="Pedidos da Lanchonete")
    aplicacao.include_router(criar_router(cardapio, servico))
    return aplicacao


app = criar_app()
