<script setup lang="ts">
  import { useActiveChatStore } from '@/stores/activeChat.ts'

  const activeChatStore = useActiveChatStore()

  await activeChatStore.startChat()
</script>

<template>
  <v-container class="h-100">
    <v-row class="h-100">
      <v-col class="d-flex flex-column justify-space-between">
        <div>
          <MessageView />
        </div>
        <div class="d-flex flex-column">
          <PromptBox @send="activeChatStore.sendPrompt" />
          <div class="d-flex">
            <ModelSelector />
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>

</style>
