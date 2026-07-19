import { afterEach, describe, expect, it, vi } from "vitest"

import {
  fetchClassificationMarkers,
  resolveBackendImageUrl,
} from "../services/mapService"

describe("mapService", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("loads classifications filtered by city", async () => {
    const response = [{ id: 1, city: "Bochum" }]
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: vi.fn().mockResolvedValue(response),
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await fetchClassificationMarkers("Bochum")

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/classifications?city=Bochum",
    )
    expect(result).toEqual(response)
  })

  it("resolves relative backend image URLs", () => {
    expect(resolveBackendImageUrl("/static/example.jpg")).toBe(
      "http://127.0.0.1:8000/static/example.jpg",
    )
  })
})
