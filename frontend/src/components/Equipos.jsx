/**
 * Vista completa de gestión de equipos.
 * Lista todos los equipos con filtros por estado y área,
 * y permite crear nuevos equipos mediante un formulario modal.
 */

import { useState, useEffect } from 'react'
import { api } from '../api'
import EstadoBadge from './EstadoBadge'

const ESTADOS = ['operativo','en_mantenimiento','fuera_de_servicio','en_revision']

export default function Equipos() {
  const [equipos,  setEquipos]  = useState([])
  const [areas,    setAreas]    = useState([])
  const [filtro,   setFiltro]   = useState('')
  const [modal,    setModal]    = useState(false)
  const [cargando, setCargando] = useState(true)
  const [error,    setError]    = useState(null)

  const cargar = () => {
    setCargando(true)
    Promise.all([api.getEquipos(), api.getAreas()])
      .then(([eq, ar]) => { setEquipos(eq); setAreas(ar) })
      .catch(e => setError(e.message))
      .finally(() => setCargando(false))
  }

  useEffect(() => { cargar() }, [])

  const filtrados = filtro
    ? equipos.filter(e => e.estado === filtro)
    : equipos

  return (
    <div className="p-8">
      {/* Encabezado */}
      <div className="flex items-end justify-between mb-8 anim-1">
        <div>
          <p className="text-xs tracking-widest uppercase mb-1" style={{ color: '#34D399' }}>Inventario</p>
          <h1 className="text-3xl font-display font-bold" style={{ fontFamily: 'Syne,sans-serif', color:'#E2E8F0' }}>
            Equipos Clínicos
          </h1>
        </div>
        <button
          onClick={() => setModal(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all"
          style={{ background: '#34D399', color: '#060B18' }}
          onMouseEnter={e => e.target.style.background = '#10B981'}
          onMouseLeave={e => e.target.style.background = '#34D399'}
        >
          <span>+</span> Nuevo Equipo
        </button>
      </div>

      {/* Filtros por estado */}
      <div className="flex flex-wrap gap-2 mb-6 anim-2">
        <FiltroBadge label="Todos" activo={filtro === ''} onClick={() => setFiltro('')} count={equipos.length} />
        {ESTADOS.map(est => (
          <FiltroBadge
            key={est}
            label={est.replace('_', ' ')}
            activo={filtro === est}
            onClick={() => setFiltro(est)}
            count={equipos.filter(e => e.estado === est).length}
          />
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-3 rounded-lg text-xs" style={{ background: 'rgba(248,113,113,0.1)', color: '#F87171', border: '1px solid rgba(248,113,113,0.2)' }}>
          ✕ Error al cargar: {error}
        </div>
      )}

      {/* Tabla */}
      <div className="card overflow-hidden anim-3">
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(52,211,153,0.1)', color: '#475569' }}>
                {['ID', 'Código', 'Nombre', 'Marca / Modelo', 'Área', 'Estado', 'Próx. Mantenimiento'].map(h => (
                  <th key={h} className="px-4 py-3 text-left tracking-widest uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cargando ? (
                <tr><td colSpan={7} className="px-4 py-10 text-center" style={{ color: '#334155' }}>Cargando…</td></tr>
              ) : filtrados.length === 0 ? (
                <tr><td colSpan={7} className="px-4 py-10 text-center" style={{ color: '#334155' }}>Sin registros</td></tr>
              ) : filtrados.map((eq, i) => (
                <tr
                  key={eq.id}
                  style={{ borderBottom: '1px solid rgba(52,211,153,0.05)', animationDelay: `${i*0.04}s` }}
                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(52,211,153,0.03)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td className="px-4 py-3" style={{ color: '#334155' }}>#{eq.id}</td>
                  <td className="px-4 py-3 font-mono" style={{ color: '#34D399' }}>{eq.codigo_patrimonial}</td>
                  <td className="px-4 py-3 font-semibold" style={{ color: '#CBD5E1' }}>{eq.nombre}</td>
                  <td className="px-4 py-3" style={{ color: '#64748B' }}>
                    {eq.marca ?? '—'} {eq.modelo ? `/ ${eq.modelo}` : ''}
                  </td>
                  <td className="px-4 py-3" style={{ color: '#94A3B8' }}>{eq.area?.nombre ?? '—'}</td>
                  <td className="px-4 py-3"><EstadoBadge estado={eq.estado} /></td>
                  <td className="px-4 py-3" style={{ color: '#64748B' }}>{eq.proximo_mantenimiento ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {modal && (
        <ModalEquipo
          areas={areas}
          onClose={() => setModal(false)}
          onCreado={() => { setModal(false); cargar() }}
        />
      )}
    </div>
  )
}

// --- Sub-componentes ---

function FiltroBadge({ label, activo, onClick, count }) {
  return (
    <button
      onClick={onClick}
      className="px-3 py-1.5 rounded-lg text-xs capitalize transition-all"
      style={{
        background: activo ? 'rgba(52,211,153,0.15)' : 'rgba(255,255,255,0.03)',
        color:      activo ? '#34D399' : '#64748B',
        border:     `1px solid ${activo ? 'rgba(52,211,153,0.3)' : 'rgba(255,255,255,0.05)'}`,
      }}
    >
      {label} <span style={{ opacity: 0.6 }}>({count})</span>
    </button>
  )
}

function ModalEquipo({ areas, onClose, onCreado }) {
  const [form,    setForm]    = useState({
    codigo_patrimonial: '', nombre: '', marca: '', modelo: '',
    numero_serie: '', estado: 'operativo', proximo_mantenimiento: '', area_id: '',
  })
  const [guardando, setGuardando] = useState(false)
  const [errorMsg,  setErrorMsg]  = useState(null)

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const guardar = async () => {
    if (!form.codigo_patrimonial || !form.nombre || !form.area_id) {
      setErrorMsg('Código, nombre y área son obligatorios.'); return
    }
    setGuardando(true); setErrorMsg(null)
    try {
      const payload = {
        ...form,
        area_id: parseInt(form.area_id),
        proximo_mantenimiento: form.proximo_mantenimiento || null,
      }
      await api.createEquipo(payload)
      onCreado()
    } catch(e) {
      setErrorMsg(e.message)
    } finally {
      setGuardando(false)
    }
  }

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 p-4"
      style={{ background: 'rgba(6,11,24,0.85)', backdropFilter: 'blur(4px)' }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div className="card w-full max-w-lg p-6 space-y-4" style={{ animation: 'slideUp 0.3s ease' }}>
        <div className="flex items-center justify-between">
          <h2 className="font-display font-bold text-lg" style={{ fontFamily: 'Syne,sans-serif', color: '#E2E8F0' }}>
            Nuevo Equipo
          </h2>
          <button onClick={onClose} className="text-lg" style={{ color: '#475569' }}>✕</button>
        </div>

        {errorMsg && (
          <p className="text-xs p-2 rounded" style={{ background: 'rgba(248,113,113,0.1)', color: '#F87171' }}>
            {errorMsg}
          </p>
        )}

        <div className="grid grid-cols-2 gap-3">
          <Campo label="Código Patrimonial *" name="codigo_patrimonial" value={form.codigo_patrimonial} onChange={handle} span />
          <Campo label="Nombre del Equipo *"  name="nombre"             value={form.nombre}             onChange={handle} span />
          <Campo label="Marca"                name="marca"              value={form.marca}              onChange={handle} />
          <Campo label="Modelo"               name="modelo"             value={form.modelo}             onChange={handle} />
          <Campo label="Número de Serie"      name="numero_serie"       value={form.numero_serie}       onChange={handle} />
          <Campo label="Próx. Mantenimiento"  name="proximo_mantenimiento" value={form.proximo_mantenimiento} onChange={handle} type="date" />

          {/* Estado */}
          <div>
            <label className="block text-xs mb-1" style={{ color: '#64748B' }}>Estado</label>
            <select name="estado" value={form.estado} onChange={handle} className="campo-input w-full"
              style={{ background: '#131F2E', border: '1px solid rgba(52,211,153,0.15)', color: '#CBD5E1', borderRadius: 8, padding: '8px 10px', fontSize: 12, width: '100%' }}>
              {['operativo','en_mantenimiento','fuera_de_servicio','en_revision'].map(s => (
                <option key={s} value={s}>{s.replace(/_/g,' ')}</option>
              ))}
            </select>
          </div>

          {/* Área */}
          <div>
            <label className="block text-xs mb-1" style={{ color: '#64748B' }}>Área *</label>
            <select name="area_id" value={form.area_id} onChange={handle}
              style={{ background: '#131F2E', border: '1px solid rgba(52,211,153,0.15)', color: '#CBD5E1', borderRadius: 8, padding: '8px 10px', fontSize: 12, width: '100%' }}>
              <option value="">— seleccionar —</option>
              {areas.map(a => <option key={a.id} value={a.id}>{a.nombre}</option>)}
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-xs" style={{ background: 'rgba(255,255,255,0.04)', color: '#64748B' }}>
            Cancelar
          </button>
          <button
            onClick={guardar}
            disabled={guardando}
            className="px-4 py-2 rounded-lg text-xs font-semibold"
            style={{ background: guardando ? '#059669' : '#34D399', color: '#060B18' }}
          >
            {guardando ? 'Guardando…' : 'Crear Equipo'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Campo({ label, name, value, onChange, type='text', span }) {
  return (
    <div className={span ? 'col-span-2' : ''}>
      <label className="block text-xs mb-1" style={{ color: '#64748B' }}>{label}</label>
      <input
        type={type} name={name} value={value} onChange={onChange}
        style={{
          background: '#131F2E',
          border: '1px solid rgba(52,211,153,0.15)',
          color: '#CBD5E1', borderRadius: 8,
          padding: '8px 10px', fontSize: 12, width: '100%',
          outline: 'none',
        }}
        onFocus={e  => e.target.style.borderColor = 'rgba(52,211,153,0.4)'}
        onBlur={e   => e.target.style.borderColor = 'rgba(52,211,153,0.15)'}
      />
    </div>
  )
}