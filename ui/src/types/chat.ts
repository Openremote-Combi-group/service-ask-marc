export type ToolCall = {
  name: string
  args?: Record<string, any>
  output?: any
  id: string
}

export type Message = {
  id: string
  type: 'human' | 'system' | 'ai'
  name: string | null
  content: string
  tool_calls: Record<string, ToolCall>
}

export type StreamResponse = StreamResponseHumanMessage | StreamResponseToken | StreamResponseToolStart | StreamResponseToolEnd

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
