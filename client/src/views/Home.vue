<template>
  <div class="home-dashboard">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-1">Zolitron</h1>
        <p class="text-body-2 text-medium-emphasis mb-6">
          Detection Overview
        </p>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="d-flex justify-center py-10">
        <v-progress-circular indeterminate color="primary" />
      </v-col>
    </v-row>

    <v-alert v-else-if="error" type="error" density="compact" class="mb-6">
      {{ error }}
    </v-alert>

    <template v-else>
      <v-row>
        <v-col cols="12" sm="4">
          <v-card class="stat-card" elevation="2">
            <v-card-text>
              <div class="stat-value">{{ stats.image_count }}</div>
              <div class="stat-label">Images processed</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="4">
          <v-card class="stat-card" elevation="2">
            <v-card-text>
              <div class="stat-value">{{ stats.classification_count }}</div>
              <div class="stat-label">Classifications</div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="4">
          <v-card class="stat-card" elevation="2">
            <v-card-text>
              <div class="stat-value">{{ stats.category_count }}</div>
              <div class="stat-label">Categories tracked</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" md="6">
          <v-card elevation="2">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              By label
            </v-card-title>
            <v-card-text>
              <div
                v-if="!labelBreakdown.length"
                class="text-body-2 text-medium-emphasis"
              >
                No classifications yet.
              </div>
              <div
                v-for="entry in labelBreakdown"
                :key="entry.name"
                class="breakdown-row"
              >
                <div class="d-flex justify-space-between text-body-2 mb-1">
                  <span class="text-capitalize">{{ entry.name }}</span>
                  <span>{{ entry.count }}</span>
                </div>
                <v-progress-linear
                  :model-value="entry.percent"
                  color="primary"
                  height="8"
                  rounded
                />
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card elevation="2">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              By category
            </v-card-title>
            <v-card-text>
              <div
                v-if="!categoryBreakdown.length"
                class="text-body-2 text-medium-emphasis"
              >
                No classifications yet.
              </div>
              <div
                v-for="entry in categoryBreakdown"
                :key="entry.name"
                class="breakdown-row"
              >
                <div class="d-flex justify-space-between text-body-2 mb-1">
                  <span class="text-capitalize">{{ entry.name }}</span>
                  <span>{{ entry.count }}</span>
                </div>
                <v-progress-linear
                  :model-value="entry.percent"
                  color="secondary"
                  height="8"
                  rounded
                />
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" sm="6">
          <v-card class="quick-action" elevation="2" to="/map">
            <v-card-text class="d-flex align-center">
              <v-icon
                icon="mdi-map-search-outline"
                size="28"
                class="mr-3"
                color="primary"
              />
              <div>
                <div class="text-subtitle-2 font-weight-bold">
                  Open the map
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  Review detections by city
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6">
          <v-card class="quick-action" elevation="2" to="/uploads">
            <v-card-text class="d-flex align-center">
              <v-icon
                icon="mdi-cloud-upload-outline"
                size="28"
                class="mr-3"
                color="primary"
              />
              <div>
                <div class="text-subtitle-2 font-weight-bold">
                  Upload images
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  Add and classify new photos
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"

import { fetchStats } from "../services/statsService"

const stats = ref(null)
const loading = ref(true)
const error = ref("")

function toBreakdown(counts, total) {
  return Object.entries(counts || {})
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({
      name,
      count,
      percent: total > 0 ? (count / total) * 100 : 0,
    }))
}

const labelBreakdown = computed(() =>
  toBreakdown(
    stats.value?.classifications_by_label,
    stats.value?.classification_count,
  ),
)
const categoryBreakdown = computed(() =>
  toBreakdown(
    stats.value?.classifications_by_category,
    stats.value?.classification_count,
  ),
)

onMounted(async () => {
  try {
    stats.value = await fetchStats()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-dashboard {
  max-width: 1100px;
}

.stat-card {
  border-radius: 12px;
  text-align: center;
}

.stat-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: rgb(var(--v-theme-primary));
  line-height: 1.1;
}

.stat-label {
  font-size: 0.85rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-top: 4px;
}

.breakdown-row {
  margin-bottom: 14px;
}

.breakdown-row:last-child {
  margin-bottom: 0;
}

.quick-action {
  border-radius: 12px;
  cursor: pointer;
}
</style>
