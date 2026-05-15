/**
 * Badge de estado para equipos clínicos.
 * Muestra un punto de color + etiqueta según el estado del equipo.
 */

const CONFIG = {
  operativo:           { label: 'Operativo',        color: '#34D399', bg: 'rgba(52,211,153,0.12)'  },
  en_mantenimiento:    { label: 'Mantenimiento',    color: '#FBBF24', bg: 'rgba(251,191,36,0.12)'  },
  fuera_de_servicio:   { label: 'Fuera de Servicio',color: '#F87171', bg: 'rgba(248,113,113,0.12)' },
  en_revision:         { label: 'En Revisión',      color: '#94A3B8', bg: 'rgba(148,163,184,0.12)' },
}

export default function EstadoBadge({ estado }) {
  const cfg = CONFIG[estado] ?? { label: estado, color: '#64748B', bg: 'rgba(100,116,139,0.12)' }

  return (
    <span
      className="badge"
      style={{ background: cfg.bg, color: cfg.color }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ background: cfg.color, display: 'inline-block', boxShadow: `0 0 4px ${cfg.color}` }}
      />
      {cfg.label}
    </span>
  )
}