import { computed, readonly, ref } from "vue"

const state = ref("idle")
const progress = ref(0)
const message = ref("Ready")
const error = ref("")
const processedCount = ref(0)
let observedJobId = null
let observedItemCount = 0

export const imagePipelineState = {
  state: readonly(state),
  progress: readonly(progress),
  message: readonly(message),
  error: readonly(error),
  processedCount: readonly(processedCount),
  active: computed(() =>
    ["queued", "fetching", "validating", "processing", "stopping"].includes(
      state.value,
    ),
  ),
  update(status) {
    state.value = status.state
    progress.value = status.progress ?? 0
    message.value = status.message || status.state
    error.value = status.error || ""

    const jobId = status.jobId || status.job_id || null
    const itemCount = Array.isArray(status.items) ? status.items.length : 0
    if (jobId && jobId !== observedJobId) {
      observedJobId = jobId
      observedItemCount = 0
    }
    if (jobId && itemCount > observedItemCount) {
      processedCount.value += itemCount - observedItemCount
      observedItemCount = itemCount
    }
  },
  reset() {
    state.value = "idle"
    progress.value = 0
    message.value = "Ready"
    error.value = ""
    processedCount.value = 0
    observedJobId = null
    observedItemCount = 0
  },
}
