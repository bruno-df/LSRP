/** União fechada dos únicos estados aceitos pelo backend. */
export type StatusPedido =
  | 'RECEBIDO'
  | 'EM_PREPARO'
  | 'PRONTO'
  | 'ENTREGUE'
  | 'CANCELADO'

/** Item público recebido do cardápio; preço chega como string decimal. */
export interface ItemCardapio {
  id: number
  nome: string
  preco: string
}

/** Item mínimo enviado pelo cliente na criação. */
export interface ItemPedidoSolicitado {
  item_cardapio_id: number
  quantidade: number
}

/** Corpo completo de POST /api/pedidos. */
export interface CriacaoPedido {
  numero_mesa: number
  itens: ItemPedidoSolicitado[]
}

/** Item enriquecido pelo backend dentro de um pedido persistido. */
export interface ItemPedidoResposta {
  item_cardapio_id: number
  nome: string
  quantidade: number
  preco_unitario: string
}

/** Espelho TypeScript do contrato de resposta PedidoResposta. */
export interface Pedido {
  id: number
  numero_mesa: number
  itens: ItemPedidoResposta[]
  status: StatusPedido
  total: string
  criado_em: string
}

/** Corpo completo de PATCH /api/pedidos/{id}/status. */
export interface AtualizacaoStatus {
  status: StatusPedido
}
