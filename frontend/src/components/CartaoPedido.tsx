import { useId } from 'react'

import type { Pedido, StatusPedido } from '../types/api'

export type AtualizarStatusHandler = (
  pedidoId: number,
  status: StatusPedido,
) => void | Promise<void>

interface CartaoPedidoProps {
  pedido: Pedido
  atualizando: boolean
  onAtualizarStatus: AtualizarStatusHandler
}

interface AcaoStatus {
  rotulo: string
  proximoStatus: StatusPedido
  variante: 'primary' | 'danger'
}

const ACOES_POR_STATUS: Record<StatusPedido, readonly AcaoStatus[]> = {
  RECEBIDO: [
    {
      rotulo: 'Iniciar preparo',
      proximoStatus: 'EM_PREPARO',
      variante: 'primary',
    },
    {
      rotulo: 'Cancelar',
      proximoStatus: 'CANCELADO',
      variante: 'danger',
    },
  ],
  EM_PREPARO: [
    {
      rotulo: 'Marcar como pronto',
      proximoStatus: 'PRONTO',
      variante: 'primary',
    },
    {
      rotulo: 'Cancelar',
      proximoStatus: 'CANCELADO',
      variante: 'danger',
    },
  ],
  PRONTO: [
    {
      rotulo: 'Marcar como entregue',
      proximoStatus: 'ENTREGUE',
      variante: 'primary',
    },
  ],
  ENTREGUE: [],
  CANCELADO: [],
}

const ROTULOS_STATUS: Record<StatusPedido, string> = {
  RECEBIDO: 'Recebido',
  EM_PREPARO: 'Em preparo',
  PRONTO: 'Pronto',
  ENTREGUE: 'Entregue',
  CANCELADO: 'Cancelado',
}

const CLASSES_STATUS: Record<StatusPedido, string> = {
  RECEBIDO: 'status-recebido',
  EM_PREPARO: 'status-em-preparo',
  PRONTO: 'status-pronto',
  ENTREGUE: 'status-entregue',
  CANCELADO: 'status-cancelado',
}

const formatadorMoeda = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

const formatadorData = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'short',
  timeStyle: 'short',
})

function formatarMoeda(valor: string): string {
  const valorNumerico = Number(valor)

  return Number.isFinite(valorNumerico)
    ? formatadorMoeda.format(valorNumerico)
    : valor
}

function formatarData(dataIso: string): string {
  const data = new Date(dataIso)

  return Number.isNaN(data.getTime()) ? dataIso : formatadorData.format(data)
}

export function CartaoPedido({
  pedido,
  atualizando,
  onAtualizarStatus,
}: CartaoPedidoProps) {
  const idBase = useId()
  const acoes = ACOES_POR_STATUS[pedido.status]
  const tituloId = `${idBase}-titulo`
  const itensId = `${idBase}-itens`

  return (
    <article
      className="pedido-card"
      aria-labelledby={tituloId}
      aria-busy={atualizando}
    >
      <header className="pedido-card__header">
        <div>
          <p className="pedido-card__eyebrow">Pedido</p>
          <h3 id={tituloId}>#{pedido.id}</h3>
        </div>
        <span
          className={`status-badge ${CLASSES_STATUS[pedido.status]}`}
          aria-label={`Status do pedido: ${ROTULOS_STATUS[pedido.status]}`}
        >
          {ROTULOS_STATUS[pedido.status]}
        </span>
      </header>

      <dl className="pedido-meta">
        <div>
          <dt>Mesa</dt>
          <dd>{pedido.numero_mesa}</dd>
        </div>
        <div>
          <dt>Criado em</dt>
          <dd>
            <time dateTime={pedido.criado_em}>
              {formatarData(pedido.criado_em)}
            </time>
          </dd>
        </div>
      </dl>

      <section className="pedido-card__items" aria-labelledby={itensId}>
        <h4 id={itensId}>Itens do pedido</h4>
        <ul className="pedido-items">
          {pedido.itens.map((item, indice) => (
            <li
              key={`${item.item_cardapio_id}-${indice}`}
              className="pedido-item"
            >
              <div>
                <strong>{item.nome}</strong>
                <span>
                  {item.quantidade}{' '}
                  {item.quantidade === 1 ? 'unidade' : 'unidades'}
                </span>
              </div>
              <span>{formatarMoeda(item.preco_unitario)} cada</span>
            </li>
          ))}
        </ul>
      </section>

      <dl className="pedido-total">
        <dt>Total</dt>
        <dd>{formatarMoeda(pedido.total)}</dd>
      </dl>

      {acoes.length > 0 && (
        <div
          className="pedido-actions"
          aria-label={`Ações do pedido ${pedido.id}`}
        >
          {acoes.map((acao) => (
            <button
              key={acao.proximoStatus}
              type="button"
              className={`button button-${acao.variante}`}
              disabled={atualizando}
              onClick={() =>
                onAtualizarStatus(pedido.id, acao.proximoStatus)
              }
            >
              {acao.rotulo}
            </button>
          ))}
          {atualizando && (
            <span className="action-loading" role="status">
              Atualizando pedido…
            </span>
          )}
        </div>
      )}
    </article>
  )
}
