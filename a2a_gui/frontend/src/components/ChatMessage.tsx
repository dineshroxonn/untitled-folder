import React from 'react';
import { clsx } from 'clsx';
import { Bot, User, AlertTriangle, Info, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import type { Message } from '../types';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const formatTime = (date: Date) => 
  date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

const formatContent = (content: string) => {
  // Enhanced formatting for diagnostic content
  return content
    .replace(/(\*\*)(.*?)\1/g, '<strong class="text-slate-100 font-semibold">$2</strong>')
    .replace(/(\*)(.*?)\1/g, '<em class="text-slate-300 italic">$2</em>')
    .replace(/(P[0-9A-F]{4})/g, '<code class="bg-slate-800/50 text-blue-400 px-2 py-0.5 rounded font-mono text-sm">$1</code>')
    .replace(/(\d+°[CF])/g, '<span class="text-cyan-400 font-medium">$1</span>')
    .replace(/(\d+\s*rpm)/gi, '<span class="text-green-400 font-medium">$1</span>')
    .replace(/(✅|🔴|🟡|🔵|⚠️|🔍|📋|📊|🚗|💬)/g, '<span class="text-lg">$1</span>');
};

export const ChatMessage: React.FC<{ message: Message }> = ({ message }) => {
  const [showActions, setShowActions] = React.useState(false);

  const getMessageIcon = () => {
    switch (message.type) {
      case 'user': return <User className="w-4 h-4" />;
      case 'agent': return <Bot className="w-4 h-4" />;
      case 'error': return <AlertTriangle className="w-4 h-4" />;
      case 'info': return <Info className="w-4 h-4" />;
      default: return null;
    }
  };

  const copyToClipboard = () => {
    if (typeof message.content === 'string') {
      navigator.clipboard.writeText(message.content);
    }
  };

  if (message.type === 'info') {
    return (
      <div className="flex justify-center message-fade-in">
        <div className="flex items-center space-x-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400">
          <Info className="w-4 h-4" />
          <span className="text-sm font-medium">{message.content}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx("flex message-fade-in group", {
      'justify-end': message.type === 'user',
      'justify-start': message.type === 'agent' || message.type === 'error',
    })}>
      <div className={clsx("max-w-[85%] flex", {
        'flex-row-reverse': message.type === 'user',
        'flex-row': message.type === 'agent' || message.type === 'error',
      })}>
        {/* Avatar */}
        <div className={clsx("flex-shrink-0 flex items-end", {
          'ml-3': message.type === 'user',
          'mr-3': message.type === 'agent' || message.type === 'error',
        })}>
          <div className={clsx(
            "w-8 h-8 rounded-full flex items-center justify-center border-2 transition-all duration-300",
            message.type === 'user' 
              ? "bg-gradient-to-r from-blue-600 to-purple-600 border-blue-500/50 text-white" 
              : message.type === 'error'
              ? "bg-gradient-to-r from-red-600 to-orange-600 border-red-500/50 text-white"
              : "bg-gradient-to-r from-emerald-600 to-cyan-600 border-emerald-500/50 text-white"
          )}>
            {getMessageIcon()}
          </div>
        </div>

        {/* Message Content */}
        <div 
          className="relative"
          onMouseEnter={() => setShowActions(true)}
          onMouseLeave={() => setShowActions(false)}
        >
          <Card className={clsx(
            "relative transition-all duration-300 hover-lift",
            message.type === 'user' 
              ? "bg-gradient-to-r from-blue-600/90 to-purple-600/90 border-blue-500/30 text-white" 
              : message.type === 'error'
              ? "bg-gradient-to-r from-red-600/20 to-orange-600/20 border-red-500/30 text-red-200"
              : "glass-effect border-slate-700/50 text-slate-100"
          )}>
            <div className="px-5 py-4">
              {typeof message.content === 'string' ? (
                <div
                  className="whitespace-pre-wrap text-base leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html: formatContent(message.content),
                  }}
                />
              ) : (
                <div className="whitespace-pre-wrap text-base leading-relaxed">
                  {message.content}
                </div>
              )}
              
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-current/10">
                <div className="text-xs opacity-70 flex items-center space-x-2">
                  <span>{formatTime(message.timestamp)}</span>
                  {message.type === 'agent' && (
                    <>
                      <span>•</span>
                      <span className="flex items-center space-x-1">
                        <Bot className="w-3 h-3" />
                        <span>AI Response</span>
                      </span>
                    </>
                  )}
                </div>
                
                {/* Message Actions */}
                <div className={clsx(
                  "flex items-center space-x-1 transition-all duration-200",
                  showActions ? "opacity-100 translate-x-0" : "opacity-0 translate-x-2"
                )}>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={copyToClipboard}
                    className="h-6 w-6 p-0 hover:bg-white/10 text-current/70 hover:text-current"
                  >
                    <Copy className="w-3 h-3" />
                  </Button>
                  
                  {message.type === 'agent' && (
                    <>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 hover:bg-white/10 text-current/70 hover:text-current"
                      >
                        <ThumbsUp className="w-3 h-3" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 hover:bg-white/10 text-current/70 hover:text-current"
                      >
                        <ThumbsDown className="w-3 h-3" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
