import { clsx } from 'clsx';
import type { Message } from '../types';
import { Card } from "@/components/ui/card";

const formatTime = (date: Date) => 
  date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

export const ChatMessage: React.FC<{ message: Message }> = ({ message }) => (
  <div className={clsx("flex message-fade-in", {
    'justify-end': message.type === 'user',
    'justify-start': message.type === 'agent' || message.type === 'error',
    'justify-center': message.type === 'info',
  })}>
    {message.type === 'info' ? (
      <div className="text-base text-muted-foreground italic my-2">{message.content}</div>
    ) : (
      <Card className={clsx("max-w-[85%] rounded-lg px-5 py-3 shadow-md", {
        'bg-primary text-primary-foreground': message.type === 'user',
        'bg-destructive text-destructive-foreground': message.type === 'error',
        'bg-muted text-foreground': message.type === 'agent',
      })}>
        <div className="whitespace-pre-wrap text-base">{message.content}</div>
        <p className="text-xs mt-2 opacity-80 text-right">{formatTime(message.timestamp)}</p>
      </Card>
    )}
  </div>
);