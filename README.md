# FilkomTech Static Company Profile — Containerized Frontend Lab

[![Static + Container CI](https://github.com/syifaniads/web-profile/actions/workflows/static-container-ci.yml/badge.svg)](https://github.com/syifaniads/web-profile/actions/workflows/static-container-ci.yml)

A small static frontend exercise packaged as an Nginx container. The repository is kept as a **frontend/containerization lab**, not as a claim that the fictional company, customer counts, certifications, or business metrics shown in the demo page are real.

> **Portfolio scope:** `FilkomTech Solutions` is demo content used to exercise responsive HTML/CSS delivery and container packaging. It is not a real company profile and its marketing copy should not be interpreted as personal or commercial claims.

## What is technically reviewable

```text
Browser
  |
  v
Nginx unprivileged container :8080
  |
  +-- index.html
  +-- css/style.css
```

The current portfolio pass focuses on the infrastructure boundary around the static UI:

- semantic single-page HTML with responsive styling;
- Nginx-based static delivery;
- unprivileged runtime image on port `8080`;
- container health check;
- Docker Compose development path;
- deterministic static-site validation;
- Docker image build validation in GitHub Actions;
- `.dockerignore` to keep build context small.

## Run locally

With Docker Compose:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8080
```

Or build directly:

```bash
docker build -t web-profile-demo .
docker run --rm -p 8080:8080 web-profile-demo
```

## Validation

The repository includes a local validator that checks the retained HTML/CSS contract without requiring a browser:

```bash
python scripts/validate_static_site.py
```

It verifies that:

- `index.html` has a document title, language, and viewport metadata;
- the referenced stylesheet exists;
- core navigation anchors resolve to real section IDs;
- Docker configuration exposes the unprivileged application port;
- no `.env` or obvious secret-bearing file is required to render the site.

GitHub Actions then runs the validator and builds the Docker image.

## Repository guide

```text
.
├── index.html
├── css/style.css
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── scripts/validate_static_site.py
└── .github/workflows/static-container-ci.yml
```

## Engineering notes

This is intentionally a small project. It demonstrates static web delivery and container hygiene rather than pretending to be a production platform. A larger production website would normally add automated accessibility testing, browser/E2E tests, CSP tuning, image optimization, immutable asset caching, structured observability, deployment environments, and a real content/data source.

## Security boundary

The site is static and requires no runtime credentials. Do not add API keys, analytics secrets, private customer information, or production configuration directly to the HTML/CSS repository. The container runs on an unprivileged port and should remain read-only at runtime where the deployment platform supports it.
