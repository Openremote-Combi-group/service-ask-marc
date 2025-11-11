import type { Message, StreamResponse } from '@/types/chat'
import { defineStore } from 'pinia'
import { computed, reactive } from 'vue'

export const useActiveChatStore = defineStore('activeChat', () => {
  let activeChat: WebSocket

  const messages = reactive(new Map<string, Message>())

  async function startChat () {
    activeChat = new WebSocket('ws://localhost:8000/chat')

    activeChat.addEventListener('open', () => {
      console.log('chat opened')
    })

    activeChat.addEventListener('message', (event: MessageEvent) => {
      const streamResponse = JSON.parse(event.data) as StreamResponse

      switch (streamResponse.type) {
        case 'human': {
          messages.set(streamResponse.id, {
            id: streamResponse.id,
            name: null,
            type: 'human',
            content: streamResponse.content,
            tool_calls: {},
          })
          break
        }

        case 'token': {
          let newMessage = messages.get(streamResponse.id)

          if (!newMessage) {
            newMessage = {
              id: streamResponse.id,
              name: null,
              type: 'ai',
              content: '',
              tool_calls: {},
            }
          }

          newMessage.content += streamResponse.content

          messages.set(streamResponse.id, newMessage)

          break
        }

        case 'tool_start': {
          let newMessage = messages.get(streamResponse.id)

          if (!newMessage) {
            newMessage = {
              id: streamResponse.id,
              name: null,
              type: 'ai',
              content: '',
              tool_calls: {},
            }
          }

          newMessage.tool_calls[streamResponse.tool_id] = {
            name: streamResponse.name,
            args: streamResponse.input,
            id: streamResponse.tool_id,
          }

          messages.set(streamResponse.id, newMessage)
          break
        }

        case 'tool_end': {
          let newMessage = messages.get(streamResponse.id)

          if (!newMessage) {
            newMessage = {
              id: streamResponse.id,
              name: null,
              type: 'ai',
              content: '',
              tool_calls: {},
            }
          }

          newMessage.tool_calls[streamResponse.tool_id] = {
            name: streamResponse.name,
            output: streamResponse.output,
            id: streamResponse.tool_id,
          }

          messages.set(streamResponse.id, newMessage)
          break
        }
      }
      // for (const message of data) {
      //   messages.set(message.id, message)
      //   console.log(message)
      // }
    })
  }

  async function sendPrompt (message: string) {
    activeChat.send(message)
  }

  const getMessages = computed(() => {
    return [...messages.values()]
  })

  const getLastMessage = computed(() => {
    return [...messages.values()].pop()
  })

  return {
    messages: getMessages,
    startChat,
    sendPrompt,
  }
})
