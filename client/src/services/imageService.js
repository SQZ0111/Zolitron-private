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

export async function listImages() {
  const response = await fetch(`${API_BASE_URL}/api/images`)
  return parseResponse(response, `Could not load images: ${response.status}`)
}

export async function listClassifications() {
  const response = await fetch(`${API_BASE_URL}/api/classifications`)
  return parseResponse(response, `Could not load classifications: ${response.status}`)
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

export async function startCameraFrameBatchJob(size = 5, cursor = null) {
  const body = { size }
  if (cursor) {
    body.cursor = cursor
  }

  const response = await fetch(
    `${API_BASE_URL}/api/images/import/camera-frames/jobs`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  )
  return parseResponse(response, `Could not start image processing: ${response.status}`)
}

export async function getCameraFrameBatchJob(jobId) {
  const response = await fetch(
    `${API_BASE_URL}/api/images/import/camera-frames/jobs/${encodeURIComponent(jobId)}`,
  )
  return parseResponse(response, `Could not read image-processing status: ${response.status}`)
}

export async function cancelCameraFrameBatchJob(jobId) {
  const response = await fetch(
    `${API_BASE_URL}/api/images/import/camera-frames/jobs/${encodeURIComponent(jobId)}/cancel`,
    { method: "POST" },
  )
  return parseResponse(response, `Could not stop image processing: ${response.status}`)
}
