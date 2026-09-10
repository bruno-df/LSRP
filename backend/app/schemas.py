"""Contratos de entrada e saída da API HTTP."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .models import ItemCardapio, Pedido, StatusPedido


InteiroEstrito = Annotated[int, Field(strict=True)]
InteiroPositivo = Annotated[int, Field(strict=True, gt=0)]


def _formatar_valor(valor: object) -> str:
    """Serializa um valor monetário com exatamente duas casas decimais."""

    return format(valor, ".2f")


# Formato público de um item retornado por GET /api/cardapio.
class ItemCardapioResposta(BaseModel):
    id: int
    nome: str
    preco: str

    @classmethod
    def de_dominio(cls, item: ItemCardapio) -> "ItemCardapioResposta":
        """Converte a entidade de domínio para o contrato HTTP do cardápio."""

        return cls(id=item.id, nome=item.nome, preco=_formatar_valor(item.preco))


# Item mínimo aceito no corpo de criação de um pedido.
class ItemPedidoSolicitado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_cardapio_id: InteiroEstrito
    quantidade: InteiroPositivo


# Corpo aceito por POST /api/pedidos com validação estrita.
class PedidoCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    numero_mesa: InteiroPositivo
    itens: list[ItemPedidoSolicitado] = Field(min_length=1)


# Único campo aceito na atualização do estado de um pedido.
class AtualizacaoStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: StatusPedido


# Representação enriquecida de um item dentro de uma resposta de pedido.
class ItemPedidoResposta(BaseModel):
    item_cardapio_id: int
    nome: str
    quantidade: int
    preco_unitario: str


# Contrato completo devolvido pelos endpoints de pedidos.
class PedidoResposta(BaseModel):
    id: int
    numero_mesa: int
    itens: list[ItemPedidoResposta]
    status: StatusPedido
    total: str
    criado_em: datetime

    @field_serializer("criado_em", when_used="json")
    def serializar_criado_em(self, valor: datetime) -> str:
        """Converte a data para UTC ISO 8601 terminada em ``Z``."""

        return valor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @classmethod
    def de_dominio(cls, pedido: Pedido) -> "PedidoResposta":
        """Transforma uma entidade persistida em resposta segura para a API."""

        if pedido.id is None:
            raise ValueError("Um pedido não persistido não pode compor uma resposta.")

        return cls(
            id=pedido.id,
            numero_mesa=pedido.numero_mesa,
            itens=[
                ItemPedidoResposta(
                    item_cardapio_id=item.item_cardapio_id,
                    nome=item.nome,
                    quantidade=item.quantidade,
                    preco_unitario=_formatar_valor(item.preco_unitario),
                )
                for item in pedido.itens
            ],
            status=pedido.status,
            total=_formatar_valor(pedido.total),
            criado_em=pedido.criado_em,
        )
