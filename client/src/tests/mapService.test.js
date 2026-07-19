import { afterEach, describe, expect, it, vi } from "vitest"

import {
  fetchClassificationMarkers,
  isTrashClassification,
  resolveBackendImageUrl,
} from "../services/mapService"

describe("mapService", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("loads classifications filtered by city", async () => {
    const response = [
      { id: 1, city: "Bochum", label: "garbage" },
      { id: 2, city: "Bochum", label: "overgrown" },
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

  it("resolves relative backend image URLs", () => {
    expect(resolveBackendImageUrl("/static/example.jpg")).toBe(
      "http://127.0.0.1:8000/static/example.jpg",
    )
  })
})
