<script setup lang="ts">
  defineProps<{
    role: 'user' | 'system'
    message: string
  }>()
</script>

<template>
  <div v-if="role == 'user'" class="d-flex ga-4 justify-end">
    <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
      {{ message }}
    </v-sheet>
  </div>
  <div v-else class="d-flex ga-4">
    <v-avatar class="ma-2" :image="`/images/OpenRemote/logo.png`" size="small"></v-avatar>
    <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
      {{ message }}
    </v-sheet>
  </div>
</template>

<style scoped>

</style>
