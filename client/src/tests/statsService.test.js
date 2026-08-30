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

import { fetchStats } from "../services/statsService"

describe("statsService", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("loads stats from the backend", async () => {
    const stats = {
      image_count: 12,
      classification_count: 10,
      category_count: 2,
      label_count: 4,
      analysis_run_count: 1,
      classifications_by_label: { garbage: 7, "not-garbage": 3 },
      classifications_by_category: { waste: 10 },
      classifications_by_disposition: {
        collect: 4,
        watch: 3,
        "not-garbage": 2,
        "low-confidence": 1,
      },
      classifications_by_city: { Bochum: 8, Essen: 2 },
    }
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(stats),
    })
    vi.stubGlobal("fetch", fetchMock)

    const result = await fetchStats()

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/stats",
    )
    expect(result).toEqual(stats)
  })

  it("throws with the backend error detail on failure", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ detail: "Stats unavailable." }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await expect(fetchStats()).rejects.toThrow("Stats unavailable.")
  })
})
