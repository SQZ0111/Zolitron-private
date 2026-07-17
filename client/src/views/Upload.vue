<script setup>
import { ref } from "vue"

import { uploadImage } from "../services/imageService"
import { validateUploadInput } from "../utils/uploadValidation"

const files = ref([])
const city = ref("")
const country = ref("Germany")
const latitude = ref("")
const longitude = ref("")
const error = ref("")
const uploading = ref(false)
const uploadedMarkers = ref([])

const handleUpload = async () => {
  error.value = ""

  try {
    validateUploadInput(files.value, city.value, country.value)
    uploading.value = true

    const metadata = {
      city: city.value,
      country: country.value,
      latitude: latitude.value,
      longitude: longitude.value,
    }

    for (const file of files.value) {
      const marker = await uploadImage(file, metadata)
      uploadedMarkers.value.push({
        ...marker,
        filename: file.name,
      })
    }

    files.value = []
  } catch (uploadError) {
    error.value = uploadError.message
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <v-row>
    <v-col cols="12" md="8" offset-md="2">
      <v-card class="pa-6">
        <v-card-title class="text-h4">Garbage Site Upload</v-card-title>
        <v-card-text>
          <v-alert v-if="error" type="error" class="mb-4">
            {{ error }}
          </v-alert>

          <v-text-field
            v-model="city"
            label="City"
            variant="outlined"
            :disabled="uploading"
          />
          <v-text-field
            v-model="country"
            label="Country"
            variant="outlined"
            :disabled="uploading"
          />

          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="latitude"
                label="Latitude (optional)"
                type="number"
                variant="outlined"
                :disabled="uploading"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="longitude"
                label="Longitude (optional)"
                type="number"
                variant="outlined"
                :disabled="uploading"
              />
            </v-col>
          </v-row>

          <v-file-input
            v-model="files"
            label="Select JPEG or PNG images"
            accept="image/jpeg,image/png"
            multiple
            variant="outlined"
            prepend-icon="mdi-cloud-upload"
            :disabled="uploading"
          />

          <v-btn
            color="primary"
            :loading="uploading"
            :disabled="uploading"
            @click="handleUpload"
          >
            Upload and classify
          </v-btn>

          <v-divider class="my-4" />

          <div v-if="uploadedMarkers.length">
            <h3 class="text-h6 mb-3">Classified images</h3>
            <v-list>
              <v-list-item
                v-for="marker in uploadedMarkers"
                :key="`${marker.image_id}-${marker.filename}`"
              >
                <v-list-item-title>
                  {{ marker.filename }} — {{ marker.label }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  Confidence: {{ marker.confidence.toFixed(2) }} |
                  Status: {{ marker.status }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<style scoped>
.v-card {
  border-radius: 12px;
}
</style>
