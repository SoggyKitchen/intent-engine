import sys
import click
from rich.console import Console
from rich.table import Table

console = Console(force_terminal=True, highlight=False)


@click.group()
def cli():
    """Intent Engine - autonomous B2B lead & SEO machine."""
    pass


@cli.command()
def init():
    """Initialize the database schema."""
    from core.db import migrate
    migrate()
    click.echo("OK  Database initialized")


@cli.command()
def harvest():
    """Harvest signals from all sources."""
    from core.db import migrate
    migrate()
    from ops.harvest import run
    count = run()
    click.echo(f"OK  Harvested {count} new signals")


@cli.command()
def score():
    """Score unprocessed signals with LLM."""
    from ops.score_job import run
    count = run()
    click.echo(f"OK  Scored {count} signals")


@cli.command()
def publish():
    """Generate outputs and publish."""
    from ops.publish_job import run
    run()
    click.echo("OK  Publish job complete")


@cli.command()
def optimize():
    """Run daily bandit optimization."""
    from learn.optimize import run_daily_optimization
    run_daily_optimization()
    click.echo("OK  Optimization complete")


@cli.command("run-all")
def run_all():
    """Run full pipeline: harvest > score > publish > optimize."""
    from core.db import migrate
    migrate()
    click.echo("Running full pipeline...")
    from ops.harvest import run as harvest_run
    n = harvest_run()
    click.echo(f"  Harvested: {n}")
    from ops.score_job import run as score_run
    n = score_run()
    click.echo(f"  Scored: {n}")
    from ops.publish_job import run as publish_run
    publish_run()
    from learn.optimize import run_daily_optimization
    run_daily_optimization()
    click.echo("DONE  Full pipeline complete")


@cli.command()
def stats():
    """Show current stats."""
    from core.db import db
    with db() as conn:
        raw_total = conn.execute("SELECT COUNT(*) FROM raw_signals").fetchone()[0]
        scored_total = conn.execute("SELECT COUNT(*) FROM scored_signals").fetchone()[0]
        outputs_total = conn.execute("SELECT COUNT(*) FROM outputs").fetchone()[0]
        revenue = conn.execute("SELECT COALESCE(SUM(revenue),0) FROM outputs").fetchone()[0]
        top = conn.execute("""
            SELECT vertical, COUNT(*) as cnt, AVG(profit_score) as avg_ps
            FROM scored_signals GROUP BY vertical ORDER BY avg_ps DESC LIMIT 10
        """).fetchall()

    click.echo("\n=== Intent Engine Stats ===")
    click.echo(f"  Raw signals:      {raw_total}")
    click.echo(f"  Scored signals:   {scored_total}")
    click.echo(f"  Outputs:          {outputs_total}")
    click.echo(f"  Total revenue:    ${revenue:.2f}")
    if top:
        click.echo("\n  Top verticals by profit score:")
        for row in top:
            click.echo(f"    {row['vertical']:<25} {row['cnt']:>5} signals  avg={row['avg_ps']:.1f}")
    click.echo("")


@cli.command()
@click.argument("vertical")
def pack(vertical: str):
    """Generate a lead pack for a specific vertical."""
    from outputs.lead_pack import generate
    path = generate(vertical)
    if path:
        click.echo(f"OK  Lead pack ready: {path}")
    else:
        click.echo("SKIP  Not enough signals for lead pack")


@cli.command()
def social():
    """Post comparison pages to Twitter/X and stage Reddit answers."""
    from ops.social_post import run_twitter, run_reddit_answers
    run_twitter()
    run_reddit_answers()
    click.echo("OK  Social posting done")


@cli.command()
def backlinks():
    """Submit new pages to IndexNow and build backlink queue."""
    from ops.backlink_submit import run
    run()
    click.echo("OK  Backlink submission done")


@cli.command()
def newsletter():
    """Generate and send weekly digest newsletter."""
    from outputs.newsletter import generate_weekly_digest, send_digest
    path = generate_weekly_digest()
    if path:
        send_digest(path)
        click.echo(f"OK  Newsletter sent: {path}")
    else:
        click.echo("SKIP  Not enough content for newsletter")


@cli.command("inject-forms")
def inject_forms():
    """Inject email capture forms into all SEO pages."""
    from outputs.newsletter import inject_capture_forms
    inject_capture_forms()
    click.echo("OK  Email forms injected")


@cli.command()
@click.option("--max-pages", default=500, help="Max pages to generate")
def programmatic(max_pages: int):
    """Generate SEO pages for ALL tool combinations (programmatic SEO)."""
    from outputs.programmatic import run_programmatic
    from publisher.pages_deploy import deploy_all
    count = run_programmatic(max_pages=max_pages)
    if count > 0:
        deploy_all()
    click.echo(f"OK  {count} programmatic pages generated and deployed")


@cli.command()
def revenue():
    """Show per-program affiliate revenue estimates."""
    from publisher.affiliate_registry import PROGRAMS, estimate_monthly_revenue
    click.echo("\n=== Affiliate Revenue Estimates (at 2k visitors/mo per page) ===")
    for vertical, programs in PROGRAMS.items():
        est = estimate_monthly_revenue(vertical, monthly_visitors=2000)
        click.echo(
            f"  {vertical:<25} {est.get('program','?'):<20} "
            f"${est.get('monthly_est',0):>7.0f}/mo  "
            f"(${est.get('yearly_est',0):>8.0f}/yr)  "
            f"{programs[0]['commission'] if programs else ''}"
        )
    click.echo("")


@cli.command()
def health():
    """Full health check — bot status, quota, pages, revenue, action items."""
    import time
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.rule import Rule

    TODAY = time.strftime("%Y-%m-%d")
    NOW = int(time.time())
    DAY_SECS = 86400

    console.print(Rule(f"[bold cyan]Intent Engine Health Check[/] [dim]{TODAY}[/]"))

    try:
        from core.db import db
        with db() as conn:
            # --- Signals ---
            raw_total   = conn.execute("SELECT COUNT(*) FROM raw_signals").fetchone()[0]
            raw_today   = conn.execute("SELECT COUNT(*) FROM raw_signals WHERE fetched_at>?", (NOW-DAY_SECS,)).fetchone()[0]
            pending     = conn.execute("SELECT COUNT(*) FROM raw_signals WHERE processed=0").fetchone()[0]
            scored_total= conn.execute("SELECT COUNT(*) FROM scored_signals").fetchone()[0]

            # --- Pages ---
            pages_total = conn.execute("SELECT COUNT(*) FROM outputs").fetchone()[0]
            pages_today = conn.execute("SELECT COUNT(*) FROM outputs WHERE created_at>?", (NOW-DAY_SECS,)).fetchone()[0]
            revenue_db  = conn.execute("SELECT COALESCE(SUM(revenue),0) FROM outputs").fetchone()[0]

            # --- Quota ---
            quota_rows  = conn.execute(
                "SELECT provider, tokens_used FROM daily_quota WHERE date=?", (TODAY,)
            ).fetchall()
            quota = {r["provider"]: r["tokens_used"] for r in quota_rows}

            # --- Recent runs ---
            runs = conn.execute(
                "SELECT job, status, started_at, signals_out, error FROM runs ORDER BY started_at DESC LIMIT 5"
            ).fetchall()

            # --- Top verticals ---
            verticals = conn.execute("""
                SELECT vertical, COUNT(*) as pages, COALESCE(SUM(revenue),0) as rev
                FROM outputs GROUP BY vertical ORDER BY pages DESC LIMIT 8
            """).fetchall()

            # --- LLM failures ---
            lf = conn.execute("""
                SELECT COUNT(*) FROM runs WHERE status='error' AND started_at>?
            """, (NOW - 3*DAY_SECS,)).fetchone()[0]

    except Exception as e:
        console.print(f"[red]DB error: {e}[/]")
        return

    DAILY_LIMITS = {
        "cerebras_qwen": 900_000,
        "cerebras_8b":   900_000,
        "groq_70b":       90_000,
        "groq_8b":        50_000,
        "groq_3b":        80_000,
        "openrouter":    200_000,
    }

    def status_icon(ok): return "[green]✓[/]" if ok else "[red]✗[/]"
    def pct_bar(used, limit, width=12):
        pct = min(used / limit, 1.0) if limit else 0
        filled = int(pct * width)
        color = "green" if pct < 0.7 else "yellow" if pct < 0.9 else "red"
        return f"[{color}]{'█'*filled}{'░'*(width-filled)}[/] {pct*100:.0f}%"

    # === SECTION 1: Signals ===
    sig_ok = raw_today > 0
    sig_table = Table(show_header=False, box=None, padding=(0,1))
    sig_table.add_row("Total signals",   str(raw_total))
    sig_table.add_row("Signals today",   f"[{'green' if raw_today>0 else 'red'}]{raw_today}[/]")
    sig_table.add_row("Pending scoring", f"[{'yellow' if pending>0 else 'green'}]{pending}[/]")
    sig_table.add_row("Scored total",    str(scored_total))

    # === SECTION 2: Pages ===
    page_ok = pages_today > 0
    page_table = Table(show_header=False, box=None, padding=(0,1))
    page_table.add_row("Total pages",   str(pages_total))
    page_table.add_row("Pages today",   f"[{'green' if pages_today>0 else 'yellow'}]{pages_today}[/]")
    page_table.add_row("Revenue (DB)",  f"[green]${revenue_db:.2f}[/]")

    # === SECTION 3: LLM Quota ===
    quota_table = Table(show_header=True, box=None, padding=(0,1))
    quota_table.add_column("Provider", style="cyan")
    quota_table.add_column("Usage", min_width=20)
    quota_table.add_column("Remaining")
    for provider, limit in DAILY_LIMITS.items():
        used = quota.get(provider, 0)
        remaining = max(0, limit - used)
        quota_table.add_row(provider, pct_bar(used, limit), f"{remaining:,}")

    # === SECTION 4: Recent Runs ===
    runs_table = Table(show_header=True, box=None, padding=(0,1))
    runs_table.add_column("Job", style="cyan")
    runs_table.add_column("Status")
    runs_table.add_column("Time")
    runs_table.add_column("Out")
    for r in runs:
        ago = int((NOW - r["started_at"]) / 60)
        ago_str = f"{ago}m ago" if ago < 120 else f"{ago//60}h ago"
        status_color = "green" if r["status"] == "ok" else "red" if r["status"] == "error" else "yellow"
        runs_table.add_row(
            r["job"],
            f"[{status_color}]{r['status']}[/]",
            ago_str,
            str(r["signals_out"] or 0),
        )

    # === SECTION 5: Verticals ===
    vert_table = Table(show_header=True, box=None, padding=(0,1))
    vert_table.add_column("Vertical", style="cyan")
    vert_table.add_column("Pages", justify="right")
    vert_table.add_column("Revenue", justify="right")
    for v in verticals:
        vert_table.add_row(v["vertical"] or "?", str(v["pages"]), f"${v['rev']:.2f}")

    # === SECTION 6: Action Items ===
    actions = []
    if pending > 20:
        actions.append(f"[yellow]⚠[/]  {pending} signals pending — run [bold]engine score[/]")
    if pages_today == 0:
        actions.append("[yellow]⚠[/]  No pages generated today — check GitHub Actions logs")
    if lf > 0:
        actions.append(f"[red]✗[/]  {lf} failed runs in last 3 days — check [bold]engine health[/] run log above")
    if not quota.get("cerebras_qwen") and not quota.get("groq_70b"):
        actions.append("[dim]ℹ[/]  No LLM quota recorded today — first run may not have happened yet")
    if revenue_db == 0:
        actions.append("[dim]ℹ[/]  $0 revenue in DB — check affiliate dashboards manually")
    if not actions:
        actions.append("[green]✓[/]  All systems nominal — nothing to do")

    # Render
    console.print()
    console.print(Panel(sig_table,   title=f"{status_icon(sig_ok)} Signals",   border_style="cyan"))
    console.print(Panel(page_table,  title=f"{status_icon(page_ok)} Pages",    border_style="cyan"))
    console.print(Panel(quota_table, title="[cyan]LLM Quota Today[/]",          border_style="blue"))
    if runs:
        console.print(Panel(runs_table, title="[cyan]Recent Runs[/]",           border_style="blue"))
    console.print(Panel(vert_table,  title="[cyan]Verticals[/]",                border_style="blue"))

    action_text = Text()
    for a in actions:
        action_text.append_text(Text.from_markup(a + "\n"))
    console.print(Panel(action_text, title="[bold yellow]Action Items[/]",       border_style="yellow"))

    console.print()
    console.print("[dim]Scheduled agents → https://claude.ai/code/scheduled[/]")
    console.print("[dim]GitHub Actions   → https://github.com/[your-repo]/actions[/]")
    console.print("[dim]Amazon Associates → https://affiliate-program.amazon.com/home/summary[/]")
    console.print()


if __name__ == "__main__":
    cli()
