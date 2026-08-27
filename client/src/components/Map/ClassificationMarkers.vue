<script setup>
import { onBeforeUnmount, watch } from "vue"
import { Marker, Popup } from "maplibre-gl"

import {
  isVisibleTrashMarker,
  resolveBackendImageUrl,
} from "../../services/mapService"

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

function createPopupContent(classification) {
  const content = document.createElement("article")
  content.className = "zolitron-marker-popup"

  const heading = document.createElement("h3")
  heading.textContent = classification.label
  content.appendChild(heading)

  const imageUrl = resolveBackendImageUrl(classification.imgUrl)
  if (imageUrl) {
    const image = document.createElement("img")
    image.src = imageUrl
    image.alt = `${classification.label} classification`
    image.loading = "lazy"
    image.addEventListener("error", () => image.remove())
    content.appendChild(image)
  }

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

    const popup = new Popup({ offset: 25, maxWidth: "290px" }).setDOMContent(
      createPopupContent(classification),
    )
    renderedMarkers.push(
      new Marker({ color: "#990066" })
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

.zolitron-marker-popup img {
  width: 100%;
  max-height: 150px;
  border-radius: 7px;
  object-fit: cover;
}

.zolitron-marker-popup p {
  margin: 0;
  color: #364152;
  font-size: 0.78rem;
}

.classification-markers-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}
</style>
