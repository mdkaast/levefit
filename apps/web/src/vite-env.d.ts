/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_DEV_INIT_DATA?: string;
}

interface Window {
  Telegram?: {
    WebApp?: {
      HapticFeedback?: {
        selectionChanged: () => void;
        impactOccurred?: (style: string) => void;
        notificationOccurred?: (type: string) => void;
      };
    };
  };
}
