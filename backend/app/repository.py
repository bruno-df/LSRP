"""Persistência em memória e geração de IDs dos pedidos."""

from dataclasses import replace
from threading import Lock

from .models import Pedido


class RepositorioPedidosMemoria:
    """Guarda pedidos enquanto o processo Python estiver em execução.

    O ``dict`` associa diretamente cada ID ao seu pedido. Isso torna simples e
    rápida a consulta por ID, mas não oferece persistência: ao fechar o servidor,
    o processo e o dicionário desaparecem, portanto todos os pedidos são perdidos.
    """

    def __init__(self) -> None:
        """Inicializa armazenamento vazio, próximo ID e trava de concorrência."""

        self._pedidos: dict[int, Pedido] = {}
        self._proximo_id = 1
        # Duas requisições podem chegar juntas; a trava evita IDs duplicados e
        # leituras durante uma alteração incompleta do dicionário.
        self._lock = Lock()

    def salvar(self, pedido: Pedido) -> Pedido:
        """Atribui ID a pedidos novos e insere ou atualiza o valor no ``dict``."""

        with self._lock:
            if pedido.id is None:
                pedido = replace(pedido, id=self._proximo_id)
                self._proximo_id += 1

            self._pedidos[pedido.id] = pedido
            return pedido

    def listar(self) -> list[Pedido]:
        """Retorna uma fotografia dos pedidos ordenada pelo ID crescente."""

        with self._lock:
            return [self._pedidos[pedido_id] for pedido_id in sorted(self._pedidos)]

    def buscar_por_id(self, pedido_id: int) -> Pedido | None:
        """Obtém diretamente um pedido pelo ID ou retorna ``None``."""

        with self._lock:
            return self._pedidos.get(pedido_id)
