<script setup>
import { ref } from "vue"

import { navigationLinks } from "../../router/navigation"

defineProps({
  currentCity: {
    type: String,
    default: "Bochum",
  },
})

defineEmits(["change-city", "reset-view"])

const navigationOpen = ref(false)
</script>

<template>
  <aside class="map-legend" aria-label="Map marker legend">
    <h2 class="legend-title">Legend</h2>
    <div class="legend-item">
      <span class="legend-color" />
      <span>Trash/litter at least 60%</span>
    </div>
    <v-btn
      class="change-city"
      color="primary"
      variant="tonal"
      size="small"
      block
      prepend-icon="mdi-map-search-outline"
      @click="$emit('change-city')"
    >
      {{ currentCity }} - Change city
    </v-btn>
    <v-btn
      class="reset-view"
      variant="text"
      size="small"
      block
      prepend-icon="mdi-crosshairs-gps"
      @click="$emit('reset-view')"
    >
      Reset view
    </v-btn>
    <v-menu
      v-model="navigationOpen"
      location="top end"
      :close-on-content-click="true"
    >
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          class="navigation-menu"
          variant="text"
          size="small"
          block
          prepend-icon="mdi-menu"
        >
          Navigation
        </v-btn>
      </template>

      <v-list nav aria-label="Application navigation">
        <v-list-item
          v-for="link in navigationLinks"
          :key="link.route"
          :to="link.route"
          :title="link.name"
          @click="navigationOpen = false"
        />
      </v-list>
    </v-menu>
  </aside>
</template>

<style scoped>
.map-legend {
  position: absolute;
  right: 20px;
  bottom: 28px;
  z-index: 3;
  min-width: 190px;
  padding: 14px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 3px 14px rgba(13, 71, 161, 0.2);
  font-size: 0.82rem;
  backdrop-filter: blur(8px);
}

.legend-title {
  margin-bottom: 9px;
  font-size: 0.9rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 6px;
}

.legend-color {
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: #990066;
}

.change-city {
  margin-top: 12px;
}

.reset-view,
.navigation-menu {
  margin-top: 4px;
}

@media (max-width: 600px) {
  .map-legend {
    right: 12px;
    bottom: 20px;
    min-width: 0;
    padding: 10px 12px;
    font-size: 0.72rem;
  }
}
</style>
