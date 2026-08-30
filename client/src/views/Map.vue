<script setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from "vue"
import { Map } from "maplibre-gl"
import "maplibre-gl/dist/maplibre-gl.css"

import ClassificationMarkers from "../components/Map/ClassificationMarkers.vue"
import MapLegend from "../components/Map/MapLegend.vue"
import MapSearch from "../components/Map/MapSearch.vue"
import { imagePipelineState } from "../services/imagePipelineState"
import { listClassifications } from "../services/imageService"
import {
  fetchClassificationMarkers,
  markerDisposition,
} from "../services/mapService"

const INITIAL_LOCATION = {
  city: "Bochum",
  longitude: 7.216,
  latitude: 51.481,
  zoom: 13,
}

const mapContainer = ref(null)
const map = shallowRef(null)
const classifications = ref([])
const currentCity = ref(INITIAL_LOCATION.city)
const selectedLocation = ref(INITIAL_LOCATION)
const cityDialogOpen = ref(false)
const loadingMarkers = ref(false)
const markerError = ref("")
const availableCities = ref([])
const showLitter = ref(true)

const visibleClassifications = computed(() => {
  if (showLitter.value) {
    return classifications.value
  }
  return classifications.value.filter(
    (item) => markerDisposition(item) !== "watch",
  )
})

async function loadMarkers(city) {
  loadingMarkers.value = true
  markerError.value = ""

  try {
    classifications.value = await fetchClassificationMarkers(city)
    currentCity.value = city
  } catch (error) {
    markerError.value = error.message
  } finally {
    loadingMarkers.value = false
  }
}

async function loadAvailableCities() {
  let items
  try {
    items = await listClassifications()
  } catch {
    return
  }

  const grouped = {}
  for (const item of items) {
    if (!item.city || item.latitude == null || item.longitude == null) {
      continue
    }
    const key = item.city.toLowerCase()
    if (!grouped[key]) {
      grouped[key] = { name: item.city, latSum: 0, lonSum: 0, count: 0 }
    }
    const entry = grouped[key]
    entry.latSum += item.latitude
    entry.lonSum += item.longitude
    entry.count += 1
  }

  availableCities.value = Object.values(grouped)
    .map((entry) => ({
      name: entry.name,
      latitude: entry.latSum / entry.count,
      longitude: entry.lonSum / entry.count,
      count: entry.count,
    }))
    .sort((a, b) => b.count - a.count)
}

function handleLocationFound(location) {
  selectedLocation.value = location
  map.value?.flyTo({
    center: [location.longitude, location.latitude],
    zoom: 13,
  })
  loadMarkers(location.city)
}

function selectCity(city) {
  selectedLocation.value = {
    city: city.name,
    longitude: city.longitude,
    latitude: city.latitude,
  }
  map.value?.flyTo({
    center: [city.longitude, city.latitude],
    zoom: 13,
  })
  loadMarkers(city.name)
}

function resetMapView() {
  map.value?.flyTo({
    center: [
      selectedLocation.value.longitude,
      selectedLocation.value.latitude,
    ],
    zoom: INITIAL_LOCATION.zoom,
  })
}

onMounted(() => {
  const apiKey = import.meta.env.VITE_MAPTILER_KEY
  map.value = new Map({
    container: mapContainer.value,
    style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${apiKey}`,
    center: [INITIAL_LOCATION.longitude, INITIAL_LOCATION.latitude],
    zoom: INITIAL_LOCATION.zoom,
  })
  loadMarkers(INITIAL_LOCATION.city)
  loadAvailableCities()
})

watch(imagePipelineState.processedCount, () => {
  if (currentCity.value) {
    loadMarkers(currentCity.value)
  }
  loadAvailableCities()
})

onBeforeUnmount(() => {
  map.value?.remove()
  map.value = null
})
</script>

<template>
  <div class="map-page">
    <div ref="mapContainer" class="map" />

    <MapSearch
      v-model="cityDialogOpen"
      :current-city="currentCity"
      @location-found="handleLocationFound"
    />
    <MapLegend
      v-model:show-litter="showLitter"
      :current-city="currentCity"
      :available-cities="availableCities"
      @change-city="cityDialogOpen = true"
      @reset-view="resetMapView"
      @select-city="selectCity"
    />
    <ClassificationMarkers
      :map="map"
      :classifications="visibleClassifications"
    />

    <v-progress-circular
      v-if="loadingMarkers"
      class="marker-loading"
      color="primary"
      indeterminate
      aria-label="Loading map markers"
    />

    <v-alert
      v-if="markerError"
      class="marker-error"
      type="error"
      density="compact"
      closable
      @click:close="markerError = ''"
    >
      {{ markerError }}
    </v-alert>
  </div>
</template>

<style scoped>
.map-page {
  position: relative;
  width: 100%;
  height: calc(100dvh - 64px);
  min-height: 520px;
  overflow: hidden;
}

.map {
  position: absolute;
  inset: 20px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow:
    0 0 0 1px rgba(66, 165, 245, 0.35),
    0 20px 50px rgba(10, 30, 60, 0.35);
}

.marker-loading {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 4;
  padding: 8px;
  border-radius: 50%;
  background: white;
  box-shadow: 0 3px 12px rgba(13, 71, 161, 0.22);
}

.marker-error {
  position: absolute;
  top: 84px;
  right: 20px;
  z-index: 4;
  width: min(380px, calc(100% - 40px));
}

@media (max-width: 600px) {
  .map-page {
    min-height: 440px;
  }

  .map {
    inset: 10px;
    border-radius: 14px;
  }

  .marker-loading {
    top: 76px;
    right: 12px;
  }

  .marker-error {
    top: 124px;
    right: 12px;
    width: calc(100% - 24px);
  }
}
</style>
