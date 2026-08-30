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

<script setup>
import { ref } from 'vue'

import ImagePipelineControl from './ImagePipelineControl.vue'
import { navigationLinks } from '../../router/navigation'

const navigationOpen = ref(false)
</script>

<template>
  <v-app-bar
    app
    class="main-navbar"
    color="primary"
    dark
    height="64"
    elevation="4"
  >
    <v-toolbar-title class="cyber-title brand-title">Zolitron2</v-toolbar-title>
    <ImagePipelineControl />
    <v-spacer></v-spacer>
    <v-tabs class="d-none d-md-flex" centered>
      <v-tab v-for="tab in navigationLinks" :key="tab.route" :to="tab.route">
        {{ tab.name }}
      </v-tab>
    </v-tabs>

    <v-menu
      v-model="navigationOpen"
      location="bottom end"
      class="d-md-none"
    >
      <template #activator="{ props }">
        <v-btn
          v-bind="props"
          icon="mdi-menu"
          aria-label="Open navigation"
          class="d-md-none"
        />
      </template>
      <v-list nav>
        <v-list-item
          v-for="tab in navigationLinks"
          :key="tab.route"
          :to="tab.route"
          :title="tab.name"
          @click="navigationOpen = false"
        />
      </v-list>
    </v-menu>
  </v-app-bar>
</template>



<style scoped>
.brand-title {
  flex: 0 0 auto;
}

.main-navbar {
  position: fixed !important;
  top: 0 !important;
  right: 0 !important;
  left: 0 !important;
  z-index: 2500 !important;
}

.v-tab {
  text-transform: none;
  letter-spacing: 0.5px;
}
</style>
