<script setup lang="ts">
  import { ref } from 'vue'

  const currentModel = ref(0)
  const models = ref([
    {
      provider: 'OpenAI',
      name: 'GPT-5',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-5 mini',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-5 nano',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-5 pro',
    },
    {
      provider: 'OpenAI',
      name: 'GPT-4.1',
    },
    {
      provider: 'Claude',
      name: 'Sonnet 4.5',
    },
    {
      provider: 'Claude',
      name: 'Haiku 4.5',
    },
    {
      provider: 'Claude',
      name: 'Opus 4.1',
    },
  ])

  function selectModel(model: number) {
    currentModel.value = model
  }
</script>

<template>
  <v-menu>
    <template #activator="{ props }">
      <v-chip v-bind="props" color="grey-darken-2">
        {{ models[currentModel]?.name || 'Model' }}
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
