const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

export const MIN_TRASH_MARKER_CONFIDENCE = 0.6

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

export async function fetchClassificationMarkers(city) {
  const query = new URLSearchParams()
  if (city?.trim()) {
    query.set("city", city.trim())
  }
  query.set("label", "garbage")

  const response = await fetch(
    `${API_BASE_URL}/api/classifications?${query.toString()}`,
  )
  const classifications = await parseResponse(
    response,
    `Could not load map markers: ${response.status}`,
  )
  return classifications.filter(isVisibleTrashMarker)
}

export function isTrashClassification(classification) {
  return ["garbage", "litter"].includes(
    classification?.label?.trim().toLowerCase(),
  )
}

export function isVisibleTrashMarker(classification) {
  const confidence = Number(classification?.confidence)
  return (
    isTrashClassification(classification) &&
    Number.isFinite(confidence) &&
    confidence >= MIN_TRASH_MARKER_CONFIDENCE &&
    classification.status !== "low-confidence"
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
