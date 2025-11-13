import type { AIMessage, Message, StreamResponse } from '@/types/chat'
import { defineStore } from 'pinia'
import { v4 } from 'uuid'
import { computed, reactive, ref } from 'vue'

export const useActiveChatStore = defineStore('activeChat', () => {
  let activeChat: WebSocket
  const connectionStatus = ref<'connected' | 'loading' | 'not_connected' | 'failed'>('not_connected')
  const streamingStatus = ref<'stand_by' | 'streaming' | null>(null)
  const selectedModel = ref<string>('gpt-4o')
  const errorMessage = ref<string>('')

  const isConnected = computed(() => connectionStatus.value === 'connected')

  const messages = reactive(new Map<string, Message>())

  async function startChat () {
    // Close existing connection if any
    if (activeChat && (activeChat.readyState === WebSocket.OPEN || activeChat.readyState === WebSocket.CONNECTING)) {
      activeChat.close()
    }
    
    activeChat = new WebSocket('ws://localhost:8000/chat')
    connectionStatus.value = 'loading'
    streamingStatus.value = null
    errorMessage.value = ''

    activeChat.addEventListener('error', () => {
      connectionStatus.value = 'failed'
      streamingStatus.value = null
      errorMessage.value = 'Failed to connect to the server.'

      const id = v4()

      messages.set(id, {
        id,
        type: 'system',
        level: 'error',
        content: 'Failed to connect.',
      })
    })

    activeChat.addEventListener('open', () => {
      // Send initialization message with selected model
      activeChat.send(JSON.stringify({
        type: 'init',
        model: selectedModel.value
      }))

      const id = v4()

      messages.set(id, {
        id,
        type: 'system',
        level: 'info',
        content: 'Chat connected',
      })
    })

    activeChat.addEventListener('close', () => {
      connectionStatus.value = 'not_connected'
      streamingStatus.value = null

      const id = v4()

      messages.set(id, {
        id,
        type: 'system',
        level: 'info',
        content: 'Chat disconnected.',
      })
    })

    activeChat.addEventListener('message', (event: MessageEvent) => {
      const streamResponse = JSON.parse(event.data) as StreamResponse

      streamingStatus.value = streamResponse.type === 'ready' ? 'stand_by' : 'streaming'

      switch (streamResponse.type) {
        case 'ready': {
          connectionStatus.value = 'connected'
          errorMessage.value = ''
          break
        }

        case 'error': {
          connectionStatus.value = 'failed'
          streamingStatus.value = null
          errorMessage.value = streamResponse.content
          
          const id = v4()
          messages.set(id, {
            id,
            type: 'system',
            level: 'error',
            content: streamResponse.content,
          })
          break
        }

        case 'human': {
          messages.set(streamResponse.id, {
            id: streamResponse.id,
            type: 'human',
            content: streamResponse.content,
          })
          break
        }

        case 'token': {
          let newMessage = messages.get(streamResponse.id)

          if (!newMessage) {
            newMessage = {
              id: streamResponse.id,
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
          let newMessage = messages.get(streamResponse.id) as AIMessage

          if (!newMessage) {
            newMessage = {
              id: streamResponse.id,
              type: 'ai',
              content: '',
              tool_calls: {},
            }
          }

          newMessage.tool_calls[streamResponse.tool_id] = {
            name: streamResponse.name,
            input: streamResponse.input,
            id: streamResponse.tool_id,
          }

          messages.set(streamResponse.id, newMessage)
          break
        }

        case 'tool_end': {
          let newMessage = messages.get(streamResponse.id) as AIMessage

          if (!newMessage) {
            newMessage = {
              id: streamResponse.id,
              type: 'ai',
              content: '',
              tool_calls: {},
            }
          }

          newMessage.tool_calls[streamResponse.tool_id] = {
            ...newMessage.tool_calls[streamResponse.tool_id],
            name: streamResponse.name,
            output: streamResponse.output,
            id: streamResponse.id,
          }

          messages.set(streamResponse.id, newMessage)
          break
        }

        case 'done': {
          streamingStatus.value = 'stand_by'
          break
        }
      }
    })
  }

  async function sendPrompt (message: string) {
    activeChat.send(message)
  }

  const getMessages = computed(() => {
    return [...messages.values()]
  })

  function setModel (model: string) {
    selectedModel.value = model
  }

  return {
    messages: getMessages,
    connectionStatus,
    isConnected,
    streamingStatus,
    errorMessage,
    selectedModel,
    startChat,
    sendPrompt,
    setModel,
  }
})
