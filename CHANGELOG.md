# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.1.2] - 2026-07-23

### Added

- **Sibling scene expansion**: search results still show one card per clip,
  but now display "N more matching scenes" with an expander that reveals all
  of that clip's matching scenes, ranked against the original query
  (`POST /api/clip_matches`, powered by a cached query vector — no extra
  embedding API calls)
- **Lightbox player**: click any clip preview (results, home page, or
  expanded scenes) to open a large popup player with native controls
- **Elasticsearch deployment portability**: run against local Docker,
  managed Elastic Cloud (`ES_URL` or new `ES_CLOUD_ID`), or Elastic Cloud
  Serverless. On startup the app reconciles the local manifest with the
  connected cluster and re-indexes missing clips automatically, using a
  persistent embed cache (`chunks/.embed_cache.json`) so switching
  deployments never re-pays the embedding API
- `/api/health` now reports the connected deployment (flavor, version,
  cluster name)

### Changed

- Dependency updates across the board (elasticsearch, fastapi, python-dotenv,
  httpx, ruff, vite 8, GitHub Actions); Dependabot now opens one grouped PR
  per ecosystem

## [0.1.1] - 2026-07-23

### Added

- Indexing progress bar showing the current file and queue position
  (e.g. "indexing clip.mp4 · 3 of 7"), with an expandable event log
- Home page shows the most recently indexed clips ("Latest additions"),
  auto-refreshing as new footage finishes, via a new `GET /api/recent` endpoint
- Upload-date badges on home-page clips
- Browser history navigation: searches and similar-clip views get URLs
  (`?q=…`, `?similar=…`), back/forward buttons work, and clicking the
  omnishot logo returns home

### Changed

- Project renamed from `omnishot-ts` to `omnishot`; the upstream benchmark
  repo now lives at `omnishot-benchmark`
- **Default Elasticsearch index renamed `broll-demo` → `broll`** and the
  watcher manifest renamed `.demo_manifest.json` → `.manifest.json`. Existing
  setups re-ingest on next start, or set `BROLL_INDEX=broll-demo` in `.env`
  to keep the old index

### Fixed

- Status no longer stays stuck on "indexing" after the last clip finishes
  (the watcher never reset its state once the ingest queue drained)
- Log toggle button now vertically aligned with the status line

## [0.1.0] - 2026-07-23

### Added

- Folder-watch ingest: drop videos in a linked library folder → scene-chunked
  (PySceneDetect), embedded (Jina v5-omni-small), indexed (Elasticsearch HNSW)
- Search by text description, by uploaded/dropped reference image, and
  "more like this" via stored vectors
- Reveal-in-file-manager for source clips (macOS / Windows / Linux)
- Library folder picker (native OS dialog) with corpus rebuild on switch
- Lightweight download scripts (Pexels, YouTube) and batch ingest CLI
- Vite + TypeScript frontend; FastAPI backend
- One-command full-stack startup via Docker Compose
- `/api/health` endpoint; graceful wait for Elasticsearch on startup
- CI (lint, tests, frontend build, Docker build) and Dependabot
