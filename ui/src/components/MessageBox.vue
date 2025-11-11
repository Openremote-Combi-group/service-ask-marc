<script setup lang="ts">
  import type { Message } from '@/types/chat.ts'

  defineProps<{
    message: Message
  }>()
</script>

<template>
  <div v-if="message.type == 'human'" class="d-flex ga-4 my-8 justify-end">
    <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
      {{ message.content }}
    </v-sheet>
  </div>
  <div v-else-if="message.type == 'ai'" class="d-flex ga-4">
    <v-avatar class="ma-2" :image="`/images/OpenRemote/logo.png`" size="small" />
    <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
      <v-expansion-panels v-if="Object.keys(message.tool_calls).length > 0" class="mb-4">
        <v-expansion-panel v-for="tool_call in message.tool_calls" :key="tool_call.id">
          <v-expansion-panel-title><code>Tool called {{ tool_call.name }}</code></v-expansion-panel-title>
          <v-expansion-panel-text v-if="tool_call.output">
            <h5>Response</h5>
            <p>{{ tool_call.output }}</p>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
      {{ message.content }}
    </v-sheet>
  </div>
</template>

<style scoped>

</style>
