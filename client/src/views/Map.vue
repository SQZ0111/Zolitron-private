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
import { Map, Marker, Popup } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const mapContainer = ref(null)
const map = ref(null)
const search = ref("")
const initialState = { lng: 7.216, lat: 51.481, zoom: 13 }

const reports = [
  {
    id: 1,
    lng: 7.216,
    lat: 51.481,
    classification: ['garbage', 'not greenery'],
    image: '../public/garbage.jpg'
  },
  {
    id: 2,
    lng: 7.233163,
    lat: 51.458288,
    classification: ['not garbage', 'greenery'],
    image: '../public/greenery.jpg'
  },
  {
    id: 3,
    lng: 7.214889,
    lat: 51.482917,
    classification: ['garbage', 'greenery'],
    image: '../public/garbageAndGreenery.jpg'
  }
]

const response = [
  {
    "id": 1,
    "image_id": 1,
    "label_id": 1,
    "category_id": 1,
    "analysis_run_id": 1,
    "label": "overgrown",
    "category": "vegetation",
    "confidence": 0.91,
    "status": "classified",
    "latitude": 51.4818,
    "longitude": 7.2162,
    "imgUrl": "/static/dummy-images/overgrown-1.jpg",
    "city": "Bochum",
    "country": "Germany"
  }
]


onMounted(() => {
  const apiKey = import.meta.env.VITE_MAPTILER_KEY
  
  map.value = new Map({
    container: mapContainer.value,
    style: `https://api.maptiler.com/maps/streets-v2/style.json?key=${apiKey}`,
    center: [initialState.lng, initialState.lat],
    zoom: initialState.zoom
  })

  reports.forEach(report => {

    const popup = new Popup({ offset: 25 }).setHTML(`
      <div style="text-align:center">
        <h3>Report ${report.id}</h3>
        <img src="${report.image}" width="220">
        <p>${report.classification.join(", ")}</p>
      </div>
    `)

    if (report.classification.includes('garbage') && report.classification.includes('not greenery')) {
        new Marker({color: "#990066"}).setLngLat([report.lng, report.lat]).setPopup(popup).addTo(map.value);
    } else if (report.classification.includes('not garbage') && report.classification.includes('greenery')) {
        new Marker({color: "#66ff99"}).setLngLat([report.lng, report.lat]).setPopup(popup).addTo(map.value);
    } else if (report.classification.includes('garbage') && report.classification.includes('greenery')) {
        new Marker({color: "#808080"}).setLngLat([report.lng, report.lat]).setPopup(popup).addTo(map.value);
    }  else {
      console.error(`Ungültige Klassifizierung: ${report.classification}`);
    }
    });
})

async function searchLocation() {
  if (!search.value) return;

  const apiKey = import.meta.env.VITE_MAPTILER_KEY;

  const response = await fetch(
    `https://api.maptiler.com/geocoding/${encodeURIComponent(search.value)}.json?key=${apiKey}`
  );

  const data = await response.json();

  if (data.features.length === 0) {
    alert("Ort nicht gefunden.");
    return;
  }

  const [lng, lat] = data.features[0].center;

  map.value.flyTo({
    center: [lng, lat],
    zoom: 13
  });
}
</script>

<template>
  <div class="map-wrapper">

    <div class="search-box">
      <input
        v-model="search"
        @keyup.enter="searchLocation"
        type="text"
        placeholder="Stadt suchen..."
      />
      <button @click="searchLocation">
        Suchen
      </button>
    </div>

    <!-- HIER wird die Karte gerendert -->
    <div ref="mapContainer" class="map"></div>

    <div class="legend">
      <h4>Legende</h4>

      <div class="legend-item">
        <span class="legend-color garbage"></span>
        <span>Garbage, no greenery</span>
      </div>

      <div class="legend-item">
        <span class="legend-color greenery"></span>
        <span>No garbage, greenery</span>
      </div>

      <div class="legend-item">
        <span class="legend-color both"></span>
        <span>Garbage and greenery</span>
      </div>
    </div>

  </div>
</template>

<style scoped>
.map-wrapper {
  position: relative;
  width: 100%;
  height: calc(100vh - 64px);
}

.map {
  width: 100%;
  height: 100%;
}

.legend {
  position: absolute;
  bottom: 20px;
  right: 20px;

  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);

  font-size: 14px;
}

.legend h4 {
  margin: 0 0 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.legend-item:last-child {
  margin-bottom: 0;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: 8px;
}

.garbage {
  background: #990066;
}

.greenery {
  background: #66ff99;
}

.both {
  background: #808080;
}

.search-box {
  position: absolute;
  top: 40px;
  left: 20px;

  z-index: 10;

  background: white;
  padding: 10px;
  border-radius: 8px;

  box-shadow: 0 2px 8px rgba(0,0,0,.2);

  display: flex;
  gap: 8px;
}

.search-box input {
  padding: 6px;
  width: 220px;
}

.search-box button {
  padding: 6px 12px;
}
</style>