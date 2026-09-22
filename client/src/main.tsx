import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '@/App';
import { ApiError } from '@/api/groups';
import './styles.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // A 404 means the caller is not a member; retrying cannot change that.
      retry: (failureCount, error) =>
        failureCount < 2 &&
        !(error instanceof ApiError && error.status === 404),
      refetchOnWindowFocus: false,
    },
  },
});

const rootEl = document.getElementById('root');
if (rootEl) {
  createRoot(rootEl).render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </StrictMode>,
  );
}
