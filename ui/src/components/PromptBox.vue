<script setup lang="ts">
  import {ref} from 'vue';

  const prompt = ref("")
</script>

<template>
  <div class="d-flex ga-4">
    <v-textarea
      v-model="prompt"
      clearable
      counter
      placeholder="Type your prompt..."
      rows="1"
      variant="solo"
    />
    <v-btn color="#4e9d2d" icon="mdi-send" @click="sendPrompt()" />
  </div>
</template>

<style scoped>

</style>
