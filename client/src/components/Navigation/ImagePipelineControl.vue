<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue"

import {
  cancelMapillaryBatchJob,
  getMapillaryBatchJob,
  startMapillaryBatchJob,
} from "../../services/imageService"
import { imagePipelineState } from "../../services/imagePipelineState"

const menuOpen = ref(false)
const city = ref("Bochum")
const batchSize = ref(5)
const autoFetch = ref(false)
const maxAutomaticBatches = ref(3)
const automaticBatchesCompleted = ref(0)
const paginationNext = ref(null)
const currentJobId = ref(null)
let pollTimer

const statusLabel = computed(() => {
  const labels = {
    idle: "Ready",
    queued: "Queued",
    fetching: "Fetching",
    validating: "Validating",
    processing: "Processing",
    stopping: "Stopping",
    stopped: "Stopped",
    ready: "Ready",
    error: "Failed",
  }
  return labels[imagePipelineState.state.value] || "Ready"
})

const canFetchNext = computed(() => Boolean(paginationNext.value))
const actionLabel = computed(() =>
  canFetchNext.value ? "Fetch next batch" : "Start fetching",
)

watch(city, () => {
  if (!imagePipelineState.active.value) {
    paginationNext.value = null
    imagePipelineState.reset()
  }
})

function schedulePoll(jobId) {
  pollTimer = window.setTimeout(() => pollJob(jobId), 700)
}

async function pollJob(jobId) {
  try {
    const status = await getMapillaryBatchJob(jobId)
    imagePipelineState.update(status)

    if (status.state === "ready") {
      currentJobId.value = null
      paginationNext.value = status.paginationNext || null
      if (
        autoFetch.value &&
        paginationNext.value &&
        automaticBatchesCompleted.value < maxAutomaticBatches.value
      ) {
        automaticBatchesCompleted.value += 1
        await startFetch(true)
        return
      }

      if (autoFetch.value) {
        const reason = paginationNext.value
          ? `limit of ${maxAutomaticBatches.value} automatic batch(es) reached`
          : "no more sites are available"
        imagePipelineState.update({
          state: "ready",
          progress: 100,
          message: `Automatic fetching complete: ${reason}`,
          items: [],
        })
      }
      return
    }
    if (["error", "stopped"].includes(status.state)) {
      currentJobId.value = null
      return
    }
    schedulePoll(jobId)
  } catch (error) {
    imagePipelineState.update({
      state: "error",
      progress: 100,
      message: "Status unavailable",
      error: error.message,
    })
  }
}

async function startFetch(isAutomatic = false) {
  if (imagePipelineState.active.value) {
    return
  }
  if (!city.value.trim()) {
    imagePipelineState.update({
      state: "error",
      progress: 0,
      message: "City required",
      error: "Please enter a city.",
    })
    return
  }

  maxAutomaticBatches.value = Math.min(
    25,
    Math.max(0, Number(maxAutomaticBatches.value) || 0),
  )

  if (!isAutomatic) {
    automaticBatchesCompleted.value = 0
  }

  imagePipelineState.update({
    state: "queued",
    progress: 0,
    message: isAutomatic
      ? `Starting automatic batch ${automaticBatchesCompleted.value} of ${maxAutomaticBatches.value}`
      : "Starting backend job",
  })

  try {
    const result = await startMapillaryBatchJob(
      city.value,
      "Germany",
      batchSize.value,
      paginationNext.value,
    )
    currentJobId.value = result.jobId
    menuOpen.value = false
    schedulePoll(result.jobId)
  } catch (error) {
    imagePipelineState.update({
      state: "error",
      progress: 100,
      message: "Could not start",
      error: error.message,
    })
  }
}

async function stopFetching() {
  autoFetch.value = false
  window.clearTimeout(pollTimer)

  if (!currentJobId.value) {
    imagePipelineState.update({
      state: "stopped",
      progress: imagePipelineState.progress.value,
      message: "Automatic fetching stopped",
    })
    return
  }

  try {
    const status = await cancelMapillaryBatchJob(currentJobId.value)
    imagePipelineState.update(status)
    if (status.state === "stopping") {
      schedulePoll(currentJobId.value)
    } else {
      currentJobId.value = null
    }
  } catch (error) {
    imagePipelineState.update({
      state: "error",
      progress: 100,
      message: "Could not stop",
      error: error.message,
    })
  }
}

onBeforeUnmount(() => {
  window.clearTimeout(pollTimer)
})
</script>

<template>
  <div class="pipeline-control">
    <div class="pipeline-status" role="status" aria-live="polite">
      <div class="d-flex align-center justify-space-between">
        <span
          class="status-label"
          :title="imagePipelineState.message.value"
        >
          {{ imagePipelineState.message.value || statusLabel }}
        </span>
        <span class="status-percent">{{ imagePipelineState.progress.value }}%</span>
      </div>
      <v-progress-linear
        :model-value="imagePipelineState.progress.value"
        :color="imagePipelineState.state.value === 'error' ? 'error' : 'accent'"
        height="4"
        rounded
      />
    </div>

    <v-menu
      v-model="menuOpen"
      :close-on-content-click="false"
      location="bottom start"
      offset="10"
    >
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          variant="tonal"
          color="white"
          prepend-icon="mdi-map-search-outline"
          class="fetch-button"
        >
          Fetch sites
        </v-btn>
      </template>

      <v-card class="fetch-menu" elevation="12">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Fetch Mapillary sites
        </v-card-title>
        <v-card-text>
          <v-text-field
            v-model="city"
            label="German city"
            prepend-inner-icon="mdi-map-marker-outline"
            variant="outlined"
            density="compact"
            :disabled="imagePipelineState.active.value"
          />

          <div class="d-flex justify-space-between text-body-2">
            <span>Images per batch</span>
            <strong>{{ batchSize }}</strong>
          </div>
          <v-slider
            v-model="batchSize"
            :min="1"
            :max="25"
            :step="1"
            thumb-label
            hide-details
            :disabled="imagePipelineState.active.value"
          />

          <v-checkbox
            v-model="autoFetch"
            label="Automatically fetch the next batch"
            color="primary"
            density="compact"
            hide-details
            class="mb-3"
          />

          <v-text-field
            v-model.number="maxAutomaticBatches"
            label="Maximum automatic batches"
            hint="Fetched after the first manual batch"
            type="number"
            :min="0"
            :max="25"
            persistent-hint
            variant="outlined"
            density="compact"
            :disabled="imagePipelineState.active.value"
            class="mb-3"
          />

          <v-alert
            v-if="imagePipelineState.error.value"
            type="error"
            density="compact"
            class="mb-3"
          >
            {{ imagePipelineState.error.value }}
          </v-alert>

          <v-btn
            block
            color="primary"
            :loading="imagePipelineState.active.value"
            :disabled="imagePipelineState.active.value"
            @click="startFetch"
          >
            {{ actionLabel }}
          </v-btn>

        </v-card-text>
      </v-card>
    </v-menu>

    <v-btn
      v-if="imagePipelineState.active.value"
      color="error"
      variant="flat"
      prepend-icon="mdi-stop-circle-outline"
      class="stop-button"
      @click="stopFetching"
    >
      STOP
    </v-btn>
  </div>
</template>

<style scoped>
.pipeline-control {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-left: 20px;
}

.pipeline-status {
  width: 220px;
  color: white;
}

.status-percent {
  font-size: 0.72rem;
  line-height: 1.2;
}

.status-label {
  min-width: 0;
  overflow: hidden;
  font-size: 0.72rem;
  font-weight: 600;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fetch-menu {
  width: min(350px, calc(100vw - 24px));
}

.stop-button {
  font-weight: 700;
}

@media (max-width: 900px) {
  .pipeline-control {
    gap: 8px;
    margin-left: 8px;
  }

  .pipeline-status {
    width: 90px;
  }

  .status-percent {
    display: none;
  }
}

@media (max-width: 500px) {
  .pipeline-status {
    width: 72px;
  }
}

</style>
