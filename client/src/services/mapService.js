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
    // Keep a stable fallback when the server does not return JSON.
  }
  throw new Error(message)
}

export async function fetchClassificationMarkers(city) {
  const query = new URLSearchParams()
  if (city?.trim()) {
    query.set("city", city.trim())
  }

  const suffix = query.size ? `?${query.toString()}` : ""
  const response = await fetch(`${API_BASE_URL}/api/classifications${suffix}`)
  return parseResponse(
    response,
    `Could not load map markers: ${response.status}`,
  )
}

export async function searchGermanLocation(query) {
  const normalizedQuery = query?.trim()
  if (!normalizedQuery) {
    throw new Error("Please enter a German city.")
  }

  const apiKey = import.meta.env.VITE_MAPTILER_KEY
  if (!apiKey) {
    throw new Error("The MapTiler key is not configured.")
  }

  const params = new URLSearchParams({
    key: apiKey,
    country: "de",
    language: "en",
    limit: "1",
  })
  const response = await fetch(
    `https://api.maptiler.com/geocoding/${encodeURIComponent(normalizedQuery)}.json?${params}`,
  )
  const data = await parseResponse(response, "Location search failed.")
  const feature = data.features?.[0]

  if (!feature?.center || feature.center.length < 2) {
    throw new Error("No matching German location was found.")
  }

  return {
    city: normalizedQuery,
    longitude: Number(feature.center[0]),
    latitude: Number(feature.center[1]),
  }
}

export function resolveBackendImageUrl(imageUrl) {
  if (!imageUrl || /^https?:\/\//i.test(imageUrl)) {
    return imageUrl
  }
  return `${API_BASE_URL}${imageUrl.startsWith("/") ? "" : "/"}${imageUrl}`
}
