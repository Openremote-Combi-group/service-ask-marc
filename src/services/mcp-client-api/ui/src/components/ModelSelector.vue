<script setup lang="ts">
  import { computed, ref, watch } from 'vue'
  import { storeToRefs } from 'pinia'
  import { useActiveChatStore } from '@/stores/activeChat.ts'

  const activeChatStore = useActiveChatStore()
  const { selectedModel } = storeToRefs(activeChatStore)

  const models = ref([
    {
      provider: 'OpenRemote',
      name: 'Local (Ollama Llama3)',
      id: 'ollama-llama3',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-4o',
      id: 'gpt-4o',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-4o Mini',
      id: 'gpt-4o-mini',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-4 Turbo',
      id: 'gpt-4-turbo',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-4',
      id: 'gpt-4',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-3.5 Turbo',
      id: 'gpt-3.5-turbo',
    },
    {
      provider: 'Claude',
      name: 'Claude 3.5 Sonnet',
      id: 'claude-3-5-sonnet-20241022',
    },
    {
      provider: 'Claude',
      name: 'Claude 3.5 Haiku',
      id: 'claude-3-5-haiku-20241022',
    },
    {
      provider: 'Claude',
      name: 'Claude 3 Opus',
      id: 'claude-3-opus-20240229',
    },
  ])

  const currentModel = ref<number>(0)

  function syncModelIndex(targetModel: string) {
    const index = models.value.findIndex((item) => item.id === targetModel)
    currentModel.value = index >= 0 ? index : 0
  }

  syncModelIndex(selectedModel.value)

  watch(selectedModel, (modelId) => {
    syncModelIndex(modelId ?? '')
  })

  const currentModelName = computed(() => {
    const index = currentModel.value
    const selected = models.value[index]
    return selected ? selected.name : 'Unknown'
  })

  async function selectModel (index: number) {
    const selected = models.value[index]
    if (!selected) {
      return
    }

    currentModel.value = index
    activeChatStore.setModel(selected.id)

    // Restart chat with new model
    await activeChatStore.startChat()
  }
</script>

<template>
  <v-menu>
    <template #activator="{ props }">
      <v-chip v-bind="props" color="grey-darken-2">
        Model: {{ currentModelName }}
      </v-chip>
    </template>
    <v-list>
      <v-list-item
        v-for="(item, index) in models"
        :key="index"
        :value="index"
        @click="selectModel(index)"
      >
        <template #prepend>
          <v-avatar class="pa-1" :image="`/images/${item.provider}/logo_light.svg`" size="small" />
        </template>
        <v-list-item-title>{{ item.name }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<style scoped>

</style>
