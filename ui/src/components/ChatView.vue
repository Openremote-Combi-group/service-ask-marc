<script setup lang="ts">
  import { useActiveChatStore } from '@/stores/activeChat.ts'

  const activeChatStore = useActiveChatStore()

  activeChatStore.startChat()
</script>

<template>
  <v-container class="h-100">
    <v-row class="h-100">
      <v-col class="d-flex flex-column justify-space-between">
        <MessageView />
        <div class="d-flex justify-center position-fixed bottom-0 w-100 left-0 pb-4">
          <div class="prompt">
            <PromptBox />
            <div class="d-flex">
              <ModelSelector />
            </div>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.prompt {
  width: 100%;
  max-width: 600px;
}
</style>
