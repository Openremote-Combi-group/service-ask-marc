<script setup lang="ts">
  import type { HumanMessage } from '@/types/chat.ts'

  defineProps<{ message: HumanMessage }>()
</script>

<template>
  <div class="d-flex my-8 justify-end">
    <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
      {{ message.content }}
    </v-sheet>
  </div>
</template>

<style scoped>

</style>
