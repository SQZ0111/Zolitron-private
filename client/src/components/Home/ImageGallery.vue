<script setup>
import { ref, watch } from "vue"

import { listClassifications } from "../../services/imageService"
import {
  coveragePercent,
  isVisibleTrashMarker,
  markerDisposition,
  resolveBackendImageUrl,
} from "../../services/mapService"

const DISPOSITION_LABELS = {
  collect: "Collect",
  watch: "Watch",
}

const RECENT_LIMIT = 10

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(["update:modelValue"])

const loading = ref(false)
const error = ref("")
const items = ref([])
const selectedItem = ref(null)

function close() {
  emit("update:modelValue", false)
}

function itemDisposition(item) {
  if (item?.disposition) {
    return item.disposition
  }
  // Rows stored before dispositions existed: infer one for accepted trash only.
  return isVisibleTrashMarker(item) ? markerDisposition(item) : null
}

function dispositionBadge(item) {
  return DISPOSITION_LABELS[itemDisposition(item)] || ""
}

function hasBox(box) {
  return (
    box.bbox_x != null &&
    box.bbox_y != null &&
    box.bbox_width != null &&
    box.bbox_height != null
  )
}

function boundingBoxStyle(box, item) {
  const left = ((box.bbox_x - box.bbox_width / 2) / item.image_width) * 100
  const top = ((box.bbox_y - box.bbox_height / 2) / item.image_height) * 100
  const width = (box.bbox_width / item.image_width) * 100
  const height = (box.bbox_height / item.image_height) * 100

  return {
    left: `${left}%`,
    top: `${top}%`,
    width: `${width}%`,
    height: `${height}%`,
  }
}

function detectionBoxes(item) {
  if (!item?.image_width || !item?.image_height) {
    return []
  }

  const detections = (item.detections || []).filter(hasBox)
  // Older rows kept only the single top box on the classification itself.
  const boxes = detections.length ? detections : hasBox(item) ? [item] : []

  return boxes.map((box, index) => ({
    key: `${item.id}-${index}`,
    className: box.class_name || item.label,
    style: boundingBoxStyle(box, item),
  }))
}

watch(
  () => props.modelValue,
  async (isOpen) => {
    if (!isOpen) {
      selectedItem.value = null
      return
    }
    if (items.value.length) {
      return
    }

    loading.value = true
    error.value = ""
    try {
      const fetched = await listClassifications()
      items.value = fetched
        .slice()
        .sort((a, b) => b.id - a.id)
        .slice(0, RECENT_LIMIT)
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  },
)
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    max-width="900"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="cyber-card gallery-panel">
      <div class="panel-header">
        <span class="panel-title">
          {{ selectedItem ? "Image detail" : "Recently classified" }}
        </span>
        <button
          type="button"
          class="cyber-arrow"
          aria-label="Close gallery"
          @click="close"
        >
          &#10005;
        </button>
      </div>

      <div v-if="loading" class="d-flex justify-center py-8">
        <v-progress-circular indeterminate color="#42A5F5" />
      </div>

      <v-alert v-else-if="error" type="error" density="compact">
        {{ error }}
      </v-alert>

      <div v-else-if="!items.length" class="panel-empty">
        No images yet.
      </div>

      <div v-else-if="selectedItem" class="gallery-detail">
        <button
          type="button"
          class="cyber-arrow gallery-back"
          @click="selectedItem = null"
        >
          &#10094;
        </button>
        <div class="gallery-detail-frame">
          <img
            :src="resolveBackendImageUrl(selectedItem.imgUrl)"
            :alt="`${selectedItem.city} image`"
            class="gallery-detail-image"
          />
          <div
            v-for="box in detectionBoxes(selectedItem)"
            :key="box.key"
            class="gallery-bbox"
            :class="`gallery-bbox--${box.className}`"
            :style="box.style"
          />
        </div>
        <div class="panel-meta-row">
          <span>{{ selectedItem.city }}, {{ selectedItem.country }}</span>
          <span>{{ selectedItem.label }} &middot; {{ selectedItem.status }}</span>
          <span v-if="itemDisposition(selectedItem)">
            {{ itemDisposition(selectedItem) }} &middot;
            {{ coveragePercent(selectedItem) }}% coverage
          </span>
        </div>
      </div>

      <div v-else class="gallery-grid">
        <button
          v-for="item in items"
          :key="item.id"
          type="button"
          class="gallery-thumb"
          :class="
            itemDisposition(item) ? `gallery-thumb--${itemDisposition(item)}` : ''
          "
          @click="selectedItem = item"
        >
          <img
            :src="resolveBackendImageUrl(item.imgUrl)"
            :alt="`${item.city} image`"
            loading="lazy"
          />
          <span
            v-if="dispositionBadge(item)"
            class="gallery-thumb-badge"
            :class="`gallery-thumb-badge--${itemDisposition(item)}`"
          >
            {{ dispositionBadge(item) }}
          </span>
          <span class="gallery-thumb-caption">{{ item.city }}</span>
        </button>
      </div>
    </div>
  </v-dialog>
</template>

<style scoped>
.gallery-panel {
  max-height: 80vh;
  overflow-y: auto;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.gallery-thumb {
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(66, 165, 245, 0.25);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(10, 30, 63, 0.6);
  cursor: pointer;
  padding: 0;
  transition: box-shadow 0.2s ease;
}

.gallery-thumb:hover {
  box-shadow: 0 0 16px rgba(66, 165, 245, 0.4);
}

@property --gallery-collect-angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}

.gallery-thumb--collect {
  border-color: rgba(255, 61, 154, 0.55);
  box-shadow: 0 0 18px rgba(255, 61, 154, 0.65), inset 0 0 10px rgba(255, 61, 154, 0.15);
}

.gallery-thumb--collect:hover {
  box-shadow: 0 0 26px rgba(255, 61, 154, 0.85), inset 0 0 12px rgba(255, 61, 154, 0.2);
}

.gallery-thumb--collect::before {
  content: "";
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  padding: 3px;
  background: conic-gradient(
    from var(--gallery-collect-angle),
    #ff3d9a 0%,
    #ffe0f2 10%,
    #ff3d9a 20%,
    rgba(255, 61, 154, 0.25) 45%,
    #ff3d9a 70%,
    #ffe0f2 80%,
    #ff3d9a 90%,
    rgba(255, 61, 154, 0.25) 100%
  );
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: gallery-collect-spin 3s linear infinite;
  pointer-events: none;
}

@keyframes gallery-collect-spin {
  to {
    --gallery-collect-angle: 360deg;
  }
}

@media (prefers-reduced-motion: reduce) {
  .gallery-thumb--collect::before {
    animation: none;
  }
}

.gallery-thumb--watch {
  border-color: rgba(249, 168, 37, 0.55);
  box-shadow: 0 0 14px rgba(249, 168, 37, 0.45), inset 0 0 8px rgba(249, 168, 37, 0.12);
}

.gallery-thumb--watch:hover {
  box-shadow: 0 0 20px rgba(249, 168, 37, 0.65), inset 0 0 10px rgba(249, 168, 37, 0.18);
}

.gallery-thumb-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  z-index: 1;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.gallery-thumb-badge--collect {
  background: #d32f2f;
  color: #fff;
}

.gallery-thumb-badge--watch {
  background: #f9a825;
  color: #241a00;
}

.gallery-thumb img {
  width: 100%;
  height: 110px;
  object-fit: cover;
}

.gallery-thumb-caption {
  padding: 6px 8px;
  font-size: 0.78rem;
  color: #90b4d6;
  text-align: left;
  text-transform: capitalize;
}

.gallery-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gallery-detail-frame {
  position: relative;
  line-height: 0;
}

.gallery-detail-image {
  width: 100%;
  height: auto;
  max-height: 55vh;
  border-radius: 10px;
}

.gallery-bbox {
  position: absolute;
  border: 2px solid #ff3d9a;
  box-shadow: 0 0 12px rgba(255, 61, 154, 0.7);
  border-radius: 2px;
  pointer-events: none;
}

.gallery-bbox--litter {
  border-color: #f9a825;
  box-shadow: 0 0 12px rgba(249, 168, 37, 0.7);
}

.gallery-back {
  align-self: flex-start;
}
</style>
