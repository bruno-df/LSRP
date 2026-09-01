"""Entidades e tipos do domínio de pedidos."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class StatusPedido(str, Enum):
    RECEBIDO = "RECEBIDO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


@dataclass(frozen=True, slots=True)
class ItemCardapio:
    id: int
    nome: str
    preco: Decimal


@dataclass(frozen=True, slots=True)
class ItemPedido:
    item_cardapio_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal


@dataclass(frozen=True, slots=True)
class Pedido:
    # Um pedido ainda não salvo não possui ID; o repositório atribui um ao salvá-lo.
    id: int | None
    numero_mesa: int
    itens: tuple[ItemPedido, ...]
    status: StatusPedido
    total: Decimal
    criado_em: datetime
