<script setup>
import { ref } from 'vue'

import ImagePipelineControl from './ImagePipelineControl.vue'

const navigationOpen = ref(false)

const tabs = [
  { name: 'Home', route: '/' },
  { name: 'About', route: '/about' },
  { name: 'Map', route: '/map' },
  { name: 'Report Bug', route: '/report' },
  { name: 'Uploads', route: '/uploads' }
]
</script>

<template>
  <v-app-bar app color="primary" dark>
    <v-toolbar-title class="brand-title">Zolitron2</v-toolbar-title>
    <ImagePipelineControl />
    <v-spacer></v-spacer>
    <v-tabs class="d-none d-md-flex" centered>
      <v-tab v-for="tab in tabs" :key="tab.route" :to="tab.route">
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
          v-for="tab in tabs"
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

.v-tab {
  text-transform: none;
  letter-spacing: 0.5px;
}
</style>
