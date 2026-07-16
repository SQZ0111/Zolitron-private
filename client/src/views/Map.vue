<!--
<template>
  <v-row>
    <v-col cols="12">
      <v-card class="pa-6">
        <v-card-title class="text-h4">Cats are superior to dogs</v-card-title>
        <v-card-text>
          <div class="placeholder">
            <v-icon size="64" color="grey">mdi-map</v-icon>
            <p class="text-subtitle-1 mt-4">We will use Leaflet or an other map lib</p>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<style scoped>
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 8px;
}
</style>
-->

<script setup>
import { ref, onMounted } from 'vue'
import { Map } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const mapContainer = ref(null)

onMounted(() => {
  const apiKey = import.meta.env.VITE_MAPTILER_KEY
  console.log(apiKey);
  const map = new Map({
    container: mapContainer.value,
    style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${apiKey}`,
    center: [7.216, 51.481],
    zoom: 13
  })
})
</script>

<template>
  <div ref="mapContainer" class="map"></div>
</template>

<style scoped>
.map {
  width: 100%;
  height: calc(100vh - 64px);
}
</style>