<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { Map } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const mapContainer = ref(null)
let map

onMounted(() => {
  const apiKey = import.meta.env.VITE_MAPTILER_KEY
  map = new Map({
    container: mapContainer.value,
    style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${apiKey}`,
    center: [7.216, 51.481],
    zoom: 13
  })
})

onBeforeUnmount(() => {
  map?.remove()
})
</script>

<template>
  <div class="map-page">
    <div ref="mapContainer" class="map"></div>
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

@media (max-width: 600px) {
  .map-page {
    min-height: 440px;
  }
}
</style>
