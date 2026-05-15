import { useState } from 'react'
import Sidebar    from './components/Sidebar'
import Dashboard  from './components/Dashboard'
import Equipos    from './components/Equipos'
import Alertas    from './components/Alertas'
import IoTMonitor from './components/IoTMonitor'

/**
 * Componente raíz. Gestiona la navegación entre vistas
 * mediante estado local (sin React Router para mantener el MVP simple).
 */
export default function App() {
  const [vista, setVista] = useState('dashboard')

  const vistas = {
    dashboard:  <Dashboard  />,
    equipos:    <Equipos    />,
    alertas:    <Alertas    />,
    iot:        <IoTMonitor />,
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar vistaActual={vista} onNavegar={setVista} />
      <main className="flex-1 overflow-auto">
        {vistas[vista]}
      </main>
    </div>
  )
}