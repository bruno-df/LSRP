import { CartaoPedido, type AtualizarStatusHandler } from './CartaoPedido'
import type { Pedido } from '../types/api'

interface ListaPedidosProps {
  pedidos: readonly Pedido[]
  carregando: boolean
  erro?: string | null
  pedidosEmAtualizacao: ReadonlySet<number>
  onAtualizarStatus: AtualizarStatusHandler
}

export function ListaPedidos({
  pedidos,
  carregando,
  erro = null,
  pedidosEmAtualizacao,
  onAtualizarStatus,
}: ListaPedidosProps) {
  if (carregando) {
    return (
      <div className="loading-state" role="status" aria-live="polite">
        Carregando pedidos…
      </div>
    )
  }

  if (erro) {
    return (
      <div className="error-state" role="alert">
        <strong>Não foi possível carregar os pedidos.</strong>
        <p>{erro}</p>
      </div>
    )
  }

  if (pedidos.length === 0) {
    return (
      <div className="empty-state">
        <strong>Nenhum pedido por aqui</strong>
        <p>Os novos pedidos aparecerão nesta lista.</p>
      </div>
    )
  }

  return (
    <div className="orders-list" aria-label="Lista de pedidos">
      {pedidos.map((pedido) => (
        <CartaoPedido
          key={pedido.id}
          pedido={pedido}
          atualizando={pedidosEmAtualizacao.has(pedido.id)}
          onAtualizarStatus={onAtualizarStatus}
        />
      ))}
    </div>
  )
}
