/**
 * Tab Group Component
 * 
 * Modern tab navigation with animated indicator
 */

import React from 'react';
import { motion } from 'framer-motion';

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

interface TabGroupProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  size?: 'sm' | 'md' | 'lg';
}

export const TabGroup: React.FC<TabGroupProps> = ({
  tabs,
  activeTab,
  onChange,
  size = 'md',
}) => {
  const sizeStyles = {
    sm: 'text-xs px-3 py-1.5',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-5 py-2.5',
  };

  return (
    <div className="flex gap-1 p-1 bg-dark-200/60 rounded-xl backdrop-blur-sm border border-white/5">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={`
              relative ${sizeStyles[size]} rounded-lg font-medium
              transition-colors duration-200
              ${isActive
                ? 'text-white'
                : 'text-gray-400 hover:text-gray-200'
              }
            `}
          >
            {isActive && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-primary-500/20 border border-primary-500/30 rounded-lg"
                transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
              />
            )}
            <span className="relative flex items-center gap-2">
              {tab.icon}
              {tab.label}
            </span>
          </button>
        );
      })}
    </div>
  );
};

export default TabGroup;
