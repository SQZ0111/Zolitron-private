import { computed, readonly, ref } from "vue"

const state = ref("idle")
const progress = ref(0)
const message = ref("Ready")
const error = ref("")
const processedCount = ref(0)

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
    if (status.state === "ready") {
      processedCount.value += status.items?.length || 0
    }
  },
  reset() {
    state.value = "idle"
    progress.value = 0
    message.value = "Ready"
    error.value = ""
    processedCount.value = 0
  },
}
