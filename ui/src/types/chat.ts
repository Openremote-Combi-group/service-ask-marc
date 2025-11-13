export type ToolCall = {
  name: string
  input?: Record<string, any>
  output?: any
  id: string
}

export type Message = AIMessage | HumanMessage | SystemMessage

export type AIMessage = {
  id: string
  type: 'ai'
  content: string
  tool_calls: Record<string, ToolCall>
}

export type HumanMessage = {
  id: string
  type: 'human'
  content: string
}

export type SystemMessage = {
  id: string
  type: 'system'
  level: 'info' | 'error'
  content: string
}

export type StreamResponse = StreamResponseReady | StreamResponseError | StreamResponseHumanMessage | StreamResponseToken | StreamResponseToolStart | StreamResponseToolEnd | StreamResponseDone

export type StreamResponseReady = {
  type: 'ready'
}

export type StreamResponseError = {
  type: 'error'
  content: string
}

export type StreamResponseHumanMessage = {
  type: 'human'
  id: string
  content: string
}

export type StreamResponseToken = {
  id: string
  type: 'token'
  content: string
}

export type StreamResponseToolStart = {
  id: string
  tool_id: string
  type: 'tool_start'
  name: string
  input: Record<string, any>
}

export type StreamResponseToolEnd = {
  id: string
  tool_id: string
  type: 'tool_end'
  name: string
  output: any
}

export type StreamResponseDone = {
  id: string
  type: 'done'
  content: string
}
