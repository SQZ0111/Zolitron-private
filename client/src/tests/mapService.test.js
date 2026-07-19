import { afterEach, describe, expect, it, vi } from "vitest"

import {
  fetchClassificationMarkers,
  isTrashClassification,
  isVisibleTrashMarker,
  resolveBackendImageUrl,
} from "../services/mapService"

describe("mapService", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("loads classifications filtered by city", async () => {
    const response = [
      {
        id: 1,
        city: "Bochum",
        label: "garbage",
        confidence: 0.72,
        status: "classified",
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
    ]
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(response),
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await fetchClassificationMarkers("Bochum")

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/classifications?city=Bochum&label=garbage",
    )
    expect(result).toEqual([response[0]])
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

  it("resolves relative backend image URLs", () => {
    expect(resolveBackendImageUrl("/static/example.jpg")).toBe(
      "http://127.0.0.1:8000/static/example.jpg",
    )
  })
})
