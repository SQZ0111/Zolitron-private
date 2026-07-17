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
    // Preserve the fallback when the server does not return JSON.
  }
  throw new Error(message)
}

export async function uploadImage(file, metadata) {
  const body = new FormData()
  body.append("file", file)
  body.append("city", metadata.city.trim())
  body.append("country", metadata.country.trim())

  if (metadata.latitude !== "" && metadata.latitude != null) {
    body.append("latitude", metadata.latitude)
  }
  if (metadata.longitude !== "" && metadata.longitude != null) {
    body.append("longitude", metadata.longitude)
  }

  const response = await fetch(`${API_BASE_URL}/api/images/upload`, {
    method: "POST",
    body,
  })
  return parseResponse(response, `Image upload failed: ${response.status}`)
}

export async function importMapillaryCity(city, country = "Germany", limit = 5) {
  const response = await fetch(`${API_BASE_URL}/api/images/import/mapillary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ city, country, limit }),
  })
  return parseResponse(response, `Mapillary import failed: ${response.status}`)
}
