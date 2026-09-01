"""Catálogo fixo e somente leitura da lanchonete."""

from decimal import Decimal
from types import MappingProxyType

from .models import ItemCardapio


_ITENS = (
    ItemCardapio(1, "Hambúrguer", Decimal("20.00")),
    ItemCardapio(2, "X-Salada", Decimal("23.00")),
    ItemCardapio(3, "Cachorro-quente", Decimal("15.00")),
    ItemCardapio(4, "Misto-quente", Decimal("12.00")),
    ItemCardapio(5, "Batata frita", Decimal("14.00")),
    ItemCardapio(6, "Porção de nuggets", Decimal("16.00")),
)
_ITENS_POR_ID = MappingProxyType({item.id: item for item in _ITENS})


class Cardapio:
    def listar(self) -> tuple[ItemCardapio, ...]:
        return _ITENS

    def buscar_por_id(self, item_id: int) -> ItemCardapio | None:
        return _ITENS_POR_ID.get(item_id)
