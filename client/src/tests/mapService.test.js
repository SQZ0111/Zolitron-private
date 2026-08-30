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
  coverageLabel,
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

  it("reports total ground coverage as an unrounded percentage number", () => {
    expect(
      coveragePercent({ garbage_coverage: 0.1, litter_coverage: 0.05 }),
    ).toBeCloseTo(15)
    expect(coveragePercent({ litter_coverage: 0.007 })).toBeCloseTo(0.7)
    expect(coveragePercent({})).toBe(0)
    expect(coveragePercent(null)).toBe(0)
  })

  it("labels small coverage with a decimal instead of zero percent", () => {
    expect(coverageLabel({ garbage_coverage: 0.07 })).toBe("7%")
    expect(
      coverageLabel({ garbage_coverage: 0.02, litter_coverage: 0.005 }),
    ).toBe("3%")
    expect(coverageLabel({ garbage_coverage: 0.003 })).toBe("0.3%")
    expect(coverageLabel({ litter_coverage: 0.0001 })).toBe("0.1%")
    expect(coverageLabel({ garbage_coverage: 0, litter_coverage: 0 })).toBe("0%")
    expect(coverageLabel({})).toBe("0%")
    expect(coverageLabel(null)).toBe("0%")
  })

  it("resolves relative backend image URLs", () => {
    expect(resolveBackendImageUrl("/static/example.jpg")).toBe(
      "http://127.0.0.1:8000/static/example.jpg",
    )
  })
})
