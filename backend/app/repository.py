"""Persistência em memória e geração de IDs dos pedidos."""

from dataclasses import replace
from threading import Lock

from .models import Pedido


class RepositorioPedidosMemoria:
    def __init__(self) -> None:
        self._pedidos: dict[int, Pedido] = {}
        self._proximo_id = 1
        self._lock = Lock()

    def salvar(self, pedido: Pedido) -> Pedido:
        with self._lock:
            if pedido.id is None:
                pedido = replace(pedido, id=self._proximo_id)
                self._proximo_id += 1

            self._pedidos[pedido.id] = pedido
            return pedido

    def listar(self) -> list[Pedido]:
        with self._lock:
            return [self._pedidos[pedido_id] for pedido_id in sorted(self._pedidos)]

    def buscar_por_id(self, pedido_id: int) -> Pedido | None:
        with self._lock:
            return self._pedidos.get(pedido_id)
