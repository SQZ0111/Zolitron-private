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