<script setup>
import { onBeforeUnmount, watch } from "vue"
import { Marker, Popup } from "maplibre-gl"

import {
  coveragePercent,
  isVisibleTrashMarker,
  markerDisposition,
  resolveBackendImageUrl,
} from "../../services/mapService"

const DISPOSITION_COLORS = {
  collect: "#d32f2f",
  watch: "#f9a825",
}

const COLLECT_BASE_SIZE = 14
const COLLECT_COVERAGE_SIZE = 40
const COLLECT_MAX_SIZE = 34
const WATCH_SIZE = 10

const props = defineProps({
  map: {
    type: Object,
    default: null,
  },
  classifications: {
    type: Array,
    default: () => [],
  },
})

let renderedMarkers = []

function clearMarkers() {
  renderedMarkers.forEach((marker) => marker.remove())
  renderedMarkers = []
}

function detectionCount(classification) {
  const garbage = classification.garbage_count
  const litter = classification.litter_count
  if (garbage != null || litter != null) {
    return (garbage || 0) + (litter || 0)
  }
  return classification.detections?.length || 0
}

function detectionBoxStyles(classification) {
  const imageWidth = Number(classification.image_width)
  const imageHeight = Number(classification.image_height)
  if (!imageWidth || !imageHeight) {
    return []
  }

  return (classification.detections || [])
    .filter(
      (detection) =>
        detection.bbox_x != null &&
        detection.bbox_y != null &&
        detection.bbox_width != null &&
        detection.bbox_height != null,
    )
    .map((detection) => ({
      className: detection.class_name,
      left: ((detection.bbox_x - detection.bbox_width / 2) / imageWidth) * 100,
      top: ((detection.bbox_y - detection.bbox_height / 2) / imageHeight) * 100,
      width: (detection.bbox_width / imageWidth) * 100,
      height: (detection.bbox_height / imageHeight) * 100,
    }))
}

function createMarkerElement(disposition, coverage) {
  const element = document.createElement("div")
  element.className = `zolitron-marker zolitron-marker--${disposition}`

  if (disposition === "watch") {
    element.style.width = `${WATCH_SIZE}px`
    element.style.height = `${WATCH_SIZE}px`
    return element
  }

  const size = Math.min(
    COLLECT_BASE_SIZE + (coverage / 100) * COLLECT_COVERAGE_SIZE,
    COLLECT_MAX_SIZE,
  )
  element.style.width = `${size}px`
  element.style.height = `${size}px`
  return element
}

function createPopupContent(classification, disposition, coverage) {
  const content = document.createElement("article")
  content.className = "zolitron-marker-popup"

  const heading = document.createElement("h3")
  heading.textContent = classification.label
  content.appendChild(heading)

  const imageUrl = resolveBackendImageUrl(classification.imgUrl)
  if (imageUrl) {
    const frame = document.createElement("div")
    frame.className = "zolitron-marker-popup-frame"

    const image = document.createElement("img")
    image.src = imageUrl
    image.alt = `${classification.label} classification`
    image.loading = "lazy"
    image.addEventListener("error", () => frame.remove())
    frame.appendChild(image)

    for (const box of detectionBoxStyles(classification)) {
      const outline = document.createElement("span")
      outline.className = `zolitron-marker-bbox zolitron-marker-bbox--${box.className}`
      outline.style.left = `${box.left}%`
      outline.style.top = `${box.top}%`
      outline.style.width = `${box.width}%`
      outline.style.height = `${box.height}%`
      frame.appendChild(outline)
    }

    content.appendChild(frame)
  }

  const recommendation = document.createElement("p")
  recommendation.className = `zolitron-marker-recommendation zolitron-marker-recommendation--${disposition}`
  recommendation.textContent =
    disposition === "watch"
      ? `Monitor only — below dispatch threshold · ${coverage}% coverage`
      : `Truck dispatch recommended · ${coverage}% frame coverage · ${detectionCount(classification)} detection(s)`
  content.appendChild(recommendation)

  const confidence = Number(classification.confidence || 0)
  const details = document.createElement("p")
  details.textContent =
    `${classification.category} | ${(confidence * 100).toFixed(1)}% confidence`
  content.appendChild(details)

  const status = document.createElement("p")
  status.textContent = `${classification.status} | ${classification.city}, ${classification.country}`
  content.appendChild(status)

  return content
}

function renderMarkers() {
  clearMarkers()
  if (!props.map) return

  for (const classification of props.classifications) {
    if (!isVisibleTrashMarker(classification)) {
      continue
    }

    const latitude = Number(classification.latitude)
    const longitude = Number(classification.longitude)
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      continue
    }

    const disposition = markerDisposition(classification)
    if (!DISPOSITION_COLORS[disposition]) {
      continue
    }
    const coverage = coveragePercent(classification)

    const popup = new Popup({ offset: 25, maxWidth: "290px" }).setDOMContent(
      createPopupContent(classification, disposition, coverage),
    )
    renderedMarkers.push(
      new Marker({ element: createMarkerElement(disposition, coverage) })
        .setLngLat([longitude, latitude])
        .setPopup(popup)
        .addTo(props.map),
    )
  }
}

watch(
  () => [props.map, props.classifications],
  renderMarkers,
  { immediate: true },
)

onBeforeUnmount(clearMarkers)
</script>

<template>
  <span class="classification-markers-sr-only">
    Classification marker layer
  </span>
</template>

<style>
.zolitron-marker {
  box-sizing: border-box;
  border-radius: 50%;
  cursor: pointer;
}

.zolitron-marker--collect {
  background: #d32f2f;
  border: 2px solid rgba(255, 255, 255, 0.85);
  box-shadow: 0 0 10px rgba(211, 47, 47, 0.65);
}

.zolitron-marker--watch {
  background: transparent;
  border: 2px solid #f9a825;
  box-shadow: 0 0 6px rgba(249, 168, 37, 0.5);
}

.zolitron-marker-popup {
  display: grid;
  gap: 8px;
  min-width: 220px;
}

.zolitron-marker-popup h3 {
  color: #0d47a1;
  font-size: 1rem;
  text-transform: capitalize;
}

.zolitron-marker-popup-frame {
  position: relative;
  line-height: 0;
}

.zolitron-marker-popup img {
  width: 100%;
  height: auto;
  border-radius: 7px;
}

.zolitron-marker-bbox {
  position: absolute;
  border: 2px solid #d32f2f;
  border-radius: 2px;
  pointer-events: none;
}

.zolitron-marker-bbox--litter {
  border-color: #f9a825;
}

.zolitron-marker-popup p {
  margin: 0;
  color: #364152;
  font-size: 0.78rem;
}

.zolitron-marker-recommendation {
  font-weight: 600;
}

.zolitron-marker-recommendation--collect {
  color: #d32f2f;
}

.zolitron-marker-recommendation--watch {
  color: #a97400;
}

.classification-markers-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}
</style>
