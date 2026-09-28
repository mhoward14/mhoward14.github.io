# Matthew Howard: Personal Site

The front door to my work, live at **[mhoward14.github.io](https://mhoward14.github.io/)**.

It introduces me, points to my main project, the **[Cybersecurity Portfolio](https://mhoward14.github.io/cyber-portfolio/)** ([source](https://github.com/mhoward14/cyber-portfolio)), and collects earlier coursework: recorded presentations and data diagrams from my web development studies.

## Pages

| Page | What it holds |
| --- | --- |
| [Home](https://mhoward14.github.io/) | About, the featured cybersecurity portfolio, and earlier work |
| [DevOps Presentations](https://mhoward14.github.io/web-430/howard-devops.html) | Recorded talks on CI, value streams, team structure, and source-control security |
| [RESTful API Presentations](https://mhoward14.github.io/web-420/howard-rest.html) | Recorded talks on REST, SOAP, SOA, JSON APIs, OAuth, and microservices |
| [NoSQL Diagrams](https://mhoward14.github.io/web-335/howard-diagrams.html) | Data diagrams and document structures from NoSQL coursework |

## Design

Plain HTML, CSS and a small script, with no framework and no build step. It shares the portfolio's design tokens (palette, type, dotted background, `// LABEL` headings) and its dark/light theme choice, so moving between the two sites feels like one site.

- `style.css`: the whole design system
- `site.js`: theme, collapsible sidebar, email links and the frame guard
- `og-image.png`: the link-preview card

## Security

The site has no forms, cookies, or accounts, and it's hardened like the portfolio:

- A strict Content Security Policy on every page: scripts only from this site and Cloudflare Web Analytics, with no inline script, inline styles, plugins, frames or form submissions.
- Clickjacking protection: pages hide themselves when framed by another site, because GitHub Pages can't send `X-Frame-Options` or `frame-ancestors` headers.
- `strict-origin-when-cross-origin` referrer policy, and `rel="noopener"` on every link that opens a new tab.
- The contact address is assembled only when a visitor reaches for the email link, so it isn't in the page source.
- The deploy workflow pins its actions to full commit SHAs and requests only the permission it needs.

The portfolio's [SECURITY.md](https://github.com/mhoward14/cyber-portfolio/blob/master/SECURITY.md) explains the full approach and the limits of static hosting.

## Local preview

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000).

## Deployment

Pushes to `master` run `.github/workflows/deploy.yml`, which publishes the repository to the `gh-pages` branch that GitHub Pages serves.
