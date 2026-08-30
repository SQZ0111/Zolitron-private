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

import { describe, expect, it } from "vitest"
import { createSSRApp, h } from "vue"
import { renderToString } from "vue/server-renderer"

import About from "../views/About.vue"

const passthrough = (tag) => ({
  inheritAttrs: false,
  setup: (_props, { slots, attrs }) => () => h(tag, attrs, slots.default?.()),
})

async function renderAbout() {
  const app = createSSRApp(About)
  app.component("VRow", passthrough("div"))
  app.component("VCol", passthrough("div"))
  return renderToString(app)
}

describe("About view", () => {
  it("renders every team member with name and role", async () => {
    const html = await renderAbout()

    const team = [
      ["Yoav Narevicius", "AI &amp; Data-Pipeline"],
      ["Dimitar Mukarev", "AI &amp; Data-Pipeline"],
      ["Yiseo Lee", "Static Client"],
      ["Saqib Bhatti", "Architecture &amp; Project Organisation"],
      ["Astid Launicke", "Client"],
      ["Said-Mahdi Waezsada", "Backend &amp; Interfaces"],
    ]

    for (const [name, role] of team) {
      expect(html).toContain(name)
      expect(html).toContain(role)
    }
  })

  it("derives a two-letter monogram for each member", async () => {
    const html = await renderAbout()

    for (const initials of ["YN", "DM", "YL", "SB", "AL", "SW"]) {
      expect(html).toMatch(new RegExp(`>\\s*${initials}\\s*</span>`))
    }
  })

  it("marks the monograms decorative and exposes the grid as a list", async () => {
    const html = await renderAbout()

    expect(html).toContain('role="list"')
    expect(html).toContain('role="listitem"')
    expect(html).toContain('aria-hidden="true"')
  })
})
