export type StatusPedido =
  | 'RECEBIDO'
  | 'EM_PREPARO'
  | 'PRONTO'
  | 'ENTREGUE'
  | 'CANCELADO'

export interface ItemCardapio {
  id: number
  nome: string
  preco: string
}

export interface ItemPedidoSolicitado {
  item_cardapio_id: number
  quantidade: number
}

export interface CriacaoPedido {
  numero_mesa: number
  itens: ItemPedidoSolicitado[]
}

export interface ItemPedidoResposta {
  item_cardapio_id: number
  nome: string
  quantidade: number
  preco_unitario: string
}

export interface Pedido {
  id: number
  numero_mesa: number
  itens: ItemPedidoResposta[]
  status: StatusPedido
  total: string
  criado_em: string
}

export interface AtualizacaoStatus {
  status: StatusPedido
}
