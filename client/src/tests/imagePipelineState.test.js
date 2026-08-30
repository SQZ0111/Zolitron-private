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
