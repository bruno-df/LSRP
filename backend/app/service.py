"""Casos de uso e regras de negócio dos pedidos."""

from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal, localcontext

from .cardapio import Cardapio
from .models import ItemPedido, Pedido, StatusPedido
from .repository import RepositorioPedidosMemoria


class ItemCardapioNaoEncontrado(ValueError):
    """Indica que a criação referenciou um item que não existe."""

    def __init__(self) -> None:
        """Cria o erro com a mensagem pública definida pelo contrato."""

        super().__init__("Item do cardápio não encontrado.")


class PedidoNaoEncontrado(LookupError):
    """Indica que não há pedido armazenado para o ID solicitado."""

    def __init__(self) -> None:
        """Cria o erro com a mensagem pública definida pelo contrato."""

        super().__init__("Pedido não encontrado.")


class TransicaoStatusInvalida(ValueError):
    """Indica tentativa de pular ou reverter uma etapa do pedido."""

    def __init__(self) -> None:
        """Cria o erro com a mensagem pública definida pelo contrato."""

        super().__init__("Transição de status não permitida.")


_TRANSICOES_PERMITIDAS = {
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
_CENTAVOS = Decimal("0.01")


class ServicoPedidos:
    """Centraliza os casos de uso e as regras de negócio dos pedidos."""

    def __init__(
        self,
        repositorio: RepositorioPedidosMemoria,
        cardapio: Cardapio,
    ) -> None:
        """Recebe persistência e cardápio sem criá-los internamente.

        Essa injeção mantém o serviço focado em negócio e permite trocar suas
        dependências sem alterar as regras aqui implementadas.
        """

        self._repositorio = repositorio
        self._cardapio = cardapio

    def criar_pedido(
        self,
        numero_mesa: int,
        itens: Sequence[tuple[int, int]],
    ) -> Pedido:
        """Valida, calcula, monta e persiste um novo pedido.

        Os dados comerciais vêm do cardápio, não da requisição, impedindo que o
        cliente escolha nomes ou preços diferentes dos oficiais.
        """

        if numero_mesa <= 0:
            raise ValueError("O número da mesa deve ser positivo.")
        if not itens:
            raise ValueError("O pedido deve possuir pelo menos um item.")

        itens_pedido: list[ItemPedido] = []
        for item_cardapio_id, quantidade in itens:
            if quantidade <= 0:
                raise ValueError("A quantidade deve ser positiva.")

            item_cardapio = self._cardapio.buscar_por_id(item_cardapio_id)
            if item_cardapio is None:
                raise ItemCardapioNaoEncontrado()

            itens_pedido.append(
                ItemPedido(
                    item_cardapio_id=item_cardapio.id,
                    nome=item_cardapio.nome,
                    quantidade=quantidade,
                    preco_unitario=item_cardapio.preco,
                )
            )

        # O contrato não limita a quantidade; a precisão acompanha o tamanho
        # dos inteiros recebidos para o cálculo continuar exato.
        maior_quantidade = max(
            len(str(item.quantidade)) for item in itens_pedido
        )
        with localcontext() as contexto:
            contexto.prec = max(
                contexto.prec,
                maior_quantidade + len(str(len(itens_pedido))) + 8,
            )
            total = sum(
                (
                    item.preco_unitario * item.quantidade
                    for item in itens_pedido
                ),
                Decimal("0.00"),
            ).quantize(_CENTAVOS)

        pedido = Pedido(
            id=None,
            numero_mesa=numero_mesa,
            itens=tuple(itens_pedido),
            status=StatusPedido.RECEBIDO,
            total=total,
            criado_em=datetime.now(timezone.utc),
        )
        return self._repositorio.salvar(pedido)

    def listar_pedidos(self) -> list[Pedido]:
        """Solicita ao repositório a lista ordenada de pedidos."""

        return self._repositorio.listar()

    def buscar_pedido(self, pedido_id: int) -> Pedido:
        """Busca um pedido e transforma ausência em erro de negócio."""

        pedido = self._repositorio.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNaoEncontrado()
        return pedido

    def atualizar_status(
        self,
        pedido_id: int,
        novo_status: StatusPedido,
    ) -> Pedido:
        """Mantém o status atual ou aplica somente uma transição permitida."""

        pedido = self.buscar_pedido(pedido_id)

        if novo_status == pedido.status:
            return pedido
        if novo_status not in _TRANSICOES_PERMITIDAS[pedido.status]:
            raise TransicaoStatusInvalida()

        return self._repositorio.salvar(replace(pedido, status=novo_status))
