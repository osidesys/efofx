import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import ShadowDOMWrapper from './components/ShadowDOMWrapper'

/**
 * efOfX Widget - Embeddable estimation chat widget
 *
 * Initialize the widget by calling: efofxWidget.init({ containerId: 'widget-container' })
 */

interface WidgetConfig {
  containerId?: string;
  apiKey?: string;
}

export function init(config: WidgetConfig = {}) {
  const { containerId = 'efofx-widget' } = config;

  // Find or create container element
  let container = document.getElementById(containerId);
  if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    document.body.appendChild(container);
  }

  // Render widget with Shadow DOM isolation
  const root = createRoot(container);
  root.render(
    <ShadowDOMWrapper>
      <App />
    </ShadowDOMWrapper>,
  );

  return {
    destroy: () => {
      root.unmount();
    },
  };
}

// Auto-initialize if running in dev mode (not as embedded widget)
if (import.meta.env.DEV) {
  init();
}

// Export for library build
export default { init };
