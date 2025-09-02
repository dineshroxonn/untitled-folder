import React, { useState, useEffect, useRef } from 'react'
import { Car, MessageCircle, AlertCircle, Loader2, Send } from 'lucide-react'
import { clsx } from 'clsx'
import './App.css'

interface Message {
  id: string
  type: 'user' | 'agent' | 'error'
  content: string
  timestamp: Date
}

interface AgentStatus {
  available: boolean
  agent_url: string
  status_code?: number
  error?: string
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Check agent status on component mount
  useEffect(() => {
    checkAgentStatus()
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const checkAgentStatus = async () => {
    try {
      const response = await fetch('/agent-status')
      const status: AgentStatus = await response.json()
      setAgentStatus(status)
    } catch (error) {
      setAgentStatus({
        available: false,
        agent_url: 'unknown',
        error: 'Failed to check agent status'
      })
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/diagnose', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage.content }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response stream available')

      let agentMessageId = Date.now().toString() + '_agent'
      let agentMessage: Message = {
        id: agentMessageId,
        type: 'agent',
        content: '',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, agentMessage])

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = new TextDecoder().decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.text) {
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === agentMessageId 
                      ? { ...msg, content: msg.content + data.text }
                      : msg
                  )
                )
              } else if (data.error) {
                const errorMessage: Message = {
                  id: Date.now().toString() + '_error',
                  type: 'error',
                  content: `Error: ${data.error}`,
                  timestamp: new Date()
                }
                setMessages(prev => [...prev, errorMessage])
                break
              } else if (data.status === 'complete') {
                break
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', line)
            }
          }
        }
      }
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now().toString() + '_error',
        type: 'error',
        content: `Failed to communicate with agent: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-automotive-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-automotive-600 rounded-lg">
                <Car className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Car Diagnostic</h1>
                <p className="text-sm text-gray-600">Virtual Mechanic Assistant</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {agentStatus && (
                <>
                  <div className={`w-2 h-2 rounded-full ${
                    agentStatus.available ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className={`text-sm font-medium ${
                    agentStatus.available ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {agentStatus.available ? 'Agent Online' : 'Agent Offline'}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Instructions Panel */}
          <div className="lg:col-span-1">
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2 text-automotive-600" />
                How to Use
              </h2>
              <div className="space-y-3 text-sm text-gray-600">
                <p>🚗 <strong>Provide car details:</strong> Include your car's make, model, and year.</p>
                <p>🔧 <strong>Share trouble codes:</strong> Enter any OBD-II diagnostic codes (e.g., P0171, P0174).</p>
                <p>💬 <strong>Get diagnosis:</strong> The AI will respond as your car and explain the issues.</p>
              </div>
              
              <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <h3 className="font-medium text-amber-800 mb-2">Example:</h3>
                <p className="text-sm text-amber-700">
                  "I have a 2015 Ford Focus and I'm seeing codes P0171 and P0174. What's going on?"
                </p>
              </div>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <div className="card flex flex-col h-[600px]">
              {/* Messages */}
              <div className="flex-1 p-4 overflow-y-auto space-y-4 messages-container">
                {messages.length === 0 ? (
                  <div className="text-center py-12">
                    <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Start a conversation with your AI mechanic</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={clsx(
                        "flex message-fade-in",
                        message.type === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      <div
                        className={clsx(
                          "max-w-[80%] rounded-lg px-4 py-2",
                          {
                            'bg-automotive-600 text-white': message.type === 'user',
                            'bg-red-100 text-red-800 border border-red-200': message.type === 'error',
                            'bg-gray-100 text-gray-900': message.type === 'agent'
                          }
                        )}
                      >
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        <p className={clsx("text-xs mt-1 opacity-70")}>
                          {formatTime(message.timestamp)}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-lg px-4 py-2 flex items-center space-x-2 typing-indicator">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span className="text-sm text-gray-600">AI is diagnosing...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t border-gray-200 p-4">
                <div className="flex space-x-3">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Describe your car and any trouble codes you're seeing..."
                    className="input-field resize-none"
                    rows={2}
                    disabled={isLoading || !agentStatus?.available}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!input.trim() || isLoading || !agentStatus?.available}
                    className="btn-primary flex items-center space-x-2 px-6"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                    <span>Send</span>
                  </button>
                </div>
                {!agentStatus?.available && (
                  <p className="text-red-600 text-sm mt-2 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    Diagnostic agent is not available. Please check the connection.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
