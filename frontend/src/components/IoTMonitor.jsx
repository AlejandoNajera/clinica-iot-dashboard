/**
 * Vista de monitoreo IoT en tiempo real.
 * Muestra las últimas lecturas de cada sensor y estadísticas agregadas.
 * Se auto-refresca cada 10 segundos.
 */

import { useState, useEffect, useRef } from 'react'
import { api } from '../api'

const UMBRAL_TEMP_WARN = 25
const UMBRAL_TEMP_CRIT = 30
const UMBRAL_HUM_WARN  = 70
const UMBRAL_HUM_CRIT  = 80

export default function IoTMonitor() {
  const [lecturas,  setLecturas]  = useState([])
  const [stats,     setStats]     = useState(null)
  const [cargando,  setCargando]  = useState(true)
  const [lastUpdate,setLastUpdate]= useState(null)
  const [tick,      setTick]      = useState(0)
  const intervalRef = useRef(null)

  const cargar = async () => {
    try {
      const [lect, st] = await Promise.all([api.getUltimasLecturas(), api.getIoTStats()])
      setLecturas(lect)
      setStats(st)
      setLastUpdate(new Date())
    } catch(e) {
      console.error(e)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
    // Refresco automático cada 10 segundos
    intervalRef.current = setInterval(() => {
      cargar()
      setTick(t => t + 1)
    }, 10000)
    return () => clearInterval(intervalRef.current)
  }, [])

  const tempColor = (t) =>
    t > UMBRAL_TEMP_CRIT ? '#F87171' : t > UMBRAL_TEMP_WARN ? '#FBBF24' : '#34D399'

  const humColor  = (h) =>
    h > UMBRAL_HUM_CRIT  ? '#F87171' : h > UMBRAL_HUM_WARN  ? '#FBBF24' : '#34D399'

  return (
    <div className="p-8">
      {/* Encabezado */}
      <div className="flex items-end justify-between mb-8 anim-1">
        <div>
          <p className="text-xs tracking-widest uppercase mb-1" style={{ color: '#34D399' }}>
            ⟁ Telemetría en Vivo
          </p>
          <h1 className="text-3xl font-display font-bold" style={{ fontFamily: 'Syne,sans-serif', color:'#E2E8F0' }}>
            Monitor IoT
          </h1>
        </div>
        <div className="text-right">
          <div className="flex items-center gap-2 justify-end mb-1">
            <span className="w-2 h-2 rounded-full" style={{ background: '#34D399', boxShadow: '0 0 6px #34D399', animation: 'pulse 2s infinite' }} />
            <span className="text-xs" style={{ color: '#34D399' }}>En vivo · refresca c/10s</span>
          </div>
          {lastUpdate && (
            <p className="text-xs" style={{ color: '#334155' }}>
              Actualizado: {lastUpdate.toLocaleTimeString('es-PE')}
            </p>
          )}
        </div>
      </div>

      {/* Stats globales */}
      {stats && (
        <div className="card p-5 mb-6 anim-2">
          <p className="text-xs tracking-widest uppercase mb-4" style={{ color: '#64748B' }}>
            Estadísticas globales — últimas 24h ({stats.total_lecturas} muestras)
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatGlobal label="Temp. Prom."  value={`${stats.temperatura.promedio}°C`} color={tempColor(stats.temperatura.promedio)} />
            <StatGlobal label="Temp. Máx."   value={`${stats.temperatura.maxima}°C`}   color={tempColor(stats.temperatura.maxima)} />
            <StatGlobal label="Hum. Prom."   value={`${stats.humedad.promedio}%`}       color={humColor(stats.humedad.promedio)} />
            <StatGlobal label="Hum. Máx."    value={`${stats.humedad.maxima}%`}         color={humColor(stats.humedad.maxima)} />
          </div>
        </div>
      )}

      {/* Leyenda */}
      <div className="flex items-center gap-5 mb-5 anim-2 text-xs">
        <span style={{ color: '#64748B' }}>Umbrales:</span>
        <LeyendaItem color="#34D399" label="Normal" />
        <LeyendaItem color="#FBBF24" label="Aviso (Temp>25° / Hum>70%)" />
        <LeyendaItem color="#F87171" label="Crítico (Temp>30° / Hum>80%)" />
      </div>

      {/* Grid de sensores */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 anim-3">
        {cargando ? (
          Array(3).fill(0).map((_, i) => <SensorSkeleton key={i} />)
        ) : lecturas.length === 0 ? (
          <div className="col-span-3 card p-12 text-center">
            <p className="text-3xl mb-3" style={{ color: '#334155' }}>⟁</p>
            <p className="text-sm" style={{ color: '#475569' }}>Sin lecturas IoT registradas</p>
            <p className="text-xs mt-2" style={{ color: '#334155' }}>Ejecuta el simulador ESP32 para ver datos aquí</p>
          </div>
        ) : lecturas.map((lect, i) => (
          <SensorCard
            key={lect.id}
            lectura={lect}
            delay={i * 0.08}
            tempColor={tempColor}
            humColor={humColor}
          />
        ))}
      </div>
    </div>
  )
}

// --- Sub-componentes ---

function SensorCard({ lectura, delay, tempColor, humColor }) {
  const tc = tempColor(lectura.temperatura)
  const hc = humColor(lectura.humedad)
  const esCritico = tc === '#F87171' || hc === '#F87171'

  const ts = new Date(lectura.timestamp + 'Z')
  const tiempoStr = ts.toLocaleTimeString('es-PE')

  return (
    <div
      className="card p-5"
      style={{
        animation: `slideUp 0.4s ease ${delay}s both`,
        borderColor: esCritico ? 'rgba(248,113,113,0.3)' : undefined,
        boxShadow:   esCritico ? '0 0 20px rgba(248,113,113,0.08)' : undefined,
      }}
    >
      {/* Header del sensor */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-xs" style={{ color: '#64748B' }}>
            {lectura.equipo_id ? `Equipo #${lectura.equipo_id}` : `Área #${lectura.area_id}`}
          </p>
          <p className="font-mono text-xs mt-0.5" style={{ color: '#475569' }}>
            Sensor ID: {lectura.id}
          </p>
        </div>
        {esCritico && (
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{ background: 'rgba(248,113,113,0.15)', color: '#F87171', animation: 'pulse 1.5s infinite' }}
          >
            ⚠ Alerta
          </span>
        )}
      </div>

      {/* Lecturas */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <LecturaGauge
          label="Temperatura"
          value={lectura.temperatura}
          unit="°C"
          color={tc}
          min={0} max={40}
        />
        <LecturaGauge
          label="Humedad"
          value={lectura.humedad}
          unit="%"
          color={hc}
          min={0} max={100}
        />
      </div>

      {/* Timestamp */}
      <p className="text-xs text-right" style={{ color: '#334155' }}>
        Última lectura: {tiempoStr}
      </p>
    </div>
  )
}

function LecturaGauge({ label, value, unit, color, min, max }) {
  const pct = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100))

  return (
    <div className="rounded-lg p-3" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
      <p className="text-xs mb-2" style={{ color: '#475569' }}>{label}</p>
      <p className="text-2xl font-mono font-semibold mb-2" style={{ color }}>
        {value.toFixed(1)}<span className="text-sm">{unit}</span>
      </p>
      {/* Mini barra de progreso */}
      <div className="h-1 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
        <div
          className="h-1 rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
    </div>
  )
}

function StatGlobal({ label, value, color }) {
  return (
    <div className="rounded-lg p-3" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(52,211,153,0.07)' }}>
      <p className="text-xs mb-1" style={{ color: '#475569' }}>{label}</p>
      <p className="text-xl font-mono font-bold" style={{ color }}>{value}</p>
    </div>
  )
}

function LeyendaItem({ color, label }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="w-2 h-2 rounded-full" style={{ background: color }} />
      <span style={{ color: '#64748B' }}>{label}</span>
    </div>
  )
}

function SensorSkeleton() {
  return (
    <div className="card p-5 space-y-4">
      {[60, 100, 80].map((w, i) => (
        <div key={i} className="h-3 rounded" style={{ width: `${w}%`, background: 'rgba(255,255,255,0.04)' }} />
      ))}
    </div>
  )
}