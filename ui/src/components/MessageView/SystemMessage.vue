<script setup lang="ts">
  import type { SystemMessage } from '@/types/chat.ts'

  defineProps<{ message: SystemMessage }>()
</script>

<template>
  <div class="d-flex my-8 justify-center text-grey-darken-1">
    <p>{{ message.content }}</p>
  </div>
</template>

<style scoped>

</style>
