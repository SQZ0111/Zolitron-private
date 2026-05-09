<script setup>
import Navbar from './components/Navigation/Navbar.vue';
</script>

<template>
  <v-app>
    <Navbar />
    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>


<style src="./styles/global.css"></style>