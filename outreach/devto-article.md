# Dev.to Article

**Title:** How I built a 1,000-page SaaS comparison site with Python and zero CMS

**Tags:** python, programming, webdev, productivity

---

## Article Body

Last year I got tired of SaaS review sites that ranked tools by affiliate commission rather than merit. So I did what any developer would do: I built something better.

This is a write-up of the technical approach behind SaaSpare (saaspare.org) — a static site with 1,000+ comparison pages built from structured YAML data and a Python pipeline. No WordPress, no Strapi, no database in production.

### The architecture

The core is a Python build pipeline:

1. **Data layer** — YAML files for each product, each category, and the comparison matrix
2. **Builder scripts** — Python scripts that read the YAML and render Jinja2 HTML templates
3. **Static output** — everything is pre-rendered into `/site/` as plain HTML
4. **Schema injection** — a separate script layer adds JSON-LD schema blocks (Product, Review, FAQ, HowTo, Speakable, BreadcrumbList) to each page post-render

No Node, no bundler, no frontend framework. The entire build runs in under 10 seconds.

### Why static HTML for SEO

Dynamic rendering adds latency and complexity that doesn't help SEO. Google's crawler loves clean, pre-rendered HTML with:
- No JavaScript-dependent content (all content in raw HTML)
- Stable canonical URLs
- Schema markup that validates without JS execution
- Sub-200ms TTFB (we're consistently at ~60ms on Netlify)

### The schema layer

Each comparison page gets:
- `Product` schema for each reviewed tool (name, description, offers, aggregateRating)
- `Review` schema for our editorial verdict
- `BreadcrumbList` for navigation path
- `FAQPage` for the Q&A section at the bottom
- `ItemList` for the side-by-side comparison table

The injection script walks the `/site/` directory and patches each file rather than rebuilding from template, which keeps the build modular.

### What actually drives traffic

Counter-intuitively, the highest-traffic pages are not the category overview pages — they're the ultra-specific comparisons:

- "[Tool A] vs [Tool B] for [team size]"
- "[Tool] pricing 2026: actual cost breakdown"
- "[Tool] free trial: does it auto-charge?"

These long-tail queries have much lower competition and convert better because the user's intent is already precise.

### The pricing data challenge

The hardest part isn't building pages — it's keeping pricing accurate. SaaS vendors change prices often without announcement. Our solution is a monthly price-check pass that diffs the current vendor pricing page against our stored value and flags changes.

One finding worth sharing: we tracked pricing across 1,000+ tools going back to 2023. Median SaaS prices rose 34% in three years. The full dataset is at saaspare.org/research/saas-pricing-2026 — licensed CC BY.

### Lessons learned

- **Start with the template, not the data.** I built the HTML template first and then reverse-engineered what fields I needed. Much easier than designing a data schema in the abstract.
- **Schema markup is genuinely worth it.** FAQ rich results drove a measurable CTR improvement on pages that got them.
- **Programmatic SEO needs a differentiation story.** You can't just spin up 10,000 thin pages and expect traffic. Every page needs to answer a question that isn't better answered by the vendor's own site.

Happy to answer questions on the technical side — stack audit, schema strategy, or the build pipeline.

---

## Notes
- Dev.to allows canonical links — add `canonical_url: https://saaspare.org/blog/[equivalent]` to the frontmatter
- This kind of "I built X, here's how" post performs well on Dev.to
- Tag it accurately — devto rewards correct tagging
- Post to the DEV Community tag AND the python tag
- Respond to comments in the first 48 hours for algorithmic boost
