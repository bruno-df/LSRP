import type {
  AtualizacaoStatus,
  CriacaoPedido,
  ItemCardapio,
  Pedido,
} from '../types/api'

// A base pode vir do ambiente de implantação. No desenvolvimento, "/api" faz
// as requisições passarem pelo proxy do Vite até o backend da porta 8000.
const urlConfigurada = import.meta.env.VITE_API_BASE_URL?.trim()
const API_BASE_URL = (urlConfigurada || '/api').replace(/\/+$/, '')

// Record cria um mapa tipado: o código HTTP é a chave e a mensagem é o valor.
const mensagensPorStatus: Readonly<Record<number, string>> = {
  400: 'A solicitação não pôde ser processada.',
  404: 'O recurso solicitado não foi encontrado.',
  422: 'Os dados informados são inválidos.',
}

/** Erro uniforme usado pela interface para falhas HTTP, de rede ou de JSON. */
export class ErroApi extends Error {
  readonly status: number | null

  constructor(
    mensagem: string,
    status: number | null = null,
    options?: ErrorOptions,
  ) {
    // Preserva a mensagem e a causa originais da classe Error.
    super(mensagem, options)
    this.name = 'ErroApi'
    this.status = status
  }
}

/**
 * Type guard que confirma em tempo de execução se um valor desconhecido pode
 * ser lido como objeto com chaves de texto.
 */
function ehRegistro(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === 'object' && valor !== null && !Array.isArray(valor)
}

/** Converte uma localização Pydantic, como body.itens.0, em texto legível. */
function formatarLocalizacao(valor: unknown): string | null {
  if (!Array.isArray(valor)) {
    return null
  }

  const partes = valor.filter(
    (parte): parte is string | number =>
      typeof parte === 'string' || typeof parte === 'number',
  )

  return partes.length > 0 ? partes.join('.') : null
}

/** Extrai mensagem e localização de um único detalhe de erro da API. */
function formatarItemDetalhe(valor: unknown): string | null {
  if (typeof valor === 'string') {
    return valor.trim() || null
  }

  if (!ehRegistro(valor)) {
    return null
  }

  const mensagem =
    typeof valor.msg === 'string'
      ? valor.msg.trim()
      : typeof valor.message === 'string'
        ? valor.message.trim()
        : typeof valor.detail === 'string'
          ? valor.detail.trim()
          : ''

  if (!mensagem) {
    return null
  }

  const localizacao = formatarLocalizacao(valor.loc)
  return localizacao ? `${localizacao}: ${mensagem}` : mensagem
}

/** Une os formatos possíveis do campo detail em uma única mensagem. */
function normalizarDetalhe(valor: unknown): string | null {
  if (Array.isArray(valor)) {
    const mensagens = valor
      .map(formatarItemDetalhe)
      .filter((mensagem): mensagem is string => mensagem !== null)

    return mensagens.length > 0 ? mensagens.join('; ') : null
  }

  return formatarItemDetalhe(valor)
}

/** Fornece uma mensagem amigável quando o backend não envia uma utilizável. */
function mensagemPadrao(status: number): string {
  return (
    mensagensPorStatus[status] ??
    `O servidor não conseguiu processar a solicitação (HTTP ${status}).`
  )
}

/** Lê com segurança texto ou JSON de uma resposta HTTP malsucedida. */
async function obterMensagemErro(response: Response): Promise<string> {
  const padrao = mensagemPadrao(response.status)
  let texto: string

  try {
    texto = await response.text()
  } catch {
    return padrao
  }

  if (!texto.trim()) {
    return padrao
  }

  let corpo: unknown
  try {
    corpo = JSON.parse(texto) as unknown
  } catch {
    return texto.trim()
  }

  const detalhe = ehRegistro(corpo) && 'detail' in corpo ? corpo.detail : corpo
  return normalizarDetalhe(detalhe) ?? padrao
}

/**
 * Executa a parte comum de todas as chamadas HTTP.
 *
 * O tipo genérico T descreve o formato esperado na resposta para que cada
 * função pública mantenha tipagem específica sem repetir fetch e tratamento de
 * erros. O backend continua sendo a autoridade que valida os dados recebidos.
 */
async function requisitar<T>(caminho: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  headers.set('Accept', 'application/json')

  if (init?.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${caminho}`, {
      ...init,
      headers,
    })
  } catch (causa: unknown) {
    throw new ErroApi(
      'Não foi possível conectar ao servidor. Verifique se o backend está ativo.',
      null,
      { cause: causa },
    )
  }

  if (!response.ok) {
    throw new ErroApi(await obterMensagemErro(response), response.status)
  }

  try {
    return (await response.json()) as T
  } catch (causa: unknown) {
    throw new ErroApi(
      'O servidor retornou uma resposta inválida.',
      response.status,
      { cause: causa },
    )
  }
}

/** Busca o cardápio e permite cancelamento durante a desmontagem da tela. */
export function listarCardapio(signal?: AbortSignal): Promise<ItemCardapio[]> {
  return requisitar<ItemCardapio[]>('/cardapio', { signal })
}

/** Envia somente mesa, IDs dos itens e quantidades para criar um pedido. */
export function criarPedido(dados: CriacaoPedido): Promise<Pedido> {
  return requisitar<Pedido>('/pedidos', {
    method: 'POST',
    body: JSON.stringify(dados),
  })
}

/** Carrega todos os pedidos armazenados no processo atual do backend. */
export function listarPedidos(signal?: AbortSignal): Promise<Pedido[]> {
  return requisitar<Pedido[]>('/pedidos', { signal })
}

/** Consulta um pedido diretamente pelo seu identificador numérico. */
export function buscarPedido(pedidoId: number): Promise<Pedido> {
  return requisitar<Pedido>(`/pedidos/${pedidoId}`)
}

/** Solicita uma transição de status e devolve o pedido atualizado. */
export function atualizarStatus(
  pedidoId: number,
  dados: AtualizacaoStatus,
): Promise<Pedido> {
  return requisitar<Pedido>(`/pedidos/${pedidoId}/status`, {
    method: 'PATCH',
    body: JSON.stringify(dados),
  })
}
