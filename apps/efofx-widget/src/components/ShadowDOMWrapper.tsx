import React, { useEffect, useRef, useState } from 'react';
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
  const [shadowRoot, setShadowRoot] = useState<ShadowRoot | null>(null);
  const rootRef = useRef<Root | null>(null);

  useEffect(() => {
    if (hostRef.current && !shadowRoot) {
      // Create shadow root with open mode
      const shadow = hostRef.current.attachShadow({ mode: 'open' });
      setShadowRoot(shadow);

      // Create a container div inside shadow DOM
      const container = document.createElement('div');
      container.id = 'efofx-widget-root';
      shadow.appendChild(container);

      // Create React root and render children
      rootRef.current = createRoot(container);
      rootRef.current.render(children);
    }

    return () => {
      if (rootRef.current) {
        rootRef.current.unmount();
        rootRef.current = null;
      }
    };
  }, [shadowRoot, children]);

  return <div ref={hostRef} className="efofx-widget-host" />;
};

export default ShadowDOMWrapper;
