import { afterEach, describe, expect, it, vi } from "vitest"

import {
  cancelMapillaryBatchJob,
  getMapillaryBatchJob,
  importMapillaryBatch,
  startMapillaryBatchJob,
} from "../services/imageService"

describe("importMapillaryBatch", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("requests the first Mapillary batch with the selected size", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({
        items: [],
        paginationNext: "offset:8",
      }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await importMapillaryBatch(" Bochum ", "Germany", 8)

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/images/import/mapillary/batch",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          city: "Bochum",
          country: "Germany",
          limit: 8,
        }),
      },
    )
  })

  it("passes paginationNext when requesting the next batch", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({ items: [], paginationNext: null }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await importMapillaryBatch("Bochum", "Germany", 5, "offset:5")

    const request = fetchMock.mock.calls[0][1]
    expect(JSON.parse(request.body).paginationNext).toBe("offset:5")
  })

  it("starts a trackable backend job", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue({ jobId: "job-1" }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await startMapillaryBatchJob("Bochum", "Germany", 5)

    expect(fetchMock.mock.calls[0][0]).toBe(
      "http://127.0.0.1:8000/api/images/import/mapillary/jobs",
    )
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

    await getMapillaryBatchJob("job/1")

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/images/import/mapillary/jobs/job%2F1",
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

    await cancelMapillaryBatchJob("job-1")

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/images/import/mapillary/jobs/job-1/cancel",
      { method: "POST" },
    )
  })
})
