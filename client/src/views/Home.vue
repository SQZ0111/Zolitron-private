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
          <div
            class="cyber-card stat-card stat-card--sky stat-card--clickable"
            role="button"
            tabindex="0"
            aria-haspopup="dialog"
            @click="galleryOpen = true"
            @keydown.enter="galleryOpen = true"
          >
            <div class="stat-value">{{ stats.image_count }}</div>
            <div class="stat-label">Images processed</div>
          </div>
        </v-col>
        <v-col cols="12" sm="4">
          <div class="cyber-card stat-card stat-card--navy">
            <div class="stat-value">{{ stats.classification_count }}</div>
            <div class="stat-label">Classifications</div>
          </div>
        </v-col>
        <v-col cols="12" sm="4">
          <div class="cyber-card stat-card stat-card--deep">
            <div class="stat-value">{{ stats.category_count }}</div>
            <div class="stat-label">Categories tracked</div>
          </div>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
          <div class="cyber-card breakdown-panel">
            <div class="panel-header">
              <span class="panel-title">{{ activeBreakdown.title }}</span>
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
              <v-window-item :value="0">
                <div v-if="!dispositionSlices.length" class="panel-empty">
                  No classifications yet.
                </div>
                <div v-else class="donut-layout">
                  <div
                    class="donut"
                    role="img"
                    :aria-label="donutLabel"
                    :style="{ background: donutGradient }"
                  >
                    <div class="donut-hole">
                      <span class="donut-total">{{ dispositionTotal }}</span>
                      <span class="donut-total-label">Total</span>
                    </div>
                  </div>
                  <ul class="donut-legend">
                    <li
                      v-for="slice in dispositionSlices"
                      :key="slice.name"
                      class="donut-legend-row"
                    >
                      <span
                        class="donut-swatch"
                        aria-hidden="true"
                        :style="{ background: slice.color }"
                      />
                      <span class="donut-legend-name">{{ slice.name }}</span>
                      <span class="donut-legend-count">{{ slice.count }}</span>
                      <span class="donut-legend-percent">
                        {{ formatPercent(slice.percent) }}
                      </span>
                    </li>
                  </ul>
                </div>
              </v-window-item>

              <v-window-item :value="1">
                <div v-if="!cityEntries.length" class="panel-empty">
                  No classifications yet.
                </div>
                <div
                  v-for="entry in cityEntries"
                  :key="entry.name"
                  class="breakdown-row"
                >
                  <div class="panel-meta-row">
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
          <router-link to="/map" class="cyber-card quick-action">
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
            class="cyber-card quick-action"
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

    <ImageGallery v-model="galleryOpen" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"

import ImageGallery from "../components/Home/ImageGallery.vue"
import { fetchStats } from "../services/statsService"

// The action buckets in reading order, with the colours the map already uses.
// Rows the backend could not act on arrive under the "low-confidence" key.
const DISPOSITION_BUCKETS = [
  { name: "collect", color: "#d32f2f" },
  { name: "watch", color: "#f9a825" },
  { name: "not-garbage", color: "#5a7599" },
  { name: "low-confidence", color: "#37507a" },
]

const breakdownSlides = [
  { key: "disposition", title: "Recommendations" },
  { key: "city", title: "By city" },
]

const stats = ref(null)
const loading = ref(true)
const error = ref("")
const activeSlide = ref(0)
const galleryOpen = ref(false)

function toBreakdown(counts, total) {
  return Object.entries(counts || {})
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({
      name,
      count,
      percent: total > 0 ? (count / total) * 100 : 0,
    }))
}

function formatPercent(percent) {
  if (percent > 0 && percent < 1) {
    return "<1%"
  }
  return `${Math.round(percent)}%`
}

const dispositionSlices = computed(() => {
  const counts = stats.value?.classifications_by_disposition || {}
  const buckets = DISPOSITION_BUCKETS.map(({ name, color }) => ({
    name,
    color,
    count: counts[name] || 0,
  })).filter((bucket) => bucket.name !== "low-confidence" || bucket.count > 0)

  const total = buckets.reduce((sum, bucket) => sum + bucket.count, 0)
  if (total === 0) {
    return []
  }

  return buckets.map((bucket) => ({
    ...bucket,
    percent: (bucket.count / total) * 100,
  }))
})

const dispositionTotal = computed(() =>
  dispositionSlices.value.reduce((sum, slice) => sum + slice.count, 0),
)

// Hand-rolled donut: one conic-gradient with a stop pair per bucket, no chart
// library. The last stop is pinned to 100% so rounding never leaves a seam.
const donutGradient = computed(() => {
  const slices = dispositionSlices.value
  let cursor = 0

  const stops = slices.map((slice, index) => {
    const start = cursor
    const end = index === slices.length - 1 ? 100 : cursor + slice.percent
    cursor = end
    return `${slice.color} ${start}% ${end}%`
  })

  return `conic-gradient(${stops.join(", ")})`
})

const donutLabel = computed(() =>
  dispositionSlices.value
    .map(
      (slice) =>
        `${slice.name}: ${slice.count} (${formatPercent(slice.percent)})`,
    )
    .join(", "),
)

const cityEntries = computed(() =>
  toBreakdown(
    stats.value?.classifications_by_city,
    stats.value?.classification_count,
  ),
)

const activeBreakdown = computed(
  () => breakdownSlides[activeSlide.value] || breakdownSlides[0],
)

function showNextBreakdown() {
  activeSlide.value = (activeSlide.value + 1) % breakdownSlides.length
}

function showPreviousBreakdown() {
  activeSlide.value =
    (activeSlide.value - 1 + breakdownSlides.length) % breakdownSlides.length
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

.stat-card {
  text-align: center;
}

.stat-card--clickable {
  cursor: pointer;
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

.breakdown-nav {
  display: flex;
  gap: 8px;
}

.breakdown-row {
  margin-bottom: 10px;
}

.breakdown-row:last-child {
  margin-bottom: 0;
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

.donut-layout {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
  padding: 4px 0;
}

.donut {
  position: relative;
  flex: 0 0 auto;
  width: 132px;
  height: 132px;
  border-radius: 50%;
  box-shadow: 0 0 18px rgba(66, 165, 245, 0.25);
}

.donut-hole {
  position: absolute;
  inset: 27%;
  border-radius: 50%;
  background: linear-gradient(160deg, rgba(20, 49, 92, 0.97), rgba(10, 30, 63, 0.97));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.donut-total {
  font-family: "Orbitron", "Roboto", sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  line-height: 1.1;
  color: #eaf6ff;
  text-shadow: 0 0 10px rgba(66, 165, 245, 0.7);
}

.donut-total-label {
  font-size: 0.6rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #90b4d6;
}

.donut-legend {
  flex: 1 1 220px;
  min-width: 0;
  list-style: none;
  margin: 0;
  padding: 0;
}

.donut-legend-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 0;
  font-size: 0.88rem;
  color: #eaf6ff;
}

.donut-legend-row + .donut-legend-row {
  border-top: 1px solid rgba(66, 165, 245, 0.12);
}

.donut-swatch {
  flex: 0 0 auto;
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.donut-legend-name {
  flex: 1 1 auto;
  text-transform: capitalize;
}

.donut-legend-count {
  font-weight: 700;
}

.donut-legend-percent {
  min-width: 42px;
  text-align: right;
  font-size: 0.8rem;
  color: #90b4d6;
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
</style>
