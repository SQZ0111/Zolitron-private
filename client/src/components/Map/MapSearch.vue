<script setup>
import { ref } from "vue"

import { searchGermanLocation } from "../../services/mapService"

const emit = defineEmits(["location-found"])

const query = ref("Bochum")
const searching = ref(false)
const error = ref("")

async function submitSearch() {
  if (searching.value) return

  searching.value = true
  error.value = ""
  try {
    emit("location-found", await searchGermanLocation(query.value))
  } catch (searchError) {
    error.value = searchError.message
  } finally {
    searching.value = false
  }
}
</script>

<template>
  <v-card class="map-search" elevation="8">
    <form class="search-form" @submit.prevent="submitSearch">
      <v-text-field
        v-model="query"
        label="Search German city"
        prepend-inner-icon="mdi-map-search-outline"
        variant="outlined"
        density="compact"
        hide-details
        :disabled="searching"
      />
      <v-btn
        color="primary"
        type="submit"
        :loading="searching"
        aria-label="Search location"
      >
        Search
      </v-btn>
    </form>
    <p v-if="error" class="search-error" role="alert">{{ error }}</p>
  </v-card>
</template>

<style scoped>
.map-search {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 3;
  width: min(420px, calc(100% - 40px));
  padding: 12px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(8px);
}

.map-search:hover {
  transform: none;
}

.search-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
}

.search-error {
  margin: 8px 4px 0;
  color: rgb(var(--v-theme-error));
  font-size: 0.78rem;
}

@media (max-width: 600px) {
  .map-search {
    top: 12px;
    left: 12px;
    width: calc(100% - 24px);
  }

  .search-form {
    grid-template-columns: 1fr;
  }
}
</style>
