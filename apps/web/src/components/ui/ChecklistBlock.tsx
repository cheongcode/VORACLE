'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import { Check, Copy, CheckCheck, Target, XCircle } from 'lucide-react';
import { useState } from 'react';

interface ChecklistBlockProps {
  title: string;
  items: string[];
  variant?: 'default' | 'action' | 'warning';
  icon?: React.ReactNode;
  className?: string;
  printable?: boolean;
}

export function ChecklistBlock({
  title,
  items,
  variant = 'default',
  icon,
  className,
  printable = true,
}: ChecklistBlockProps) {
  const [copiedAll, setCopiedAll] = useState(false);
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set());

  const variants = {
    default: {
      container: 'border-valorant-border bg-valorant-card',
      header: 'text-text-secondary',
      icon: <Target className="h-5 w-5 text-c9-cyan" />,
      checkColor: 'text-c9-cyan',
    },
    action: {
      container: 'border-c9-cyan/30 bg-c9-cyan/5',
      header: 'text-c9-cyan',
      icon: <Target className="h-5 w-5 text-c9-cyan" />,
      checkColor: 'text-c9-cyan',
    },
    warning: {
      container: 'border-valorant-red/30 bg-valorant-red/5',
      header: 'text-valorant-red',
      icon: <XCircle className="h-5 w-5 text-valorant-red" />,
      checkColor: 'text-valorant-red',
    },
  };

  const config = variants[variant];

  const handleCopyAll = async () => {
    const text = items.map((item, i) => `${i + 1}. ${item}`).join('\n');
    await navigator.clipboard.writeText(text);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  const toggleItem = (index: number) => {
    const newChecked = new Set(checkedItems);
    if (newChecked.has(index)) {
      newChecked.delete(index);
    } else {
      newChecked.add(index);
    }
    setCheckedItems(newChecked);
  };

  return (
    <motion.div
      className={cn(
        'rounded-xl border overflow-hidden',
        config.container,
        printable && 'print:border-gray-300 print:bg-white',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-valorant-border print:border-gray-300">
        <div className="flex items-center gap-3">
          {icon || config.icon}
          <h3 className={cn(
            'text-sm font-semibold uppercase tracking-widest',
            config.header,
            'print:text-gray-700'
          )}>
            {title}
          </h3>
        </div>
        
        <button
          onClick={handleCopyAll}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-text-secondary hover:text-c9-cyan hover:bg-c9-cyan/10 transition-colors print:hidden"
        >
          {copiedAll ? (
            <>
              <CheckCheck className="h-3.5 w-3.5" />
              Copied
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              Copy All
            </>
          )}
        </button>
      </div>

      {/* Items */}
      <div className="p-4 space-y-2">
        {items.map((item, index) => (
          <motion.div
            key={index}
            className={cn(
              'group flex items-start gap-3 p-3 rounded-lg',
              'hover:bg-valorant-dark/30 transition-colors cursor-pointer',
              checkedItems.has(index) && 'opacity-60',
              'print:p-2 print:hover:bg-transparent'
            )}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            onClick={() => toggleItem(index)}
          >
            {/* Checkbox */}
            <div
              className={cn(
                'flex-shrink-0 w-6 h-6 rounded-md border-2 flex items-center justify-center',
                checkedItems.has(index)
                  ? `${variant === 'warning' ? 'bg-valorant-red border-valorant-red' : 'bg-c9-cyan border-c9-cyan'}`
                  : 'border-valorant-border group-hover:border-c9-cyan/50',
                'transition-colors print:w-5 print:h-5 print:border-gray-400'
              )}
            >
              {checkedItems.has(index) && (
                <Check className="h-4 w-4 text-white print:text-gray-800" />
              )}
            </div>

            {/* Number */}
            <span className={cn(
              'flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
              variant === 'warning'
                ? 'bg-valorant-red/20 text-valorant-red'
                : 'bg-c9-cyan/20 text-c9-cyan',
              'print:bg-gray-200 print:text-gray-700'
            )}>
              {index + 1}
            </span>

            {/* Text */}
            <p className={cn(
              'flex-1 text-sm leading-relaxed',
              checkedItems.has(index) ? 'text-text-secondary line-through' : 'text-white',
              'print:text-gray-800 print:no-underline'
            )}>
              {item}
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
