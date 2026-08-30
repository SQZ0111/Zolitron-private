// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Zolitron
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

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
