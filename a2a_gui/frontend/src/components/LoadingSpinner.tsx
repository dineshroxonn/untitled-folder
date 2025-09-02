import React from 'react';
import { Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  text,
  className 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <div className={clsx("flex items-center space-x-3", className)}>
      <Loader2 className={clsx(sizeClasses[size], "animate-spin text-blue-400")} />
      {text && (
        <span className="text-slate-300 font-medium">{text}</span>
      )}
    </div>
  );
};