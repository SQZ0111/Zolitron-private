<script setup>
// TODO: split into form component
// TODO: functions with computed
import { ref } from 'vue'

const form = ref({
  title: '',
  description: '',
  level: 'Medium'
})

const levels = ['Low', 'Medium', 'High', 'Critical']


const submitReport = () => {
  console.log(`Bug report ${form.value}`)
  form.value = { title: '', description: '', level: 'Medium' }
}
</script>
<template>
  <v-row justify="center">
    <v-col cols="12" md="8">
      <v-card class="pa-6 cyber-panel" theme="blueSkyNight">
        <v-card-title class="cyber-title text-h4 text-center mt-4 mb-4">
          Report a Bug
        </v-card-title>
        <v-card-text class="d-flex justify-center">
          <v-form class="report-form" @submit.prevent="submitReport">
            <v-text-field
              v-model="form.title"
              label="Bug Title"
              required
              variant="outlined"
            ></v-text-field>

            <v-textarea
              v-model="form.description"
              label="Description"
              rows="4"
              variant="outlined"
            ></v-textarea>

            <v-select
              v-model="form.level"
              :items="levels"
              label="Level"
              variant="outlined"
            ></v-select>

            <v-btn
              type="submit"
              variant="flat"
              rounded="lg"
              block
              class="cyber-button mt-2"
            >
              Submit Report
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>


<style scoped>
.v-card {
  border-radius: 12px;
}

.report-form {
  width: 100%;
  max-width: 520px;
}
</style>