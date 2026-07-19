import { beforeEach, describe, expect, it } from "vitest"

import { imagePipelineState } from "../services/imagePipelineState"

describe("imagePipelineState", () => {
  beforeEach(() => {
    imagePipelineState.reset()
  })

  it("signals each newly processed job item only once", () => {
    imagePipelineState.update({
      jobId: "job-1",
      state: "processing",
      progress: 60,
      items: [{ id: 1 }],
    })
    expect(imagePipelineState.processedCount.value).toBe(1)

    imagePipelineState.update({
      jobId: "job-1",
      state: "processing",
      progress: 70,
      items: [{ id: 1 }],
    })
    expect(imagePipelineState.processedCount.value).toBe(1)

    imagePipelineState.update({
      jobId: "job-1",
      state: "processing",
      progress: 90,
      items: [{ id: 1 }, { id: 2 }],
    })
    expect(imagePipelineState.processedCount.value).toBe(2)
  })

  it("tracks items independently for consecutive jobs", () => {
    imagePipelineState.update({
      jobId: "job-1",
      state: "ready",
      progress: 100,
      items: [{ id: 1 }],
    })
    imagePipelineState.update({
      jobId: "job-2",
      state: "processing",
      progress: 60,
      items: [{ id: 2 }],
    })

    expect(imagePipelineState.processedCount.value).toBe(2)
  })
})
