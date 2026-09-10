import { useMemo, useState, type FormEvent } from 'react'

import type { CriacaoPedido, ItemCardapio } from '../types/api'

interface FormularioPedidoProps {
  cardapio: ItemCardapio[]
  carregandoCardapio: boolean
  criandoPedido: boolean
  erroCardapio?: string | null
  onCriarPedido: (dados: CriacaoPedido) => Promise<boolean>
}

const formatadorMoeda = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

/**
 * Formulário controlado que transforma as quantidades do cardápio no contrato
 * mínimo de criação aceito pelo backend.
 */
function FormularioPedido({
  cardapio,
  carregandoCardapio,
  criandoPedido,
  erroCardapio = null,
  onCriarPedido,
}: FormularioPedidoProps) {
  const [numeroMesa, setNumeroMesa] = useState('')
  // O Record funciona como um dicionário no navegador: itemId -> quantidade.
  // Itens ainda não editados usam zero como padrão e não ocupam uma entrada.
  const [quantidades, setQuantidades] = useState<Record<number, number>>({})
  const [erroValidacao, setErroValidacao] = useState<string | null>(null)
  const [aguardandoCriacao, setAguardandoCriacao] = useState(false)

  // useMemo recalcula apenas quando cardápio ou quantidades mudam, evitando
  // reconstruir o corpo do pedido em renderizações não relacionadas.
  const itensSelecionados = useMemo(
    () =>
      cardapio
        .map((item) => ({
          item_cardapio_id: item.id,
          quantidade: quantidades[item.id] ?? 0,
        }))
        .filter((item) => item.quantidade > 0),
    [cardapio, quantidades],
  )

  // Este total é apenas uma prévia visual. O total definitivo sempre vem da API.
  const totalEstimado = useMemo(
    () =>
      cardapio.reduce(
        (total, item) =>
          total + Number(item.preco) * (quantidades[item.id] ?? 0),
        0,
      ),
    [cardapio, quantidades],
  )

  const enviando = criandoPedido || aguardandoCriacao
  const cardapioIndisponivel = carregandoCardapio || cardapio.length === 0

  /** Aceita somente quantidades inteiras não negativas no estado do formulário. */
  function alterarQuantidade(itemId: number, valor: string) {
    const quantidade = valor === '' ? 0 : Number(valor)

    if (!Number.isInteger(quantidade) || quantidade < 0) {
      return
    }

    setQuantidades((atuais) => ({ ...atuais, [itemId]: quantidade }))
    setErroValidacao(null)
  }

  /** Valida a tela, monta o contrato da API e aguarda a criação do pedido. */
  async function enviarPedido(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const mesa = Number(numeroMesa)
    if (!Number.isInteger(mesa) || mesa <= 0) {
      setErroValidacao('Informe um número de mesa inteiro e maior que zero.')
      return
    }

    if (itensSelecionados.length === 0) {
      setErroValidacao('Selecione ao menos um item do cardápio.')
      return
    }

    setErroValidacao(null)
    setAguardandoCriacao(true)

    try {
      const pedidoCriado = await onCriarPedido({
        numero_mesa: mesa,
        itens: itensSelecionados,
      })

      if (pedidoCriado) {
        setNumeroMesa('')
        setQuantidades({})
      }
    } finally {
      setAguardandoCriacao(false)
    }
  }

  return (
    <section className="panel" aria-labelledby="novo-pedido-titulo">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Atendimento</p>
          <h2 id="novo-pedido-titulo">Novo pedido</h2>
        </div>
        <span className="step-marker" aria-hidden="true">
          01
        </span>
      </div>

      <form noValidate onSubmit={enviarPedido} aria-busy={enviando}>
        <label htmlFor="numero-mesa">Número da mesa</label>
        <input
          id="numero-mesa"
          name="numero-mesa"
          type="number"
          min="1"
          step="1"
          inputMode="numeric"
          placeholder="Ex.: 7"
          value={numeroMesa}
          disabled={enviando}
          aria-invalid={
            erroValidacao?.startsWith('Informe um número de mesa') || undefined
          }
          aria-describedby={
            erroValidacao?.startsWith('Informe um número de mesa')
              ? 'erro-formulario-pedido'
              : undefined
          }
          onChange={(evento) => {
            setNumeroMesa(evento.currentTarget.value)
            setErroValidacao(null)
          }}
        />

        <fieldset className="menu-fieldset" disabled={enviando}>
          <legend>Itens do cardápio</legend>

          {carregandoCardapio ? (
            <p className="menu-placeholder" role="status">
              Carregando cardápio…
            </p>
          ) : erroCardapio ? (
            <p className="menu-placeholder form-error" role="alert">
              {erroCardapio}
            </p>
          ) : cardapio.length === 0 ? (
            <p className="menu-placeholder" role="status">
              Nenhum item disponível no cardápio.
            </p>
          ) : (
            <div className="menu-list">
              {cardapio.map((item) => (
                <div className="menu-item" key={item.id}>
                  <div className="menu-item__description">
                    <strong>{item.nome}</strong>
                    <span>{formatadorMoeda.format(Number(item.preco))}</span>
                  </div>

                  <div className="quantity-field">
                    <label htmlFor={`quantidade-${item.id}`}>
                      Quantidade de {item.nome}
                    </label>
                    <input
                      id={`quantidade-${item.id}`}
                      name={`quantidade-${item.id}`}
                      type="number"
                      min="0"
                      step="1"
                      inputMode="numeric"
                      value={quantidades[item.id] ?? 0}
                      onChange={(evento) =>
                        alterarQuantidade(item.id, evento.currentTarget.value)
                      }
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </fieldset>

        {erroValidacao && (
          <p id="erro-formulario-pedido" className="form-error" role="alert">
            {erroValidacao}
          </p>
        )}

        <div className="order-summary" aria-live="polite">
          <span>Total estimado</span>
          <strong>{formatadorMoeda.format(totalEstimado)}</strong>
        </div>

        <button
          type="submit"
          className="button button-primary"
          disabled={enviando || cardapioIndisponivel}
        >
          {enviando ? 'Criando pedido…' : 'Criar pedido'}
        </button>
      </form>
    </section>
  )
}

export default FormularioPedido
