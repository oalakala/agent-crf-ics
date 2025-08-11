# agent-crf-ics — Pages structure

This patch adds:
- `.github/workflows/publish.yml` — build & deploy Pages from `site/` artifact
- `wp/posts_consolidado.csv` — CSV feed for WordPress plugin
- `ics/.keep` — keep ICS directory tracked

## After pushing
- Run Actions: **Build & Publish ICS** → *Run workflow*
- CSV URL to use in WordPress:
  https://oalakala.github.io/agent-crf-ics/wp/posts_consolidado.csv