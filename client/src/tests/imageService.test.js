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

import { afterEach, describe, expect, it, vi } from "vitest"

import {
  cancelCameraFrameBatchJob,
  getCameraFrameBatchJob,
  startCameraFrameBatchJob,
} from "../services/imageService"

describe("startCameraFrameBatchJob", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("starts a trackable backend job with the selected batch size", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({ jobId: "job-1" }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await startCameraFrameBatchJob(8)

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/images/import/camera-frames/jobs",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ size: 8 }),
      },
    )
  })

  it("passes the cursor when requesting the next batch", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({ jobId: "job-2" }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await startCameraFrameBatchJob(5, "cursor-abc")

    const request = fetchMock.mock.calls[0][1]
    expect(JSON.parse(request.body).cursor).toBe("cursor-abc")
  })

  it("reads a backend job status", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        jobId: "job/1",
        state: "processing",
        progress: 50,
      }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await getCameraFrameBatchJob("job/1")

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/images/import/camera-frames/jobs/job%2F1",
    )
  })

  it("requests backend job cancellation", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        jobId: "job-1",
        state: "stopping",
        progress: 50,
      }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await cancelCameraFrameBatchJob("job-1")

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/images/import/camera-frames/jobs/job-1/cancel",
      { method: "POST" },
    )
  })
})
