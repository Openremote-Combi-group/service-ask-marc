<script setup lang="ts">
  import { ref } from 'vue'

  defineEmits(['send'])

  const prompt = ref('can you ask marc if life has any meaning?')
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
    <v-btn color="#4e9d2d" icon="mdi-send" @click="$emit('send', prompt)" />
  </div>
</template>

<style scoped>

</style>
