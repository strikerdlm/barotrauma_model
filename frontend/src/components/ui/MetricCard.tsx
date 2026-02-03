/**
 * Metric Card Component
 * 
 * Displays a single key metric with label, value, and optional delta indicator
 */

import React from 'react';
import { motion } from 'framer-motion';

interface MetricCardProps {
  label: string;
  value: string | number;
  unit?: string;
  delta?: number;
  deltaLabel?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger';
  icon?: React.ReactNode;
  compact?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  delta,
  deltaLabel,
  variant = 'default',
  icon,
  compact = false,
}) => {
  const variantStyles = {
    default: {
      border: 'border-white/5',
      glow: '',
      text: 'text-primary-400',
    },
    success: {
      border: 'border-risk-low/30',
      glow: 'shadow-risk-low/10',
      text: 'text-risk-low',
    },
    warning: {
      border: 'border-risk-moderate/30',
      glow: 'shadow-risk-moderate/10',
      text: 'text-risk-moderate',
    },
    danger: {
      border: 'border-risk-high/30',
      glow: 'shadow-risk-high/10',
      text: 'text-risk-high',
    },
  };

  const styles = variantStyles[variant];
  const deltaPositive = delta !== undefined && delta >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className={`
        metric-card ${styles.border} ${styles.glow}
        ${compact ? 'p-3' : 'p-4'}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="metric-label flex items-center gap-2">
            {icon && <span className="text-lg">{icon}</span>}
            {label}
          </p>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className={`metric-value ${styles.text}`}>
              {typeof value === 'number' ? value.toFixed(2) : value}
            </span>
            {unit && (
              <span className="text-sm text-gray-500 font-mono">{unit}</span>
            )}
          </div>
        </div>
        
        {delta !== undefined && (
          <div className={`
            flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium
            ${deltaPositive 
              ? 'bg-risk-high/20 text-risk-high' 
              : 'bg-risk-low/20 text-risk-low'
            }
          `}>
            <span>{deltaPositive ? '↑' : '↓'}</span>
            <span className="font-mono">
              {Math.abs(delta).toFixed(1)}
              {deltaLabel && ` ${deltaLabel}`}
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default MetricCard;
