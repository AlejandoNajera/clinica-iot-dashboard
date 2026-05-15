/**
 * Vista principal del dashboard.
 * Muestra KPIs del inventario, alertas próximas y tabla resumida de equipos.
 */

import { useState, useEffect } from 'react'
import { api } from '../api'
import EstadoBadge from './EstadoBadge'

export default function Dashboard() {
  const [equipos,  setEquipos]  = useState([])
  const [alertas,  setAlertas]  = useState([])
  const [iotStats, setIotStats] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    Promise.all([api.getEquipos(), api.getAlertas(15), api.getIoTStats()])
      .then(([eq, al, iot]) => { setEquipos(eq); setAlertas(al); setIotStats(iot) })
      .catch(console.error)
      .finally(() => setCargando(false))
  }, [])

  // Calcular KPIs
  const total       = equipos.length
  const operativos  = equipos.filter(e => e.estado === 'operativo').length
  const enMant      = equipos.filter(e => e.estado === 'en_mantenimiento').length
  const fuera       = equipos.filter(e => e.estado === 'fuera_de_servicio').length

  if (cargando) return <Loader />

  return (
    <div className="p-8 space-y-8">
      {/* Encabezado */}
      <div className="anim-1">
        <p className="text-xs tracking-widest uppercase mb-1" style={{ color: '#34D399' }}>
          Panel de Control
        </p>
        <h1
          className="text-3xl font-display font-bold"
          style={{ fontFamily: 'Syne, sans-serif', color: '#E2E8F0' }}
        >
          Dashboard General
        </h1>
        <p className="text-sm mt-1" style={{ color: '#64748B' }}>
          {new Date().toLocaleDateString('es-PE', { weekday:'long', year:'numeric', month:'long', day:'numeric' })}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Total Equipos"     value={total}      accent="#E2E8F0" delay="anim-2" icon="⊞" />
        <KpiCard label="Operativos"        value={operativos} accent="#34D399" delay="anim-3" icon="✓" />
        <KpiCard label="En Mantenimiento"  value={enMant}     accent="#FBBF24" delay="anim-4" icon="⚙" />
        <KpiCard label="Fuera de Servicio" value={fuera}      accent="#F87171" delay="anim-5" icon="✕" />
      </div>

      {/* IoT Stats */}
      {iotStats && (
        <div className="anim-4 card p-5">
          <p className="text-xs tracking-widest uppercase mb-4" style={{ color: '#34D399' }}>
            ⟁ Lecturas IoT — Últimas 24 horas ({iotStats.total_lecturas} muestras)
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <IoTStat label="Temp. Promedio" value={`${iotStats.temperatura.promedio}°C`} />
            <IoTStat label="Temp. Máxima"   value={`${iotStats.temperatura.maxima}°C`}   warn={iotStats.temperatura.maxima > 28} />
            <IoTStat label="Hum. Promedio"  value={`${iotStats.humedad.promedio}%`} />
            <IoTStat label="Hum. Máxima"    value={`${iotStats.humedad.maxima}%`}         warn={iotStats.humedad.maxima > 70} />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tabla de equipos */}
        <div className="lg:col-span-2 anim-5 card overflow-hidden">
          <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: 'rgba(52,211,153,0.1)' }}>
            <p className="text-sm font-display font-semibold" style={{ fontFamily: 'Syne,sans-serif', color:'#E2E8F0' }}>
              Inventario de Equipos
            </p>
            <span className="text-xs" style={{ color: '#64748B' }}>{total} registros</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(52,211,153,0.08)', color: '#64748B' }}>
                  {['Código', 'Equipo', 'Área', 'Estado', 'Próx. Mant.'].map(h => (
                    <th key={h} className="px-4 py-3 text-left tracking-wider uppercase text-xs">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {equipos.slice(0, 8).map((eq, i) => (
                  <tr
                    key={eq.id}
                    className="transition-colors"
                    style={{
                      borderBottom: '1px solid rgba(52,211,153,0.05)',
                      animationDelay: `${i * 0.05}s`,
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'rgba(52,211,153,0.03)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                  >
                    <td className="px-4 py-3 font-mono" style={{ color: '#34D399' }}>{eq.codigo_patrimonial}</td>
                    <td className="px-4 py-3" style={{ color: '#E2E8F0' }}>{eq.nombre}</td>
                    <td className="px-4 py-3" style={{ color: '#94A3B8' }}>{eq.area?.nombre ?? '—'}</td>
                    <td className="px-4 py-3"><EstadoBadge estado={eq.estado} /></td>
                    <td className="px-4 py-3" style={{ color: '#64748B' }}>
                      {eq.proximo_mantenimiento ?? <span style={{ color: '#334155' }}>Sin fecha</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Panel de alertas */}
        <div className="anim-6 card overflow-hidden">
          <div className="px-5 py-4 border-b flex items-center gap-2" style={{ borderColor: 'rgba(52,211,153,0.1)' }}>
            <span style={{ color: '#FBBF24' }}>◈</span>
            <p className="text-sm font-display font-semibold" style={{ fontFamily: 'Syne,sans-serif', color:'#E2E8F0' }}>
              Alertas (15 días)
            </p>
            {alertas.length > 0 && (
              <span className="ml-auto text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(251,191,36,0.15)', color: '#FBBF24' }}>
                {alertas.length}
              </span>
            )}
          </div>
          <div className="divide-y" style={{ borderColor: 'rgba(52,211,153,0.05)' }}>
            {alertas.length === 0 ? (
              <p className="px-5 py-8 text-center text-xs" style={{ color: '#334155' }}>
                Sin mantenimientos próximos ✓
              </p>
            ) : (
              alertas.map(al => (
                <AlertaRow key={al.id} alerta={al} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// --- Sub-componentes del Dashboard ---

function KpiCard({ label, value, accent, delay, icon }) {
  return (
    <div className={`card p-5 ${delay}`}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs tracking-wider uppercase" style={{ color: '#64748B' }}>{label}</span>
        <span className="text-lg" style={{ color: accent, opacity: 0.6 }}>{icon}</span>
      </div>
      <p className="text-4xl font-display font-bold" style={{ fontFamily: 'Syne,sans-serif', color: accent }}>
        {value}
      </p>
    </div>
  )
}

function IoTStat({ label, value, warn }) {
  return (
    <div className="rounded-lg p-3" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(52,211,153,0.08)' }}>
      <p className="text-xs mb-1" style={{ color: '#64748B' }}>{label}</p>
      <p className="text-xl font-mono font-semibold" style={{ color: warn ? '#FBBF24' : '#34D399' }}>
        {value}
        {warn && <span className="text-xs ml-1">⚠</span>}
      </p>
    </div>
  )
}

function AlertaRow({ alerta }) {
  const urgente = alerta.dias_restantes <= 3
  return (
    <div className="px-5 py-3">
      <div className="flex items-center justify-between mb-0.5">
        <p className="text-xs font-semibold truncate" style={{ color: '#CBD5E1', maxWidth: '65%' }}>
          {alerta.nombre}
        </p>
        <span
          className="text-xs font-mono px-2 py-0.5 rounded"
          style={{
            background: urgente ? 'rgba(248,113,113,0.15)' : 'rgba(251,191,36,0.12)',
            color:      urgente ? '#F87171' : '#FBBF24',
          }}
        >
          {alerta.dias_restantes}d
        </span>
      </div>
      <p className="text-xs" style={{ color: '#475569' }}>{alerta.area?.nombre}</p>
    </div>
  )
}

function Loader() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center space-y-3">
        <div className="text-3xl" style={{ color: '#34D399', animation: 'pulse 1.5s infinite' }}>✚</div>
        <p className="text-xs tracking-widest" style={{ color: '#475569' }}>CARGANDO DATOS…</p>
      </div>
    </div>
  )
}