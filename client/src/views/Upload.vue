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
import { computed, ref } from "vue"

import ClassificationNotifications from "../components/Upload/ClassificationNotifications.vue"
import { uploadImage } from "../services/imageService"
import { validateUploadInput } from "../utils/uploadValidation"

const fileInput = ref(null)
const files = ref([])
const city = ref("")
const country = ref("Germany")
const latitude = ref("")
const longitude = ref("")
const error = ref("")
const uploading = ref(false)
const dragActive = ref(false)
const notifications = ref([])

const selectedFileText = computed(() => {
  if (!files.value.length) return "No photos selected"
  if (files.value.length === 1) return "1 photo selected"
  return `${files.value.length} photos selected`
})

function addFiles(selectedFiles) {
  if (uploading.value) return

  const incoming = Array.from(selectedFiles || [])
  const knownFiles = new Set(
    files.value.map((file) => `${file.name}-${file.size}-${file.lastModified}`),
  )

  for (const file of incoming) {
    const key = `${file.name}-${file.size}-${file.lastModified}`
    if (!knownFiles.has(key)) {
      files.value.push(file)
      knownFiles.add(key)
    }
  }

  if (fileInput.value) {
    fileInput.value.value = ""
  }
}

function handleFileSelection(event) {
  addFiles(event.target.files)
}

function handleDrop(event) {
  dragActive.value = false
  addFiles(event.dataTransfer.files)
}

function removeFile(index) {
  files.value.splice(index, 1)
}

function dismissNotification(id) {
  notifications.value = notifications.value.filter(
    (notification) => notification.id !== id,
  )
}

function addNotification(notification) {
  notifications.value.unshift({
    id: `${Date.now()}-${Math.random()}`,
    ...notification,
  })
}

async function handleUpload() {
  error.value = ""

  try {
    validateUploadInput(files.value, city.value, country.value)
  } catch (validationError) {
    error.value = validationError.message
    return
  }

  uploading.value = true
  const failedFiles = []
  const metadata = {
    city: city.value,
    country: country.value,
    latitude: latitude.value,
    longitude: longitude.value,
  }

  for (const file of files.value) {
    try {
      const result = await uploadImage(file, metadata)
      const confidence = `${(Number(result.confidence) * 100).toFixed(1)}%`
      addNotification({
        type: "success",
        title: "Classification ready",
        filename: file.name,
        message: `${result.label} · ${confidence} confidence · ${result.status}`,
      })
    } catch (uploadError) {
      failedFiles.push(file)
      addNotification({
        type: "error",
        title: "Classification failed",
        filename: file.name,
        message: uploadError.message,
      })
    }
  }

  files.value = failedFiles
  uploading.value = false
}
</script>

<template>
  <main class="upload-page">
    <ClassificationNotifications
      :notifications="notifications"
      @dismiss="dismissNotification"
    />

    <v-card
      class="upload-card cyber-panel"
      theme="blueSkyNight"
      elevation="10"
    >
      <header class="upload-header">
        <v-avatar color="primary" size="52">
          <v-icon icon="mdi-camera-plus-outline" size="28" />
        </v-avatar>
        <div>
          <h1 class="cyber-title text-h5">Upload street photos</h1>
          <p class="text-body-2 text-medium-emphasis mt-1">
            Add location details and submit JPEG or PNG photos for classification.
          </p>
        </div>
      </header>

      <v-divider />

      <v-card-text class="upload-form">
        <v-alert v-if="error" type="error" density="compact" class="mb-5">
          {{ error }}
        </v-alert>

        <section aria-labelledby="location-heading">
          <h2 id="location-heading" class="section-title">
            <v-icon icon="mdi-map-marker-outline" size="20" />
            Location details
          </h2>

          <v-row>
            <v-col cols="12" sm="7">
              <v-text-field
                v-model="city"
                label="City"
                placeholder="e.g. Bochum"
                variant="outlined"
                :disabled="uploading"
              />
            </v-col>
            <v-col cols="12" sm="5">
              <v-text-field
                v-model="country"
                label="Country"
                variant="outlined"
                :disabled="uploading"
              />
            </v-col>
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
        </section>

        <section aria-labelledby="photos-heading">
          <h2 id="photos-heading" class="section-title">
            <v-icon icon="mdi-image-multiple-outline" size="20" />
            Photos
          </h2>

          <input
            ref="fileInput"
            class="visually-hidden"
            type="file"
            accept="image/jpeg,image/png"
            multiple
            :disabled="uploading"
            @change="handleFileSelection"
          />

          <div
            class="drop-zone"
            :class="{
              'drop-zone--active': dragActive,
              'drop-zone--disabled': uploading,
            }"
            role="button"
            tabindex="0"
            @click="fileInput?.click()"
            @keydown.enter="fileInput?.click()"
            @keydown.space.prevent="fileInput?.click()"
            @dragenter.prevent="dragActive = true"
            @dragover.prevent="dragActive = true"
            @dragleave.prevent="dragActive = false"
            @drop.prevent="handleDrop"
          >
            <v-icon icon="mdi-cloud-upload-outline" color="primary" size="44" />
            <p class="text-subtitle-1 font-weight-bold mt-2">
              Drop photos here or click to browse
            </p>
            <p class="text-body-2 text-medium-emphasis">
              JPEG or PNG · maximum 10 MB per photo
            </p>
          </div>

          <div class="selected-files-header">
            <span class="text-body-2 font-weight-medium">
              {{ selectedFileText }}
            </span>
          </div>

          <v-list v-if="files.length" class="selected-files" lines="two">
            <v-list-item
              v-for="(file, index) in files"
              :key="`${file.name}-${file.size}-${file.lastModified}`"
              prepend-icon="mdi-file-image-outline"
              :title="file.name"
              :subtitle="`${(file.size / 1024 / 1024).toFixed(2)} MB`"
            >
              <template #append>
                <v-btn
                  icon="mdi-close"
                  variant="text"
                  size="small"
                  :disabled="uploading"
                  :aria-label="`Remove ${file.name}`"
                  @click="removeFile(index)"
                />
              </template>
            </v-list-item>
          </v-list>
        </section>

        <v-btn
          variant="flat"
          size="large"
          block
          rounded="lg"
          prepend-icon="mdi-cloud-upload-outline"
          :loading="uploading"
          :disabled="uploading"
          class="submit-button cyber-button"
          @click="handleUpload"
        >
          Upload and classify
        </v-btn>
      </v-card-text>
    </v-card>
  </main>
</template>

<style scoped>
.upload-page {
  display: flex;
  width: 100%;
  min-height: calc(100dvh - 96px);
  justify-content: center;
  padding: 40px 20px;
}

.upload-card {
  width: min(820px, 100%);
  overflow: hidden;
}

.upload-card:hover {
  transform: none;
}

.upload-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 28px 32px;
}

.upload-form {
  padding: 28px 32px 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: rgb(var(--v-theme-primary));
  font-size: 1rem;
  font-weight: 700;
}

.drop-zone {
  display: grid;
  min-height: 190px;
  place-content: center;
  padding: 28px;
  border: 2px dashed rgba(var(--v-theme-primary), 0.45);
  border-radius: 14px;
  background: rgba(var(--v-theme-primary), 0.04);
  text-align: center;
  cursor: pointer;
  transition: border-color 160ms ease, background 160ms ease;
}

.drop-zone:hover,
.drop-zone:focus-visible,
.drop-zone--active {
  border-color: rgb(var(--v-theme-primary));
  outline: none;
  background: rgba(var(--v-theme-primary), 0.09);
}

.drop-zone--disabled {
  opacity: 0.6;
  pointer-events: none;
}

.selected-files-header {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.selected-files {
  margin-top: 8px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 10px;
}

.submit-button {
  margin-top: 28px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  white-space: nowrap;
}

@media (max-width: 600px) {
  .upload-page {
    min-height: auto;
    padding: 16px 12px 28px;
  }

  .upload-header {
    align-items: flex-start;
    padding: 22px 20px;
  }

  .upload-form {
    padding: 22px 20px 24px;
  }

  .drop-zone {
    min-height: 160px;
    padding: 22px 16px;
  }
}
</style>
