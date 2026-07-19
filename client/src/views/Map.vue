<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue"
import { Map } from "maplibre-gl"
import "maplibre-gl/dist/maplibre-gl.css"

import ClassificationMarkers from "../components/Map/ClassificationMarkers.vue"
import MapLegend from "../components/Map/MapLegend.vue"
import MapSearch from "../components/Map/MapSearch.vue"
import { imagePipelineState } from "../services/imagePipelineState"
import { fetchClassificationMarkers } from "../services/mapService"

const INITIAL_LOCATION = {
  city: "Bochum",
  longitude: 7.216,
  latitude: 51.481,
  zoom: 13,
}

const mapContainer = ref(null)
const map = ref(null)
const classifications = ref([])
const currentCity = ref(INITIAL_LOCATION.city)
const loadingMarkers = ref(false)
const markerError = ref("")

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

function handleLocationFound(location) {
  map.value?.flyTo({
    center: [location.longitude, location.latitude],
    zoom: 13,
  })
  loadMarkers(location.city)
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
})

watch(imagePipelineState.processedCount, () => {
  if (currentCity.value) {
    loadMarkers(currentCity.value)
  }
})

onBeforeUnmount(() => {
  map.value?.remove()
  map.value = null
})
</script>

<template>
  <div class="map-page">
    <div ref="mapContainer" class="map" />

    <MapSearch @location-found="handleLocationFound" />
    <MapLegend />
    <ClassificationMarkers
      :map="map"
      :classifications="classifications"
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
  width: 100%;
  height: 100%;
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
