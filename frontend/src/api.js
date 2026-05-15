/**
 * Capa de acceso a la API backend.
 * Centraliza todas las llamadas HTTP para que los componentes
 * no dependan de fetch directamente.
 */

const BASE = '/api/v1'

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`)
  return res.json()
}

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`)
  return res.json()
}

async function put(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method:  'PUT',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`PUT ${path} → ${res.status}`)
  return res.json()
}

async function del(path) {
  const res = await fetch(`${BASE}${path}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`DELETE ${path} → ${res.status}`)
  return res.status === 204 ? null : res.json()
}

export const api = {
  // Equipos
  getEquipos:   ()       => get('/equipos'),
  createEquipo: (data)   => post('/equipos', data),
  updateEquipo: (id, d)  => put(`/equipos/${id}`, d),
  deleteEquipo: (id)     => del(`/equipos/${id}`),

  // Áreas
  getAreas:     ()       => get('/areas'),
  createArea:   (data)   => post('/areas', data),

  // Mantenimientos
  createMantenimiento: (data) => post('/mantenimientos', data),

  // Alertas
  getAlertas:   (dias=15) => get(`/alertas?dias=${dias}`),

  // IoT
  getIoTStats:  ()       => get('/iot/stats'),
  getUltimasLecturas: () => get('/iot/lecturas/ultimas'),
}