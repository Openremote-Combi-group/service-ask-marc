<script setup lang="ts">
  import { ref } from 'vue'
  import { useActiveChatStore } from '@/stores/activeChat.ts'

  const activeChatStore = useActiveChatStore()

  const prompt = ref('')

  async function sendPrompt () {
    await activeChatStore.sendPrompt(prompt.value)

    prompt.value = ''
  }
</script>

<template>
  <div class="d-flex flex-column ga-2">
    <v-alert
      v-if="activeChatStore.errorMessage"
      type="error"
      density="compact"
      variant="tonal"
      closable
      class="mb-2"
    >
      {{ activeChatStore.errorMessage }}
    </v-alert>
    <div class="d-flex ga-4 justify-center">
      <v-textarea
        v-model="prompt"
        auto-grow
        clearable
        counter
        :disabled="!activeChatStore.isConnected"
        :loading="activeChatStore.connectionStatus === 'loading'"
        placeholder="Type your prompt..."
        rows="1"
        variant="solo"
      />
      <v-btn
        color="#4e9d2d"
        :disabled="!activeChatStore.isConnected"
        :icon="activeChatStore.streamingStatus === 'streaming' ? 'mdi-square' : 'mdi-send'"
        @click="sendPrompt()"
      />
    </div>
  </div>
</template>

<style scoped>

</style>
