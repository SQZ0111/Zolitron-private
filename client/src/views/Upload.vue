<script setup>
import { ref } from 'vue'

const files = ref(undefined)
const error = ref('')
const uploadedFiles = ref([])

const handleUpload = (newFiles) => {
    try {
        if (!newFiles || !newFiles.length) {
            throw new Error('Please select at least one file')
        }

        uploadedFiles.value = [...uploadedFiles.value, ...newFiles]
        console.log(`${newFiles.length} file(s) uploaded successfully`)
        files.value = undefined
        error.value = ''
    } catch (err) {
        error.value = err.message
        console.error(err)
    }
}

</script>


<template>
    <v-row>
        <v-col cols="12" md="8" offset-md="2">
            <v-card class="pa-6">
                <v-card-title class="text-h4">Garbage Site Upload</v-card-title>
                <v-card-text>
                    <v-alert v-if="error" type="error" class="mb-4">{{ error }}</v-alert> 

                    <v-file-input class="mt-4" v-model="files" label="Select files" multiple variant="outlined"
                        prepend-icon="mdi-cloud-upload" @update:model-value="handleUpload">
                    </v-file-input>
                    
                    <v-divider class="my-4"></v-divider>

                    <div v-if="uploadedFiles.length">
                        <h3 class="text-h6 mb-3">Uploaded Files</h3>
                        <v-list>
                            <v-list-item v-for="(file, index) in uploadedFiles" :key="index">
                                <v-list-item-title>{{ file.name }}</v-list-item-title>
                                <v-list-item-subtitle>{{ (file.size / 1024).toFixed(2) }} KB</v-list-item-subtitle>
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