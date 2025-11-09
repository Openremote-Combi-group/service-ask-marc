<template>
  <v-app class="bg-transparent">
    <v-layout>
      <v-main>
        <v-container class="h-100">
          <v-row class="h-100">
            <v-col class="d-flex flex-column justify-space-between">
              <div>
                <div class="d-flex ga-4 justify-end">
                  <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
                    Lorum Ipsum
                  </v-sheet>
                </div>
                <div class="d-flex ga-4">
                  <v-avatar class="ma-2" :image="`/images/OpenRemote/logo.png`" size="small"></v-avatar>
                  <v-sheet class="rounded-lg pa-4 mr-16 mb-4" elevation="1" max-width="800">
                    Lorum Ipsum
                  </v-sheet>
                </div>
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
