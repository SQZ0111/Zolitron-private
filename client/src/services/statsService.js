const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

async function parseResponse(response, fallbackMessage) {
  if (response.ok) {
    return response.json()
  }

  let message = fallbackMessage
  try {
    const error = await response.json()
    message = error.detail || message
  } catch {
  }
  throw new Error(message)
}

export async function fetchStats() {
  const response = await fetch(`${API_BASE_URL}/api/stats`)
  return parseResponse(response, `Could not load stats: ${response.status}`)
}
