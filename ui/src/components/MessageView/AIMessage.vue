<script setup lang="ts">
  import type { AIMessage } from '@/types/chat.ts'
  import VueMarkdown from 'vue-markdown-render'

  defineProps<{ message: AIMessage }>()
</script>

<template>
  <div class="d-flex ga-4 my-8">
    <v-avatar class="ma-2" :image="`/images/OpenRemote/logo.png`" size="small" />
    <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
      <v-expansion-panels v-if="Object.keys(message.tool_calls).length > 0" class="mb-4">
        <v-expansion-panel v-for="tool_call in message.tool_calls" :key="tool_call.id">
          <v-expansion-panel-title><code>Tool call: {{ tool_call.name }}</code></v-expansion-panel-title>
          <v-expansion-panel-text>
            <template v-if="tool_call.input && Object.keys(tool_call.input).length > 0">
              <h5>Input</h5>
              <p>{{ tool_call.input }}</p>
            </template>
            <template v-if="tool_call.output">
              <h5>Response</h5>
              <p>{{ tool_call.output }}</p>
            </template>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
      <vue-markdown class="markdown-content" :options="{ breaks: true }" :source="message.content" />
    </v-sheet>
  </div>
</template>

<style scoped>

</style>
