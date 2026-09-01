"""Contratos de entrada e saída da API HTTP."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .models import ItemCardapio, Pedido, StatusPedido


InteiroEstrito = Annotated[int, Field(strict=True)]
InteiroPositivo = Annotated[int, Field(strict=True, gt=0)]


def _formatar_valor(valor: object) -> str:
    return format(valor, ".2f")


class ItemCardapioResposta(BaseModel):
    id: int
    nome: str
    preco: str

    @classmethod
    def de_dominio(cls, item: ItemCardapio) -> "ItemCardapioResposta":
        return cls(id=item.id, nome=item.nome, preco=_formatar_valor(item.preco))


class ItemPedidoSolicitado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_cardapio_id: InteiroEstrito
    quantidade: InteiroPositivo


class PedidoCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    numero_mesa: InteiroPositivo
    itens: list[ItemPedidoSolicitado] = Field(min_length=1)


class AtualizacaoStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: StatusPedido


class ItemPedidoResposta(BaseModel):
    item_cardapio_id: int
    nome: str
    quantidade: int
    preco_unitario: str


class PedidoResposta(BaseModel):
    id: int
    numero_mesa: int
    itens: list[ItemPedidoResposta]
    status: StatusPedido
    total: str
    criado_em: datetime

    @field_serializer("criado_em", when_used="json")
    def serializar_criado_em(self, valor: datetime) -> str:
        return valor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    @classmethod
    def de_dominio(cls, pedido: Pedido) -> "PedidoResposta":
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
