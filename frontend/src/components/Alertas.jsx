/**
 * Vista de alertas de mantenimiento próximo.
 * Permite configurar la ventana de días y ver detalles de cada equipo.
 */

import { useState, useEffect } from 'react'
import { api } from '../api'
import EstadoBadge from './EstadoBadge'

export default function Alertas() {
  const [alertas,  setAlertas]  = useState([])
  const [dias,     setDias]     = useState(15)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    setCargando(true)
    api.getAlertas(dias)
      .then(setAlertas)
      .catch(console.error)
      .finally(() => setCargando(false))
  }, [dias])

  return (
    <div className="p-8">
      {/* Encabezado */}
      <div className="flex items-end justify-between mb-8 anim-1">
        <div>
          <p className="text-xs tracking-widest uppercase mb-1" style={{ color: '#FBBF24' }}>◈ Mantenimiento Preventivo</p>
          <h1 className="text-3xl font-display font-bold" style={{ fontFamily: 'Syne,sans-serif', color:'#E2E8F0' }}>
            Alertas Próximas
          </h1>
        </div>

        {/* Selector de ventana */}
        <div className="flex items-center gap-2">
          <span className="text-xs" style={{ color: '#64748B' }}>Ventana:</span>
          {[7, 15, 30].map(d => (
            <button
              key={d}
              onClick={() => setDias(d)}
              className="px-3 py-1.5 rounded-lg text-xs transition-all"
              style={{
                background: dias === d ? 'rgba(251,191,36,0.15)' : 'rgba(255,255,255,0.03)',
                color:      dias === d ? '#FBBF24' : '#64748B',
                border:     `1px solid ${dias === d ? 'rgba(251,191,36,0.3)' : 'rgba(255,255,255,0.05)'}`,
              }}
            >
              {d} días
            </button>
          ))}
        </div>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-3 gap-4 mb-6 anim-2">
        <ResumenCard label="Total Alertas"  value={alertas.length}                               color="#FBBF24" />
        <ResumenCard label="Urgentes (≤3d)" value={alertas.filter(a => a.dias_restantes <= 3).length} color="#F87171" />
        <ResumenCard label="Esta semana"    value={alertas.filter(a => a.dias_restantes <= 7).length} color="#94A3B8" />
      </div>

      {/* Lista de alertas */}
      <div className="space-y-3 anim-3">
        {cargando ? (
          <p className="text-center py-12 text-xs" style={{ color: '#334155' }}>Cargando alertas…</p>
        ) : alertas.length === 0 ? (
          <div className="card p-12 text-center">
            <p className="text-3xl mb-3">✓</p>
            <p className="text-sm" style={{ color: '#34D399' }}>Sin mantenimientos en los próximos {dias} días</p>
          </div>
        ) : alertas.map((al, i) => (
          <AlertaCard key={al.id} alerta={al} delay={i * 0.06} />
        ))}
      </div>
    </div>
  )
}

function ResumenCard({ label, value, color }) {
  return (
    <div className="card p-4">
      <p className="text-xs mb-2" style={{ color: '#64748B' }}>{label}</p>
      <p className="text-3xl font-display font-bold" style={{ fontFamily: 'Syne,sans-serif', color }}>{value}</p>
    </div>
  )
}

function AlertaCard({ alerta, delay }) {
  const urgente  = alerta.dias_restantes <= 3
  const pronto   = alerta.dias_restantes <= 7

  const colorBarra = urgente ? '#F87171' : pronto ? '#FBBF24' : '#34D399'
  const porcentaje = Math.max(5, 100 - (alerta.dias_restantes / 15) * 100)

  return (
    <div
      className="card p-5 flex items-center gap-5"
      style={{ animation: `slideUp 0.4s ease ${delay}s both` }}
    >
      {/* Indicador de urgencia */}
      <div
        className="w-1 self-stretch rounded-full flex-shrink-0"
        style={{ background: colorBarra, minHeight: 40 }}
      />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-3 mb-1">
          <p className="font-display font-semibold truncate" style={{ fontFamily: 'Syne,sans-serif', color: '#E2E8F0' }}>
            {alerta.nombre}
          </p>
          <EstadoBadge estado={alerta.estado} />
        </div>
        <div className="flex gap-4 text-xs" style={{ color: '#64748B' }}>
          <span>📍 {alerta.area?.nombre}</span>
          <span>🏷 {alerta.codigo_patrimonial}</span>
          <span>📅 {alerta.proximo_mantenimiento}</span>
        </div>

        {/* Barra de progreso de urgencia */}
        <div className="mt-3 h-1 rounded-full" style={{ background: 'rgba(255,255,255,0.05)' }}>
          <div
            className="h-1 rounded-full transition-all duration-700"
            style={{ width: `${porcentaje}%`, background: colorBarra }}
          />
        </div>
      </div>

      {/* Días restantes */}
      <div className="text-right flex-shrink-0">
        <p
          className="text-2xl font-display font-bold"
          style={{ fontFamily: 'Syne,sans-serif', color: colorBarra }}
        >
          {alerta.dias_restantes}
        </p>
        <p className="text-xs" style={{ color: '#475569' }}>días</p>
      </div>
    </div>
  )
}