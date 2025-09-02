import React, { useState } from 'react';
import { 
  MessageCircle, 
  Loader2, 
  Send, 
  AlertCircle, 
  Sparkles,
  Mic,
  Paperclip,
  MoreHorizontal,
  Maximize2,
  Minimize2
} from 'lucide-react';
import type { Message } from '../types';
import { ChatMessage } from './ChatMessage';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { clsx } from 'clsx';

interface ChatInterfaceProps {
  messages: Message[];
  input: string;
  setInput: (val: string) => void;
  isLoading: boolean;
  agentAvailable: boolean;
  onSendMessage: () => void;
  messagesEndRef: React.Ref<HTMLDivElement>;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  messages, 
  input, 
  setInput, 
  isLoading, 
  agentAvailable, 
  onSendMessage, 
  messagesEndRef 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [inputFocused, setInputFocused] = useState(false);

  const quickActions = [
    { label: "Scan for codes", action: "Scan my vehicle for trouble codes" },
    { label: "Engine parameters", action: "Show me live engine parameters" },
    { label: "Check emissions", action: "Check my vehicle's emissions system" },
    { label: "Fuel system", action: "Analyze my fuel system performance" }
  ];

  const handleQuickAction = (action: string) => {
    setInput(action);
  };

  return (
    <div className="xl:col-span-3 flex flex-col h-full">
      <Card className={clsx(
        "flex flex-col h-full glass-effect border-slate-700/50 transition-all duration-500",
        isExpanded && "fixed inset-4 z-50"
      )}>
        <CardHeader className="flex-shrink-0 border-b border-slate-700/30 bg-slate-900/50">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <MessageCircle className="w-6 h-6 text-blue-400" />
                {agentAvailable && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                )}
              </div>
              <div>
                <span className="text-lg font-semibold text-slate-100">AI Diagnostic Chat</span>
                <div className="text-xs text-slate-400 flex items-center mt-1">
                  <Sparkles className="w-3 h-3 mr-1" />
                  Powered by Advanced AI
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-slate-400 hover:text-slate-200"
              >
                {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-slate-400 hover:text-slate-200"
              >
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </div>
          </CardTitle>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-16">
                <div className="relative mb-8">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full blur-2xl opacity-20" />
                  <div className="relative bg-gradient-to-r from-blue-500/20 to-purple-600/20 p-6 rounded-full border border-slate-700/50">
                    <MessageCircle className="w-16 h-16 text-blue-400" />
                  </div>
                </div>
                
                <h3 className="text-2xl font-bold text-slate-100 mb-3">
                  Welcome to AI Car Diagnostic
                </h3>
                <p className="text-slate-400 mb-8 max-w-md leading-relaxed">
                  Connect to your vehicle and start a conversation with your AI mechanic. 
                  Get instant diagnostics, troubleshooting, and repair guidance.
                </p>
                
                {/* Quick Action Buttons */}
                <div className="grid grid-cols-2 gap-3 w-full max-w-md">
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickAction(action.action)}
                      disabled={!agentAvailable}
                      className="border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white transition-all duration-300"
                    >
                      {action.label}
                    </Button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="glass-effect rounded-2xl px-6 py-4 flex items-center space-x-4 border border-slate-700/50">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full typing-indicator" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-blue-400 rounded-full typing-indicator" style={{ animationDelay: '200ms' }} />
                        <div className="w-2 h-2 bg-blue-400 rounded-full typing-indicator" style={{ animationDelay: '400ms' }} />
                      </div>
                      <span className="text-slate-300 font-medium">AI is analyzing your vehicle...</span>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="flex-shrink-0 border-t border-slate-700/30 bg-slate-900/30 p-6">
            {!agentAvailable && (
              <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center space-x-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                <div>
                  <p className="text-red-400 font-medium text-sm">Diagnostic Agent Offline</p>
                  <p className="text-red-300/70 text-xs mt-1">
                    The AI diagnostic system is currently unavailable. Please check your connection.
                  </p>
                </div>
              </div>
            )}
            
            <div className={clsx(
              "relative rounded-2xl border transition-all duration-300",
              inputFocused 
                ? "border-blue-500/50 shadow-lg shadow-blue-500/10" 
                : "border-slate-600/50",
              !agentAvailable && "opacity-50"
            )}>
              <div className="flex items-end space-x-3 p-4">
                <div className="flex-1 space-y-3">
                  <Textarea
                    value={input}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
                    onKeyPress={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        onSendMessage();
                      }
                    }}
                    onFocus={() => setInputFocused(true)}
                    onBlur={() => setInputFocused(false)}
                    placeholder="Describe your vehicle's symptoms or ask for diagnostics..."
                    className="resize-none bg-transparent border-0 focus:ring-0 text-slate-200 placeholder-slate-500 text-base leading-relaxed"
                    rows={2}
                    disabled={isLoading || !agentAvailable}
                  />
                  
                  {input.trim() === '' && !isLoading && (
                    <div className="flex flex-wrap gap-2">
                      {quickActions.slice(0, 2).map((action, index) => (
                        <button
                          key={index}
                          onClick={() => handleQuickAction(action.action)}
                          disabled={!agentAvailable}
                          className="px-3 py-1.5 text-xs bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 hover:text-slate-200 rounded-lg border border-slate-700/50 transition-all duration-200 disabled:opacity-50"
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={!agentAvailable}
                    className="text-slate-400 hover:text-slate-200 p-2"
                  >
                    <Paperclip className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={!agentAvailable}
                    className="text-slate-400 hover:text-slate-200 p-2"
                  >
                    <Mic className="w-4 h-4" />
                  </Button>
                  
                  <Button
                    onClick={onSendMessage}
                    disabled={!input.trim() || isLoading || !agentAvailable}
                    className={clsx(
                      "h-10 w-10 rounded-xl transition-all duration-300",
                      input.trim() && agentAvailable
                        ? "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl"
                        : "bg-slate-700 text-slate-500"
                    )}
                  >
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </Button>
                </div>
              </div>
            </div>
            
            <div className="flex items-center justify-between mt-3 text-xs text-slate-500">
              <div className="flex items-center space-x-4">
                <span>Press Enter to send • Shift+Enter for new line</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={clsx(
                  "w-2 h-2 rounded-full transition-colors duration-300",
                  agentAvailable ? "bg-green-500" : "bg-red-500"
                )} />
                <span>{agentAvailable ? "AI Ready" : "AI Offline"}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
