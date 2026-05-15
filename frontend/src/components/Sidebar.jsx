/**
 * Barra de navegación lateral fija.
 * Muestra el logo, los enlaces de navegación y el indicador de estado del sistema.
 */

const NAV = [
  { id: 'dashboard', label: 'Dashboard',   icon: '▦' },
  { id: 'equipos',   label: 'Equipos',     icon: '⊞' },
  { id: 'alertas',   label: 'Alertas',     icon: '◈' },
  { id: 'iot',       label: 'Monitor IoT', icon: '⟁' },
]

export default function Sidebar({ vistaActual, onNavegar }) {
  return (
    <aside
      className="w-56 min-h-screen flex flex-col"
      style={{
        background: 'linear-gradient(180deg, #0B1221 0%, #060B18 100%)',
        borderRight: '1px solid rgba(52,211,153,0.1)',
      }}
    >
      {/* Logo */}
      <div className="px-6 py-7 border-b" style={{ borderColor: 'rgba(52,211,153,0.1)' }}>
        <div className="flex items-center gap-2">
          <span className="text-xl" style={{ color: '#34D399' }}>✚</span>
          <span
            className="text-lg font-display font-800 tracking-tight"
            style={{ color: '#E2E8F0', fontFamily: 'Syne, sans-serif', fontWeight: 800 }}
          >
            Med<span style={{ color: '#34D399' }}>Track</span>
          </span>
        </div>
        <p className="text-xs mt-1" style={{ color: '#64748B' }}>v1.0 MVP · HealthTech</p>
      </div>

      {/* Navegación */}
      <nav className="flex-1 px-3 py-5 space-y-1">
        {NAV.map((item) => {
          const activo = vistaActual === item.id
          return (
            <button
              key={item.id}
              onClick={() => onNavegar(item.id)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200"
              style={{
                background:  activo ? 'rgba(52,211,153,0.1)'  : 'transparent',
                color:       activo ? '#34D399'                : '#64748B',
                borderLeft:  activo ? '2px solid #34D399'      : '2px solid transparent',
                fontFamily:  'JetBrains Mono, monospace',
              }}
            >
              <span className="text-base">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>

      {/* Estado del sistema */}
      <div className="px-5 py-5 border-t" style={{ borderColor: 'rgba(52,211,153,0.1)' }}>
        <div className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full"
            style={{ background: '#34D399', boxShadow: '0 0 6px #34D399', animation: 'pulse 2s infinite' }}
          />
          <span className="text-xs" style={{ color: '#34D399' }}>Sistema en línea</span>
        </div>
      </div>
    </aside>
  )
}