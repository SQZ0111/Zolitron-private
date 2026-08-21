<template>
  <div class="cyber-panel home-dashboard">
    <v-row>
      <v-col cols="12">
        <h1 class="cyber-title home-title">Zolitron</h1>
        <p class="cyber-subtitle">Detection Overview</p>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="d-flex justify-center py-10">
        <v-progress-circular indeterminate color="#42A5F5" />
      </v-col>
    </v-row>

    <v-alert v-else-if="error" type="error" density="compact" class="mb-6">
      {{ error }}
    </v-alert>

    <template v-else>
      <v-row>
        <v-col cols="12" sm="4">
          <div class="home-card stat-card stat-card--sky">
            <div class="stat-value">{{ stats.image_count }}</div>
            <div class="stat-label">Images processed</div>
          </div>
        </v-col>
        <v-col cols="12" sm="4">
          <div class="home-card stat-card stat-card--navy">
            <div class="stat-value">{{ stats.classification_count }}</div>
            <div class="stat-label">Classifications</div>
          </div>
        </v-col>
        <v-col cols="12" sm="4">
          <div class="home-card stat-card stat-card--deep">
            <div class="stat-value">{{ stats.category_count }}</div>
            <div class="stat-label">Categories tracked</div>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <div class="home-card breakdown-panel">
            <div class="breakdown-header">
              <span class="breakdown-title">{{ activeBreakdown.title }}</span>
              <div class="breakdown-nav">
                <button
                  type="button"
                  class="cyber-arrow"
                  :disabled="breakdownSlides.length < 2"
                  aria-label="Previous breakdown"
                  @click="showPreviousBreakdown"
                >
                  &#10094;
                </button>
                <button
                  type="button"
                  class="cyber-arrow"
                  :disabled="breakdownSlides.length < 2"
                  aria-label="Next breakdown"
                  @click="showNextBreakdown"
                >
                  &#10095;
                </button>
              </div>
            </div>

            <v-window v-model="activeSlide" transition="fade-transition" reverse-transition="fade-transition">
              <v-window-item
                v-for="(slide, index) in breakdownSlides"
                :key="slide.key"
                :value="index"
              >
                <div v-if="!slide.entries.length" class="breakdown-empty">
                  No classifications yet.
                </div>
                <div
                  v-for="entry in slide.entries"
                  :key="entry.name"
                  class="breakdown-row"
                >
                  <div class="breakdown-row-header">
                    <span class="breakdown-name">{{ entry.name }}</span>
                    <span class="breakdown-count">{{ entry.count }}</span>
                  </div>
                  <div class="breakdown-track">
                    <div
                      class="breakdown-fill"
                      :style="{ width: `${entry.percent}%` }"
                    />
                  </div>
                </div>
              </v-window-item>
            </v-window>

            <div class="breakdown-dots">
              <button
                v-for="(slide, index) in breakdownSlides"
                :key="slide.key"
                type="button"
                class="breakdown-dot"
                :class="{ 'breakdown-dot--active': index === activeSlide }"
                :aria-label="`Show ${slide.title}`"
                @click="activeSlide = index"
              />
            </div>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" sm="6">
          <router-link to="/map" class="home-card quick-action">
            <span class="quick-action-icon">&#9737;</span>
            <div>
              <div class="quick-action-title">Open the map</div>
              <div class="quick-action-subtitle">Review detections by city</div>
            </div>
          </router-link>
        </v-col>
        <v-col cols="12" sm="6">
          <router-link
            to="/uploads"
            class="home-card quick-action"
          >
            <span class="quick-action-icon">&#8593;</span>
            <div>
              <div class="quick-action-title">Upload images</div>
              <div class="quick-action-subtitle">Add and classify new photos</div>
            </div>
          </router-link>
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
const activeSlide = ref(0)

function toBreakdown(counts, total) {
  return Object.entries(counts || {})
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({
      name,
      count,
      percent: total > 0 ? (count / total) * 100 : 0,
    }))
}

const breakdownSlides = computed(() => [
  {
    key: "label",
    title: "By label",
    entries: toBreakdown(
      stats.value?.classifications_by_label,
      stats.value?.classification_count,
    ),
  },
  {
    key: "category",
    title: "By category",
    entries: toBreakdown(
      stats.value?.classifications_by_category,
      stats.value?.classification_count,
    ),
  },
])

const activeBreakdown = computed(
  () => breakdownSlides.value[activeSlide.value] || breakdownSlides.value[0],
)

function showNextBreakdown() {
  activeSlide.value = (activeSlide.value + 1) % breakdownSlides.value.length
}

function showPreviousBreakdown() {
  activeSlide.value =
    (activeSlide.value - 1 + breakdownSlides.value.length) %
    breakdownSlides.value.length
}

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
  width: 80vw;
  max-width: 1000px;
  margin: 24px auto;
  align-self: flex-start;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.home-title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  margin: 0 0 2px;
}

.cyber-subtitle {
  margin: 0;
}

.home-card {
  position: relative;
  border-radius: 14px;
  background: linear-gradient(160deg, rgba(20, 49, 92, 0.9), rgba(10, 30, 63, 0.9));
  border: 1px solid rgba(66, 165, 245, 0.25);
  padding: 14px 18px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.home-card:hover {
  transform: translateY(-4px);
}

.stat-card {
  text-align: center;
}

.stat-card--sky {
  box-shadow: 0 0 18px rgba(66, 165, 245, 0.25), inset 0 0 20px rgba(66, 165, 245, 0.06);
}

.stat-card--navy {
  border-color: rgba(13, 71, 161, 0.5);
  box-shadow: 0 0 18px rgba(13, 71, 161, 0.35), inset 0 0 20px rgba(13, 71, 161, 0.1);
}

.stat-card--deep {
  border-color: rgba(30, 136, 229, 0.4);
  box-shadow: 0 0 18px rgba(30, 136, 229, 0.3), inset 0 0 20px rgba(30, 136, 229, 0.08);
}

.stat-card--sky:hover {
  box-shadow: 0 0 32px rgba(66, 165, 245, 0.45), inset 0 0 24px rgba(66, 165, 245, 0.1);
}

.stat-card--navy:hover {
  box-shadow: 0 0 32px rgba(13, 71, 161, 0.55), inset 0 0 24px rgba(13, 71, 161, 0.15);
}

.stat-card--deep:hover {
  box-shadow: 0 0 32px rgba(30, 136, 229, 0.5), inset 0 0 24px rgba(30, 136, 229, 0.12);
}

.stat-value {
  font-family: "Orbitron", "Roboto", sans-serif;
  font-weight: 700;
  font-size: 1.9rem;
  line-height: 1.1;
  color: #eaf6ff;
}

.stat-card--sky .stat-value {
  text-shadow: 0 0 12px rgba(66, 165, 245, 0.85);
}

.stat-card--navy .stat-value {
  text-shadow: 0 0 12px rgba(13, 71, 161, 0.9);
}

.stat-card--deep .stat-value {
  text-shadow: 0 0 12px rgba(30, 136, 229, 0.9);
}

.stat-label {
  margin-top: 6px;
  font-size: 0.82rem;
  color: #90b4d6;
}

.breakdown-panel {
  border-color: rgba(66, 165, 245, 0.2);
}

.breakdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.breakdown-title {
  font-family: "Orbitron", "Roboto", sans-serif;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: #eaf6ff;
}

.breakdown-nav {
  display: flex;
  gap: 8px;
}

.cyber-arrow {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid rgba(66, 165, 245, 0.35);
  background: rgba(66, 165, 245, 0.08);
  color: #42a5f5;
  cursor: pointer;
  font-size: 0.7rem;
  line-height: 1;
}

.cyber-arrow:hover:not(:disabled) {
  background: rgba(66, 165, 245, 0.2);
  box-shadow: 0 0 12px rgba(66, 165, 245, 0.5);
}

.cyber-arrow:disabled {
  opacity: 0.3;
  cursor: default;
}

.breakdown-empty {
  color: #90b4d6;
  font-size: 0.9rem;
}

.breakdown-row {
  margin-bottom: 10px;
}

.breakdown-row:last-child {
  margin-bottom: 0;
}

.breakdown-row-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.88rem;
  color: #eaf6ff;
  margin-bottom: 6px;
  text-transform: capitalize;
}

.breakdown-track {
  height: 8px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.breakdown-fill {
  height: 100%;
  border-radius: 999px;
  background: #42a5f5;
  box-shadow: 0 0 10px rgba(66, 165, 245, 0.6);
}

.breakdown-dots {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 18px;
}

.breakdown-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: none;
  padding: 0;
  background: rgba(255, 255, 255, 0.2);
  cursor: pointer;
}

.breakdown-dot--active {
  background: #42a5f5;
  box-shadow: 0 0 8px rgba(66, 165, 245, 0.8);
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  cursor: pointer;
  border-color: rgba(255, 61, 154, 0.35);
  box-shadow: 0 0 16px rgba(255, 61, 154, 0.2);
}

.quick-action:hover {
  box-shadow: 0 0 28px rgba(255, 61, 154, 0.4);
}

.quick-action-icon {
  font-size: 1.6rem;
  color: #ff3d9a;
  text-shadow: 0 0 10px rgba(255, 61, 154, 0.8);
}

.quick-action-title {
  font-weight: 700;
  color: #eaf6ff;
  font-size: 0.95rem;
}

.quick-action-subtitle {
  color: #90b4d6;
  font-size: 0.82rem;
}

@media (prefers-reduced-motion: reduce) {
  .home-card {
    transition: none;
  }
}
</style>
