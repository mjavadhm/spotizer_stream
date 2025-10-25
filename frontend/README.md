# Music Streamer Frontend

This is a SvelteKit frontend for a music streaming service.

## Getting Started

1.  **Install dependencies:**
    ```bash
    npm install
    ```

2.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

## Deployment

This project is configured with `@sveltejs/adapter-auto`, which automatically adapts the output for the target deployment platform. To deploy, simply connect your Git repository to a hosting provider that supports Node.js, such as Vercel, Netlify, or Cloudflare Pages.

For example, with Vercel, you can import the repository and use the following settings:
- **Framework Preset:** SvelteKit
- **Build Command:** `npm run build`
- **Output Directory:** `.svelte-kit/output` (usually detected automatically)

The adapter will handle the rest.
