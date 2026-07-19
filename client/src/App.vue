<script setup>
import Navbar from './components/Navigation/Navbar.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
</script>

<template>
  <v-app>
    <Navbar />
    <v-main>
      <v-container
        fluid
        :class="{ 'app-container--map': route.path === '/map' }"
      >
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>


<style src="./styles/global.css"></style>

<style scoped>
.app-container--map {
  display: block;
  align-self: stretch;
  max-width: none;
  padding: 0;
}
</style>
