import React from 'react';
import { MessageCircle, Loader2, Send, AlertCircle } from 'lucide-react';
import type { Message } from '../types';
import { ChatMessage } from './ChatMessage';
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface ChatInterfaceProps {
  messages: Message[];
  input: string;
  setInput: (val: string) => void;
  isLoading: boolean;
  agentAvailable: boolean;
  onSendMessage: () => void;
  messagesEndRef: React.Ref<HTMLDivElement>;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ messages, input, setInput, isLoading, agentAvailable, onSendMessage, messagesEndRef }) => (
  <div className="lg:col-span-2">
    <Card className="flex flex-col h-[75vh] bg-secondary border-primary/20">
      <CardContent className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.length === 0 ? (
          <div className="text-center py-16">
            <MessageCircle className="w-16 h-16 text-primary mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-foreground">
              Welcome to AI Car Diagnostic
            </h3>
            <p className="text-muted-foreground mt-2">
              Connect to your vehicle to begin diagnostics.
            </p>
          </div>
        ) : (
          messages.map((message) => <ChatMessage key={message.id} message={message} />)
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg px-4 py-3 flex items-center space-x-3">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <span className="text-base text-foreground">AI is diagnosing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </CardContent>
      <div className="border-t-2 border-primary/20 p-4">
        <div className="flex items-center space-x-4">
          <Textarea
            value={input}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
            onKeyPress={(e: React.KeyboardEvent<HTMLTextAreaElement>) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), onSendMessage())}
            placeholder="Ask about the diagnosis or enter codes manually..."
            className="flex-1 resize-none bg-background"
            rows={2}
            disabled={isLoading || !agentAvailable}
          />
          <Button
            onClick={onSendMessage}
            disabled={!input.trim() || isLoading || !agentAvailable}
            className="px-6 py-3"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
        {!agentAvailable && (
          <p className="text-destructive text-sm mt-2 flex items-center">
            <AlertCircle className="w-4 h-4 mr-2" />
            Diagnostic agent is not available.
          </p>
        )}
      </div>
    </Card>
  </div>
);