import { clsx } from 'clsx';
import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: boolean;
  hover?: boolean;
  title?: string;
  subtitle?: string;
}

export function Card({ children, className, padding = true, hover = false, title, subtitle }: CardProps) {
  return (
    <div className={clsx(
      'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm',
      padding && 'p-6',
      hover && 'hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200',
      className
    )}>
      {(title || subtitle) && (
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && <h3 className="text-base font-bold text-gray-900 dark:text-white">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>}
          </div>
        </div>
      )}
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
}

export function CardHeader({ title, subtitle, action, className }: CardHeaderProps) {
  return (
    <div className={clsx('flex items-center justify-between mb-4', className)}>
      <div>
        <h3 className="text-base font-bold text-gray-900 dark:text-white">{title}</h3>
        {subtitle && <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
