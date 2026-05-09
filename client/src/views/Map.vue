<template>
  <v-row>
    <v-col cols="12">
      <v-card class="pa-6">
        <v-card-title class="text-h4">Cats are superior to dogs</v-card-title>
        <v-card-text>
          <div class="placeholder">
            <v-icon size="64" color="grey">mdi-map</v-icon>
            <p class="text-subtitle-1 mt-4">We will use Leaflet or an other map lib</p>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<style scoped>
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  border-radius: 8px;
}
</style>