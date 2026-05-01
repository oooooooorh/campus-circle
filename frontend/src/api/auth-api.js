import { API_BASE, getAuthToken } from '../config.js'

export async function register(username, password) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || '注册失败')
  return data
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || '登录失败')
  localStorage.setItem('campus_circle_token', data.access_token)
  localStorage.setItem('campus_circle_username', username)
  return data
}

export function logout() {
  localStorage.removeItem('campus_circle_token')
  localStorage.removeItem('campus_circle_username')
  localStorage.removeItem('campus_circle_avatar')
}

export async function getMe() {
  const token = getAuthToken()
  if (!token) return null
  const res = await fetch(`${API_BASE}/api/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) return null
  return await res.json()
}

