import React, { useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';

interface ShadowDOMWrapperProps {
  children: React.ReactNode;
}

/**
 * Shadow DOM Wrapper Component
 *
 * Provides style isolation for the widget by rendering children inside a Shadow DOM.
 * This prevents CSS conflicts with the host site's styles.
 */
export const ShadowDOMWrapper: React.FC<ShadowDOMWrapperProps> = ({ children }) => {
  const hostRef = useRef<HTMLDivElement>(null);
  const shadowRootRef = useRef<ShadowRoot | null>(null);
  const reactRootRef = useRef<Root | null>(null);

  useEffect(() => {
    if (!hostRef.current) return;

    // Only create shadow root once
    if (!shadowRootRef.current) {
      // Check if shadow root already exists (safety check)
      const existingShadow = hostRef.current.shadowRoot;
      if (existingShadow) {
        shadowRootRef.current = existingShadow;
      } else {
        shadowRootRef.current = hostRef.current.attachShadow({ mode: 'open' });
      }

      // Create a container div inside shadow DOM
      const container = document.createElement('div');
      container.id = 'efofx-widget-root';
      shadowRootRef.current.appendChild(container);

      // Create React root
      reactRootRef.current = createRoot(container);
    }

    // Render children (will update on children change)
    if (reactRootRef.current) {
      reactRootRef.current.render(children);
    }

    return () => {
      // Only unmount on final cleanup
      if (reactRootRef.current) {
        reactRootRef.current.unmount();
        reactRootRef.current = null;
        shadowRootRef.current = null;
      }
    };
  }, [children]);

  return <div ref={hostRef} className="efofx-widget-host" />;
};

export default ShadowDOMWrapper;
