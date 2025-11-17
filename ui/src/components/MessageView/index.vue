<script setup lang="ts">
  import { useActiveChatStore } from '@/stores/activeChat.ts'

  const activeChatStore = useActiveChatStore()
</script>

<template>
  <div class="message-view">
    <template v-for="message in activeChatStore.messages" :key="message.id">
      <HumanMessage v-if="message.type == 'human'" :message="message" />
      <AIMessage v-else-if="message.type == 'ai'" :message="message" />
    </template>
  </div>
</template>

<style scoped>
.message-view {
  padding-bottom: 12rem;
}
</style>
