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
    <v-card class="city-dialog">
      <v-card-title>Change city</v-card-title>
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
          <v-btn :disabled="searching" @click="closeDialog">Cancel</v-btn>
          <v-btn color="primary" type="submit" :loading="searching">
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
