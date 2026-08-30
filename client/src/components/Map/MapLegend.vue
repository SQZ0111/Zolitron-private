<script setup>
import { ref } from "vue"

import { navigationLinks } from "../../router/navigation"

defineProps({
  currentCity: {
    type: String,
    default: "Bochum",
  },
  availableCities: {
    type: Array,
    default: () => [],
  },
  showLitter: {
    type: Boolean,
    default: true,
  },
})

defineEmits(["change-city", "reset-view", "select-city", "update:showLitter"])

const navigationOpen = ref(false)
const citiesOpen = ref(false)
</script>

<template>
  <v-sheet
    tag="aside"
    theme="blueSkyNight"
    class="map-legend cyber-card"
    aria-label="Map marker legend"
  >
    <h2 class="panel-title legend-title">Legend</h2>
    <div class="legend-item">
      <span class="legend-color legend-color--collect" />
      <span>Garbage &mdash; collection recommended</span>
    </div>
    <div class="legend-item">
      <span class="legend-color legend-color--watch" />
      <span>Litter &mdash; monitoring</span>
    </div>
    <v-switch
      class="legend-toggle"
      :model-value="showLitter"
      color="warning"
      density="compact"
      hide-details
      label="Show litter (monitoring)"
      @update:model-value="$emit('update:showLitter', Boolean($event))"
    />
    <v-menu
      v-if="availableCities.length"
      v-model="citiesOpen"
      location="top end"
      :close-on-content-click="true"
    >
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          class="change-city"
          color="primary"
          variant="tonal"
          size="small"
          block
          prepend-icon="mdi-map-marker-multiple-outline"
        >
          {{ currentCity }} - Cities with data
        </v-btn>
      </template>

      <v-list nav aria-label="Cities with imported data">
        <v-list-item
          v-for="city in availableCities"
          :key="city.name"
          :title="city.name"
          :subtitle="`${city.count} classification(s)`"
          @click="$emit('select-city', city)"
        />
      </v-list>
    </v-menu>
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
  </v-sheet>
</template>

<style scoped>
.map-legend {
  position: absolute;
  right: 20px;
  bottom: 28px;
  z-index: 3;
  min-width: 190px;
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
  color: #eaf6ff;
}

.legend-color {
  box-sizing: border-box;
  width: 14px;
  height: 14px;
  flex: 0 0 auto;
  border-radius: 50%;
}

.legend-color--collect {
  background: #d32f2f;
}

.legend-color--watch {
  background: transparent;
  border: 2px solid #f9a825;
}

.legend-toggle {
  margin-top: 4px;
  font-size: 0.78rem;
}

/* Match the 9px gap the legend items use between marker and text. */
.legend-toggle :deep(.v-label) {
  margin-left: 9px;
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
