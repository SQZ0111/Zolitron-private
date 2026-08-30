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
