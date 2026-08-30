// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Zolitron
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

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
