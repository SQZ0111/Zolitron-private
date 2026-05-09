<script setup>
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
    <v-toolbar-title>Zolitron2</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-tabs centered>
      <v-tab v-for="tab in tabs" :key="tab.route" :to="tab.route">
        {{ tab.name }}
      </v-tab>
    </v-tabs>
  </v-app-bar>
</template>



<style scoped>
.v-tab {
  text-transform: none;
  letter-spacing: 0.5px;
}
</style>