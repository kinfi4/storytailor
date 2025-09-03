import React from 'react';
import { createRoot } from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import StoriesListPage from './pages/StoriesListPage';
import CreateStoryPage from './pages/CreateStoryPage';
import StoryDetailsPage from './pages/StoryDetailsPage';
import './styles.css';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <StoriesListPage /> },
      { path: 'create', element: <CreateStoryPage /> },
      { path: 'stories/:id', element: <StoryDetailsPage /> },
      { path: 'stories', element: <StoriesListPage /> },
    ],
  },
]);

const container = document.getElementById('root');
if (!container) {
  throw new Error('Root container not found');
}

createRoot(container).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
