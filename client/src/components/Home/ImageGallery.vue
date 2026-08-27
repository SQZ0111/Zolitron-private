<script setup>
import { ref, watch } from "vue"

import { listClassifications } from "../../services/imageService"
import { resolveBackendImageUrl } from "../../services/mapService"

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

function isGarbage(item) {
  return item.label === "garbage"
}

function hasBoundingBox(item) {
  return (
    item.bbox_x != null &&
    item.bbox_y != null &&
    item.bbox_width != null &&
    item.bbox_height != null &&
    item.image_width &&
    item.image_height
  )
}

function boundingBoxStyle(item) {
  const left = ((item.bbox_x - item.bbox_width / 2) / item.image_width) * 100
  const top = ((item.bbox_y - item.bbox_height / 2) / item.image_height) * 100
  const width = (item.bbox_width / item.image_width) * 100
  const height = (item.bbox_height / item.image_height) * 100

  return {
    left: `${left}%`,
    top: `${top}%`,
    width: `${width}%`,
    height: `${height}%`,
  }
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
            v-if="hasBoundingBox(selectedItem)"
            class="gallery-bbox"
            :style="boundingBoxStyle(selectedItem)"
          />
        </div>
        <div class="panel-meta-row">
          <span>{{ selectedItem.city }}, {{ selectedItem.country }}</span>
          <span>{{ selectedItem.label }} &middot; {{ selectedItem.status }}</span>
        </div>
      </div>

      <div v-else class="gallery-grid">
        <button
          v-for="item in items"
          :key="item.id"
          type="button"
          class="gallery-thumb"
          :class="{ 'gallery-thumb--garbage': isGarbage(item) }"
          @click="selectedItem = item"
        >
          <img
            :src="resolveBackendImageUrl(item.imgUrl)"
            :alt="`${item.city} image`"
            loading="lazy"
          />
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

@property --gallery-garbage-angle {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}

.gallery-thumb--garbage {
  position: relative;
  border-color: rgba(255, 61, 154, 0.55);
  box-shadow: 0 0 18px rgba(255, 61, 154, 0.65), inset 0 0 10px rgba(255, 61, 154, 0.15);
}

.gallery-thumb--garbage:hover {
  box-shadow: 0 0 26px rgba(255, 61, 154, 0.85), inset 0 0 12px rgba(255, 61, 154, 0.2);
}

.gallery-thumb--garbage::before {
  content: "";
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  padding: 3px;
  background: conic-gradient(
    from var(--gallery-garbage-angle),
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
  animation: gallery-garbage-spin 3s linear infinite;
  pointer-events: none;
}

@keyframes gallery-garbage-spin {
  to {
    --gallery-garbage-angle: 360deg;
  }
}

@media (prefers-reduced-motion: reduce) {
  .gallery-thumb--garbage::before {
    animation: none;
  }
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

.gallery-back {
  align-self: flex-start;
}
</style>
