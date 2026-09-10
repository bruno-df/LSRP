import { useState, type FormEvent } from 'react'

interface ConsultaPedidoProps {
  consultandoPedido: boolean
  onConsultarPedido: (pedidoId: number) => void
}

/** Formulário compacto que valida o ID antes de solicitar uma consulta real. */
function ConsultaPedido({
  consultandoPedido,
  onConsultarPedido,
}: ConsultaPedidoProps) {
  const [pedidoId, setPedidoId] = useState('')
  const [erroValidacao, setErroValidacao] = useState<string | null>(null)

  /** Impede recarregamento e encaminha somente um ID inteiro positivo. */
  function consultarPedido(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const id = Number(pedidoId)
    if (!Number.isInteger(id) || id <= 0) {
      setErroValidacao('Informe um ID de pedido inteiro e maior que zero.')
      return
    }

    setErroValidacao(null)
    onConsultarPedido(id)
  }

  return (
    <section
      className="panel compact-panel"
      aria-labelledby="consulta-pedido-titulo"
    >
      <div className="section-heading">
        <div>
          <p className="section-kicker">Consulta rápida</p>
          <h2 id="consulta-pedido-titulo">Buscar pedido</h2>
        </div>
      </div>

      <form noValidate onSubmit={consultarPedido} aria-busy={consultandoPedido}>
        <div className="search-row">
          <div>
            <label htmlFor="pedido-id">Número do pedido</label>
            <input
              id="pedido-id"
              name="pedido-id"
              type="number"
              min="1"
              step="1"
              inputMode="numeric"
              autoComplete="off"
              placeholder="Ex.: 12"
              value={pedidoId}
              disabled={consultandoPedido}
              aria-invalid={erroValidacao ? true : undefined}
              aria-describedby={erroValidacao ? 'erro-consulta-pedido' : undefined}
              onChange={(evento) => {
                setPedidoId(evento.currentTarget.value)
                setErroValidacao(null)
              }}
            />
          </div>

          <button
            type="submit"
            className="button button-secondary"
            disabled={consultandoPedido}
          >
            {consultandoPedido ? 'Consultando…' : 'Consultar'}
          </button>
        </div>

        {erroValidacao && (
          <p id="erro-consulta-pedido" className="form-error" role="alert">
            {erroValidacao}
          </p>
        )}
      </form>
    </section>
  )
}

export default ConsultaPedido
