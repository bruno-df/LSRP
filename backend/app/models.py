"""Entidades e tipos do domínio de pedidos."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


# Estados possíveis de um pedido ao longo do atendimento.
class StatusPedido(str, Enum):
    RECEBIDO = "RECEBIDO"
    EM_PREPARO = "EM_PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


@dataclass(frozen=True, slots=True)
class ItemCardapio:
    """Alimento imutável disponibilizado pelo cardápio da lanchonete."""

    id: int
    nome: str
    preco: Decimal


@dataclass(frozen=True, slots=True)
class ItemPedido:
    """Cópia dos dados comerciais de um item no momento da compra.

    Nome e preço são guardados no pedido para que ele não dependa de futuras
    alterações no cardápio para representar o que foi efetivamente comprado.
    """

    item_cardapio_id: int
    nome: str
    quantidade: int
    preco_unitario: Decimal


@dataclass(frozen=True, slots=True)
class Pedido:
    """Entidade imutável que representa um pedido e seu estado atual."""

    # Um pedido ainda não salvo não possui ID; o repositório atribui um ao salvá-lo.
    id: int | None
    numero_mesa: int
    itens: tuple[ItemPedido, ...]
    status: StatusPedido
    total: Decimal
    criado_em: datetime
