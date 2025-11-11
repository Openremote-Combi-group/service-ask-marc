<script setup lang="ts">
  import { useActiveChatStore } from '@/stores/activeChat.ts'

  const activeChatStore = useActiveChatStore()

</script>

<template>
  <MessageBox v-for="(message, index) in activeChatStore.messages" :key="index" :message="message" />
</template>

<style scoped>

</style>
