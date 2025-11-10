<template>
  <v-app class="bg-transparent">
    <v-layout>
      <v-main>
        <v-container class="h-100">
          <v-row class="h-100">
            <v-col class="d-flex flex-column justify-space-between">
              <div>
                <MessageView />
              </div>
              <div class="d-flex flex-column">
                <PromptBox />
                <div class="d-flex">
                  <ModelSelector />
                </div>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-main>
    </v-layout>
  </v-app>
</template>

<script lang="ts" setup>
  //
</script>
