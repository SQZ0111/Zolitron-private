import { afterEach, describe, expect, it, vi } from "vitest"

import {
  coveragePercent,
  fetchClassificationMarkers,
  isTrashClassification,
  isVisibleTrashMarker,
  markerDisposition,
  resolveBackendImageUrl,
} from "../services/mapService"

describe("mapService", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("loads garbage and litter classifications filtered by city only", async () => {
    const response = [
      {
        id: 1,
        city: "Bochum",
        label: "garbage",
        confidence: 0.72,
        status: "classified",
        disposition: "collect",
      },
      {
        id: 2,
        city: "Bochum",
        label: "garbage",
        confidence: 0.57,
        status: "low-confidence",
      },
      {
        id: 3,
        city: "Bochum",
        label: "overgrown",
        confidence: 0.95,
        status: "classified",
      },
      {
        id: 4,
        city: "Bochum",
        label: "litter",
        confidence: 0.68,
        status: "classified",
        disposition: "watch",
      },
    ]
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(response),
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await fetchClassificationMarkers("Bochum")

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/classifications?city=Bochum",
    )
    expect(result).toEqual([response[0], response[3]])
  })

  it("accepts only garbage and litter classifications as markers", () => {
    expect(isTrashClassification({ label: "garbage" })).toBe(true)
    expect(isTrashClassification({ label: "LITTER" })).toBe(true)
    expect(isTrashClassification({ label: "not-garbage" })).toBe(false)
    expect(isTrashClassification({ label: "overgrown" })).toBe(false)
  })

  it("shows accepted trash markers from 60 percent confidence", () => {
    expect(
      isVisibleTrashMarker({
        label: "garbage",
        confidence: 0.6,
        status: "classified",
      }),
    ).toBe(true)
    expect(
      isVisibleTrashMarker({
        label: "litter",
        confidence: "0.72",
        status: "classified",
      }),
    ).toBe(true)
    expect(
      isVisibleTrashMarker({
        label: "garbage",
        confidence: 0.5999,
        status: "classified",
      }),
    ).toBe(false)
    expect(
      isVisibleTrashMarker({
        label: "garbage",
        confidence: 0.7,
        status: "low-confidence",
      }),
    ).toBe(false)
    expect(
      isVisibleTrashMarker({
        label: "overgrown",
        confidence: 0.99,
        status: "classified",
      }),
    ).toBe(false)
  })

  it("reads the stored disposition and falls back for older rows", () => {
    expect(markerDisposition({ label: "litter", disposition: "collect" })).toBe(
      "collect",
    )
    expect(markerDisposition({ label: "garbage", disposition: "watch" })).toBe(
      "watch",
    )
    expect(markerDisposition({ label: "litter" })).toBe("watch")
    expect(markerDisposition({ label: "garbage" })).toBe("collect")
  })

  it("reports total frame coverage as a percentage", () => {
    expect(
      coveragePercent({ garbage_coverage: 0.1, litter_coverage: 0.05 }),
    ).toBe(15)
    expect(coveragePercent({ litter_coverage: 0.124 })).toBe(12)
    expect(coveragePercent({})).toBe(0)
    expect(coveragePercent(null)).toBe(0)
  })

  it("resolves relative backend image URLs", () => {
    expect(resolveBackendImageUrl("/static/example.jpg")).toBe(
      "http://127.0.0.1:8000/static/example.jpg",
    )
  })
})
