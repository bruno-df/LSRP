import { useEffect, useRef, useState } from 'react'

import {
  ErroApi,
  atualizarStatus,
  buscarPedido,
  criarPedido,
  listarCardapio,
  listarPedidos,
} from './api/pedidosApi'
import { CartaoPedido } from './components/CartaoPedido'
import ConsultaPedido from './components/ConsultaPedido'
import FormularioPedido from './components/FormularioPedido'
import { ListaPedidos } from './components/ListaPedidos'
import type {
  CriacaoPedido,
  ItemCardapio,
  Pedido,
  StatusPedido,
} from './types/api'
import './App.css'

interface MensagemInterface {
  tipo: 'sucesso' | 'erro'
  texto: string
}

const formatadorMoeda = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
})

function mensagemDoErro(erro: unknown): string {
  return erro instanceof Error
    ? erro.message
    : 'Não foi possível concluir a operação.'
}

function substituirPedido(lista: Pedido[], pedidoAtualizado: Pedido): Pedido[] {
  const pedidoExiste = lista.some((pedido) => pedido.id === pedidoAtualizado.id)

  if (!pedidoExiste) {
    return [...lista, pedidoAtualizado].sort((a, b) => a.id - b.id)
  }

  return lista.map((pedido) =>
    pedido.id === pedidoAtualizado.id ? pedidoAtualizado : pedido,
  )
}

function App() {
  const [cardapio, setCardapio] = useState<ItemCardapio[]>([])
  const [pedidos, setPedidos] = useState<Pedido[]>([])
  const [pedidoConsultado, setPedidoConsultado] = useState<Pedido | null>(null)
  const [carregandoCardapio, setCarregandoCardapio] = useState(true)
  const [carregandoPedidos, setCarregandoPedidos] = useState(true)
  const [criandoPedido, setCriandoPedido] = useState(false)
  const [consultandoPedido, setConsultandoPedido] = useState(false)
  const atualizacoesAtivas = useRef(new Set<number>())
  const [pedidosEmAtualizacao, setPedidosEmAtualizacao] = useState<
    ReadonlySet<number>
  >(
    () => new Set(),
  )
  const [erroCardapio, setErroCardapio] = useState<string | null>(null)
  const [erroPedidos, setErroPedidos] = useState<string | null>(null)
  const [mensagem, setMensagem] = useState<MensagemInterface | null>(null)

  useEffect(() => {
    let telaAtiva = true
    const controlador = new AbortController()

    function registrarErroInicial(texto: string) {
      setMensagem((atual) => {
        const textos = new Set(
          atual?.tipo === 'erro' ? [atual.texto, texto] : [texto],
        )
        return { tipo: 'erro', texto: [...textos].join(' ') }
      })
    }

    async function carregarCardapio() {
      try {
        const itens = await listarCardapio(controlador.signal)
        if (!telaAtiva) return
        setCardapio(itens)
        setErroCardapio(null)
      } catch (erro: unknown) {
        if (!telaAtiva) return
        const texto = mensagemDoErro(erro)
        setErroCardapio(texto)
        registrarErroInicial(texto)
      } finally {
        if (telaAtiva) setCarregandoCardapio(false)
      }
    }

    async function carregarListaPedidos() {
      try {
        const pedidosCarregados = await listarPedidos(controlador.signal)
        if (!telaAtiva) return
        setPedidos(pedidosCarregados)
        setErroPedidos(null)
      } catch (erro: unknown) {
        if (!telaAtiva) return
        const texto = mensagemDoErro(erro)
        setErroPedidos(texto)
        registrarErroInicial(texto)
      } finally {
        if (telaAtiva) setCarregandoPedidos(false)
      }
    }

    void carregarCardapio()
    void carregarListaPedidos()

    return () => {
      telaAtiva = false
      controlador.abort()
    }
  }, [])

  async function criarNovoPedido(dados: CriacaoPedido): Promise<boolean> {
    setCriandoPedido(true)
    setMensagem(null)

    try {
      const pedidoCriado = await criarPedido(dados)
      setPedidos((atuais) => substituirPedido(atuais, pedidoCriado))
      setErroPedidos(null)
      setMensagem({
        tipo: 'sucesso',
        texto: `Pedido #${pedidoCriado.id} criado com sucesso. Total definitivo: ${formatadorMoeda.format(Number(pedidoCriado.total))}.`,
      })
      return true
    } catch (erro: unknown) {
      setMensagem({ tipo: 'erro', texto: mensagemDoErro(erro) })
      return false
    } finally {
      setCriandoPedido(false)
    }
  }

  async function consultarPedidoPorId(pedidoId: number) {
    setConsultandoPedido(true)
    setPedidoConsultado(null)
    setMensagem(null)

    try {
      const pedido = await buscarPedido(pedidoId)
      setPedidoConsultado(pedido)
      setMensagem({
        tipo: 'sucesso',
        texto: `Pedido #${pedido.id} localizado.`,
      })
    } catch (erro: unknown) {
      const texto =
        erro instanceof ErroApi && erro.status === 404
          ? 'Pedido não encontrado.'
          : mensagemDoErro(erro)
      setMensagem({ tipo: 'erro', texto })
    } finally {
      setConsultandoPedido(false)
    }
  }

  async function atualizarStatusDoPedido(
    pedidoId: number,
    status: StatusPedido,
  ) {
    if (atualizacoesAtivas.current.has(pedidoId)) {
      return
    }

    atualizacoesAtivas.current.add(pedidoId)
    setPedidosEmAtualizacao(new Set(atualizacoesAtivas.current))
    setMensagem(null)

    try {
      const pedidoAtualizado = await atualizarStatus(pedidoId, { status })
      setPedidos((atuais) => substituirPedido(atuais, pedidoAtualizado))
      setErroPedidos(null)
      setPedidoConsultado((atual) =>
        atual?.id === pedidoAtualizado.id ? pedidoAtualizado : atual,
      )
      setMensagem({
        tipo: 'sucesso',
        texto: `Pedido #${pedidoAtualizado.id} atualizado para ${pedidoAtualizado.status.replace('_', ' ').toLowerCase()}.`,
      })
    } catch (erro: unknown) {
      const texto = mensagemDoErro(erro)
      setMensagem({ tipo: 'erro', texto })

      try {
        const pedidosSincronizados = await listarPedidos()
        setPedidos(pedidosSincronizados)
        setErroPedidos(null)
        setPedidoConsultado((atual) =>
          atual
            ? (pedidosSincronizados.find((pedido) => pedido.id === atual.id) ??
              atual)
            : null,
        )
      } catch (erroSincronizacao: unknown) {
        setMensagem({
          tipo: 'erro',
          texto: `${texto} Também não foi possível sincronizar a lista: ${mensagemDoErro(erroSincronizacao)}`,
        })
      }
    } finally {
      atualizacoesAtivas.current.delete(pedidoId)
      setPedidosEmAtualizacao(new Set(atualizacoesAtivas.current))
    }
  }

  return (
    <main className="app-shell">
      <header className="page-header">
        <p className="eyebrow">Atendimento e cozinha</p>
        <h1>Pedidos da Lanchonete</h1>
        <p className="page-description">
          Registre os pedidos das mesas e acompanhe o preparo em um só lugar.
        </p>
      </header>

      <div
        className="feedback-region"
        aria-live="polite"
        aria-atomic="true"
      >
        {mensagem && (
          <p
            className={`notification notification-${mensagem.tipo}`}
            role={mensagem.tipo === 'erro' ? 'alert' : 'status'}
          >
            {mensagem.texto}
          </p>
        )}
      </div>

      <div className="workspace-grid">
        <FormularioPedido
          cardapio={cardapio}
          carregandoCardapio={carregandoCardapio}
          criandoPedido={criandoPedido}
          erroCardapio={erroCardapio}
          onCriarPedido={criarNovoPedido}
        />

        <div className="orders-column">
          <ConsultaPedido
            consultandoPedido={consultandoPedido}
            onConsultarPedido={consultarPedidoPorId}
          />

          {pedidoConsultado && (
            <section
              className="lookup-result"
              aria-labelledby="resultado-consulta-titulo"
            >
              <div className="result-heading">
                <p className="section-kicker">Resultado da consulta</p>
                <h2 id="resultado-consulta-titulo">Pedido localizado</h2>
              </div>
              <CartaoPedido
                pedido={pedidoConsultado}
                atualizando={pedidosEmAtualizacao.has(pedidoConsultado.id)}
                onAtualizarStatus={atualizarStatusDoPedido}
              />
            </section>
          )}

          <section className="panel" aria-labelledby="pedidos-titulo">
            <div className="section-heading">
              <div>
                <p className="section-kicker">Acompanhamento</p>
                <h2 id="pedidos-titulo">Pedidos</h2>
              </div>
              <span
                className="orders-count"
                aria-label={`${pedidos.length} pedidos`}
              >
                {pedidos.length}
              </span>
            </div>

            <ListaPedidos
              pedidos={pedidos}
              carregando={carregandoPedidos}
              erro={erroPedidos}
              pedidosEmAtualizacao={pedidosEmAtualizacao}
              onAtualizarStatus={atualizarStatusDoPedido}
            />
          </section>
        </div>
      </div>
    </main>
  )
}

export default App
