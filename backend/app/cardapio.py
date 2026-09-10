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
# MappingProxyType oferece uma visão somente leitura do dicionário. A tupla
# preserva a ordem de exibição; o mapa permite buscar um ID sem percorrer tudo.
_ITENS_POR_ID = MappingProxyType({item.id: item for item in _ITENS})


class Cardapio:
    """Fornece leitura do catálogo fixo sem permitir alterações externas."""

    def listar(self) -> tuple[ItemCardapio, ...]:
        """Retorna todos os itens na ordem oficial do cardápio."""

        return _ITENS

    def buscar_por_id(self, item_id: int) -> ItemCardapio | None:
        """Busca um item em tempo constante ou devolve ``None`` se não existir."""

        return _ITENS_POR_ID.get(item_id)
