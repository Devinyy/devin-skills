# Feature Plan

## Goal

Turn `video-knowledge-skill` into a usable app for collecting links/files, extracting transcripts or article text, and generating structured notes.

## Recommended Path

Start with a local Web app:

- Backend: FastAPI
- Frontend: React or Next.js
- Data: SQLite
- Queue: SQLite-backed sequential queue first
- Runtime: local ffmpeg, MLX Whisper, Playwright, cookies

This fits the current project best because platform extraction depends on local browser state, local files, ffmpeg, and Apple Silicon GPU acceleration.

## Options

### 1. Local Web App

Run a local server and use the browser as the UI.

Pros:

- Lowest migration cost from current scripts.
- Keeps cookies, video files, transcripts, and API keys local.
- Works well with ffmpeg, MLX, and Playwright.
- Good fit for personal knowledge management.

Cons:

- Mainly for one machine.
- Requires local environment setup.
- Sharing across devices needs extra work.

Core features:

- Submit URL or local file.
- Queue view with pending/running/done/failed states.
- Task detail page.
- Transcript viewer.
- Summary viewer with `dual`, `faithful`, and `note` modes.
- Retry failed task.
- Re-summarize task.
- Output browser and cleanup tools.

### 2. Cloud Web App

Deploy the whole app to a server.

Pros:

- Accessible from multiple devices.
- Easier to turn into a real hosted product.
- Can support accounts, teams, sharing, and sync.

Cons:

- Higher server cost for ffmpeg, Whisper, and Playwright.
- Platform cookies and browser verification become harder.
- Local MLX GPU acceleration is lost.
- More privacy and compliance concerns.

Best use:

- Later-stage hosted product.
- Or hybrid mode where cloud manages metadata while local workers handle extraction.

### 3. Desktop App

Package the local app with Electron or Tauri.

Pros:

- Better user experience than CLI.
- Can still use local cookies, ffmpeg, MLX, and Playwright.
- Good for drag-and-drop files and background queues.
- Easier to distribute to a small group than a raw local server.

Cons:

- Packaging and auto-update add complexity.
- Electron is heavier; Tauri is lighter but has more integration work.
- UI and release process need maintenance.

Best use:

- After the local Web app is stable.

### 4. Browser Extension + Local Service

Add a browser extension button that sends the current page to the local queue.

Pros:

- Best capture experience.
- One-click save from Bilibili, Douyin, Xiaohongshu, WeChat articles, and other pages.
- Local service still does heavy extraction and summarization.

Cons:

- Requires maintaining both extension and local service.
- Platform page changes may break capture helpers.
- Browser permissions and extension distribution need care.

Best use:

- Add after the local Web app has a stable API.

## Suggested Roadmap

### Phase 1: Local Web MVP

- Add FastAPI server.
- Expose APIs:
  - `POST /tasks`
  - `GET /tasks`
  - `GET /tasks/{id}`
  - `POST /tasks/{id}/retry`
  - `POST /tasks/{id}/summarize`
- Store task state in SQLite.
- Reuse existing extractors and summarizer.
- Build simple UI:
  - submit form
  - queue table
  - task detail
  - transcript/summary tabs

### Phase 2: Better Knowledge UI

- Search across summaries and transcripts.
- Filter by platform and status.
- Add tags and favorite/star.
- Add summary style switch.
- Add markdown export.
- Add batch input UI.

### Phase 3: Browser Extension

- Add local API endpoint for browser extension.
- Build extension action: "Save to Knowledge Queue".
- Capture current URL, title, and selected text when available.

### Phase 4: Desktop Packaging

- Package local Web app as desktop app.
- Add app settings:
  - LLM endpoint/key
  - cookie file paths
  - model size
  - transcription backend
  - output path

### Phase 5: Optional Cloud/Sync

- Add optional account and sync layer.
- Keep extraction local by default.
- Sync only metadata, summaries, and transcripts if enabled.

## Open Decisions

- Frontend stack: React SPA or Next.js.
- Queue runner: in-process worker or separate process.
- Storage layout: keep current `outputs/{task_id}` plus SQLite index, or move all state into SQLite.
- Secret handling: `.env`, OS keychain, or app settings file.
- Whether to support multi-user mode later.

