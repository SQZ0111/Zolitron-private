<!--
SPDX-License-Identifier: MIT
Copyright (c) 2026 Zolitron

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-->

<template>
  <div class="cyber-panel about-panel">
    <v-row>
      <v-col cols="12">
        <h1 class="cyber-title about-title">About</h1>
        <p class="cyber-subtitle">The Team</p>
      </v-col>
    </v-row>

    <v-row role="list" aria-label="Project team">
      <v-col
        v-for="member in members"
        :key="member.name"
        cols="12"
        sm="6"
        md="4"
        role="listitem"
        class="d-flex"
      >
        <div
          class="cyber-card member-card"
          :class="`member-card--${member.discipline}`"
        >
          <span class="member-monogram" aria-hidden="true">
            {{ member.initials }}
          </span>
          <span class="member-name">{{ member.name }}</span>
          <span class="member-role">{{ member.role }}</span>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <p class="cyber-subtitle about-footer">
          Version 1.0.0 &middot; Built with Vue 3 + Vuetify
        </p>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
const team = [
  { name: "Yoav Narevicius", role: "AI & Data-Pipeline" },
  { name: "Dimitar Mukarev", role: "AI & Data-Pipeline" },
  { name: "Yiseo Lee", role: "Static Client" },
  { name: "Saqib Bhatti", role: "Architecture & Project Organisation" },
  { name: "Astid Launicke", role: "Client" },
  { name: "Said-Mahdi Waezsada", role: "Backend & Interfaces" },
]

const disciplineRules = [
  { match: "architecture", discipline: "architecture" },
  { match: "backend", discipline: "backend" },
  { match: "data-pipeline", discipline: "ai" },
  { match: "client", discipline: "client" },
]

function initialsOf(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase()
}

function disciplineOf(role) {
  const value = role.toLowerCase()
  const rule = disciplineRules.find((entry) => value.includes(entry.match))
  return rule ? rule.discipline : "general"
}

const members = team.map((member) => ({
  ...member,
  initials: initialsOf(member.name),
  discipline: disciplineOf(member.role),
}))
</script>

<style scoped>
.about-panel {
  width: 80vw;
  max-width: 1000px;
  margin: 24px auto;
  align-self: flex-start;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.about-title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  margin: 0 0 2px;
}

.cyber-subtitle {
  margin: 0;
}

.member-card {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 10px;
  padding: 20px 16px;
}

.member-monogram {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  font-family: "Orbitron", "Roboto", sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: 0.04em;
  line-height: 1;
  color: #eaf6ff;
  background: radial-gradient(
    circle at 30% 25%,
    rgba(66, 165, 245, 0.35),
    rgba(10, 30, 63, 0.95) 70%
  );
  border: 1px solid rgba(66, 165, 245, 0.35);
  box-shadow:
    0 0 16px rgba(66, 165, 245, 0.25),
    inset 0 0 18px rgba(66, 165, 245, 0.08);
  text-shadow: 0 0 12px rgba(66, 165, 245, 0.85);
  transition: box-shadow 0.2s ease;
}

.member-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: #eaf6ff;
}

.member-role {
  display: inline-block;
  font-size: 0.8rem;
  line-height: 1.3;
  color: #90b4d6;
  border-top: 1px solid rgba(66, 165, 245, 0.2);
  padding-top: 8px;
}

/* Discipline hints, restrained to the two existing accents. */
.member-card--ai,
.member-card--architecture {
  border-color: rgba(255, 61, 154, 0.35);
  box-shadow: 0 0 16px rgba(255, 61, 154, 0.18);
}

.member-card--ai:hover,
.member-card--architecture:hover {
  box-shadow: 0 0 28px rgba(255, 61, 154, 0.38);
}

.member-card--ai .member-monogram,
.member-card--architecture .member-monogram {
  background: radial-gradient(
    circle at 30% 25%,
    rgba(255, 61, 154, 0.3),
    rgba(10, 30, 63, 0.95) 70%
  );
  border-color: rgba(255, 61, 154, 0.35);
  box-shadow:
    0 0 16px rgba(255, 61, 154, 0.22),
    inset 0 0 18px rgba(255, 61, 154, 0.08);
  text-shadow: 0 0 12px rgba(255, 61, 154, 0.8);
}

.member-card--ai .member-role,
.member-card--architecture .member-role {
  border-top-color: rgba(255, 61, 154, 0.25);
}

.member-card--client,
.member-card--backend,
.member-card--general {
  box-shadow: 0 0 16px rgba(66, 165, 245, 0.2);
}

.member-card--client:hover,
.member-card--backend:hover,
.member-card--general:hover {
  box-shadow: 0 0 28px rgba(66, 165, 245, 0.4);
}

.about-footer {
  text-align: center;
  padding-top: 4px;
}

@media (prefers-reduced-motion: reduce) {
  .member-monogram {
    transition: none;
  }
}
</style>
