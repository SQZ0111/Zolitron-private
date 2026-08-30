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
import { ref, watch } from "vue"

import { searchGermanLocation } from "../../services/mapService"

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  currentCity: {
    type: String,
    default: "Bochum",
  },
})

const emit = defineEmits(["update:modelValue", "location-found"])

const query = ref("Bochum")
const searching = ref(false)
const error = ref("")

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      query.value = props.currentCity
      error.value = ""
    }
  },
)

function closeDialog() {
  if (!searching.value) {
    emit("update:modelValue", false)
  }
}

async function submitSearch() {
  if (searching.value) return

  searching.value = true
  error.value = ""
  try {
    const location = await searchGermanLocation(query.value)
    emit("location-found", location)
    emit("update:modelValue", false)
  } catch (searchError) {
    error.value = searchError.message
  } finally {
    searching.value = false
  }
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    max-width="460"
    :persistent="searching"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card class="city-dialog cyber-panel" theme="blueSkyNight">
      <v-card-title class="cyber-title">Change city</v-card-title>
      <v-card-subtitle>
        Bochum is the current focus of the MVP.
      </v-card-subtitle>

      <form @submit.prevent="submitSearch">
        <v-card-text>
          <v-text-field
            v-model="query"
            label="German city"
            prepend-inner-icon="mdi-map-search-outline"
            variant="outlined"
            autofocus
            :disabled="searching"
          />
          <p v-if="error" class="search-error" role="alert">{{ error }}</p>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" :disabled="searching" @click="closeDialog">
            Cancel
          </v-btn>
          <v-btn
            variant="flat"
            rounded="lg"
            type="submit"
            class="cyber-button"
            :loading="searching"
          >
            Show city
          </v-btn>
        </v-card-actions>
      </form>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.city-dialog:hover {
  transform: none;
}

.search-error {
  margin: -12px 4px 0;
  color: rgb(var(--v-theme-error));
  font-size: 0.78rem;
}
</style>
