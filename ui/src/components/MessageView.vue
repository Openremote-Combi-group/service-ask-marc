<script setup lang="ts">
  const messages = [
    {
      role: 'user',
      message: 'Can you list all the assets in the Smart City?',
    },
    {
      role: 'assistant',
      message: 'Here are all the assets in the Smart City:',
    },
  ]
</script>

<template>
  <MessageBox v-for="(message, index) in messages" :key="index" :message="message.message" :role="message.role" />
</template>

<style scoped>

</style>
