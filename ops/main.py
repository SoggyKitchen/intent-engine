import click
from rich.console import Console
from rich.table import Table

console = Console(force_terminal=True, highlight=False, safe_box=True)


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
    from ops.harvest import run

    migrate()
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
    from learn.optimize import run_daily_optimization
    from ops.harvest import run as harvest_run
    from ops.publish_job import run as publish_run
    from ops.score_job import run as score_run

    migrate()
    click.echo("Running full pipeline...")
    harvested = harvest_run()
    click.echo(f"  Harvested: {harvested}")
    scored = score_run()
    click.echo(f"  Scored: {scored}")
    publish_run()
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
    """Post comparison pages to Twitter/X, LinkedIn, and Reddit."""
    from ops.social_post import build_social_pack, run_linkedin, run_reddit_answers, run_twitter

    build_social_pack()
    run_twitter()
    run_linkedin()
    run_reddit_answers()
    click.echo("OK  Social posting done")


@cli.command()
def backlinks():
    """Submit new pages to IndexNow and build backlink queue."""
    from ops.backlink_submit import run

    run()
    click.echo("OK  Backlink submission done")


@cli.command("youtube-bridge")
def youtube_bridge():
    """Build the SaaSpare page manifest used by the YouTube content engine."""
    from scripts.youtube_bridge import write_manifest

    data = write_manifest()
    click.echo(f"OK  YouTube bridge manifest refreshed ({data['total']} pages)")


@cli.command("import-links")
@click.option("--csv", "csv_path", required=True, help="Path to affiliate links CSV export")
@click.option("--output", "output_path", default="", help="Optional output JSON path")
def import_links(csv_path: str, output_path: str):
    """Import affiliate tracking links from a CSV export and rebuild redirect state."""
    from publisher.affiliate_importer import import_affiliate_bundle
    from publisher.affiliate_registry import clear_imported_affiliate_cache, write_redirects_file

    summary = import_affiliate_bundle(csv_path, links_path=output_path or "data/affiliate_links.json")
    clear_imported_affiliate_cache()
    redirect_count = write_redirects_file()
    click.echo(
        "OK  Imported affiliate links: "
        f"{summary['links_summary']['advertiser_count']} advertisers -> {summary['links_path']} | "
        f"{summary['overrides_summary']['links_selected']} curated overrides -> {summary['overrides_path']} | "
        f"{redirect_count} redirects rebuilt"
    )


@cli.command("import-affiliates")
@click.option(
    "--csv",
    "csv_path",
    default=r"C:\Users\smith\Downloads\links.csv",
    show_default=True,
    help="Path to a CJ/affiliate CSV export.",
)
def import_affiliates(csv_path: str):
    """Backward-compatible alias for the full affiliate CSV import."""
    ctx = click.get_current_context()
    ctx.invoke(import_links, csv_path=csv_path, output_path="")


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
    else:
        click.echo("OK  No new programmatic pages generated; site artifacts refreshed")


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


@cli.command("profit-audit")
@click.option("--limit", default=12, show_default=True, help="Max rows per section")
def profit_audit(limit: int):
    """Show monetization coverage, CTA leaks, and partner gaps."""
    from ops.profit_audit import collect_profit_audit

    audit = collect_profit_audit(max_gap_items=limit)

    click.echo("\n=== Profit Audit ===")
    click.echo(f"  SEO pages scanned:        {audit['page_count']}")
    click.echo(f"  Pages with /go/ CTA:      {audit['pages_with_cta']}")
    click.echo(f"  CTA coverage:             {audit['cta_coverage_pct']:.1f}%")
    click.echo(f"  Redirects available:      {audit['redirect_count']}")
    click.echo(f"  Imported CJ advertisers:  {audit['imported_affiliate_count']}")

    click.echo("\n  Pages missing affiliate CTA:")
    if audit["pages_without_go_cta"]:
        for item in audit["pages_without_go_cta"]:
            click.echo(f"    - {item['title']}  [{item['page_type']}]")
        if audit["pages_without_go_cta_total"] > len(audit["pages_without_go_cta"]):
            click.echo(f"    ... and {audit['pages_without_go_cta_total'] - len(audit['pages_without_go_cta'])} more")
    else:
        click.echo("    - none")

    click.echo("\n  High-value tools with pages but no default redirect:")
    if audit["missing_partner_targets"]:
        for item in audit["missing_partner_targets"]:
            suffix = f" ({item['page_count']} live pages)" if item["page_count"] else ""
            click.echo(f"    - {item['tool']} [{item['vertical']}]{suffix}")
        if audit["missing_partner_targets_total"] > len(audit["missing_partner_targets"]):
            click.echo(f"    ... and {audit['missing_partner_targets_total'] - len(audit['missing_partner_targets'])} more")
    else:
        click.echo("    - none")

    click.echo("\n  Coupon pages without coupon-specific redirect:")
    if audit["missing_coupon_targets"]:
        for item in audit["missing_coupon_targets"]:
            suffix = f" ({item['page_count']} live pages)" if item["page_count"] else ""
            click.echo(f"    - {item['tool']} [{item['vertical']}]{suffix}")
        if audit["missing_coupon_targets_total"] > len(audit["missing_coupon_targets"]):
            click.echo(f"    ... and {audit['missing_coupon_targets_total'] - len(audit['missing_coupon_targets'])} more")
    else:
        click.echo("    - none")

    if audit["network_signups"]:
        click.echo("\n  Networks to prioritize for missing coverage:")
        for network in audit["network_signups"]:
            click.echo(f"    - {network['name']}: {network['signup_url']}")
    click.echo("")


@cli.command()
def health():
    """Full health check - bot status, quota, pages, revenue, action items."""
    import subprocess
    import time
    from pathlib import Path
    from rich.align import Align
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.text import Text

    today = time.strftime("%Y-%m-%d")
    now = int(time.time())
    day_secs = 86400

    console.print()
    console.print(Rule(f"[bold cyan] Intent Engine Health [/]  [dim]{today} {time.strftime('%H:%M')}[/]"))
    console.print()

    from llm.router import configured_provider_count, quota_status as llm_quota_status

    try:
        from core.db import db

        with db() as conn:
            raw_total = conn.execute("SELECT COUNT(*) FROM raw_signals").fetchone()[0]
            raw_today = conn.execute(
                "SELECT COUNT(*) FROM raw_signals WHERE fetched_at>?",
                (now - day_secs,),
            ).fetchone()[0]
            pending = conn.execute("SELECT COUNT(*) FROM raw_signals WHERE processed=0").fetchone()[0]
            scored_total = conn.execute("SELECT COUNT(*) FROM scored_signals").fetchone()[0]
            runs = conn.execute(
                "SELECT job, status, started_at, signals_out, error FROM runs ORDER BY started_at DESC LIMIT 6"
            ).fetchall()
            verticals = conn.execute("""
                SELECT vertical, COUNT(*) as pages, COALESCE(SUM(revenue),0) as rev
                FROM outputs
                WHERE type = 'seo_page'
                GROUP BY vertical
                ORDER BY pages DESC
                LIMIT 10
            """).fetchall()
            lf = conn.execute(
                "SELECT COUNT(*) FROM runs WHERE status='error' AND started_at>?",
                (now - 3 * day_secs,),
            ).fetchone()[0]
    except Exception as e:
        console.print(f"[red bold]DB error: {e}[/]")
        return

    pages_dir = Path("site/pages")
    page_files = []
    if pages_dir.exists():
        page_files = [
            path for path in pages_dir.glob("*.html")
            if path.stem not in {"index", "thanks", "verification"}
        ]
    pages_total = len(page_files)
    pages_today = sum(1 for path in page_files if (now - int(path.stat().st_mtime)) <= day_secs)
    pages_week = sum(1 for path in page_files if (now - int(path.stat().st_mtime)) <= 7 * day_secs)

    provider_quota = llm_quota_status()
    provider_count = configured_provider_count()
    total_quota_used = sum(item["used"] for item in provider_quota.values())
    total_quota_limit = sum(item["limit"] for item in provider_quota.values())

    def pct_bar(used, limit, width=14):
        pct = min(used / limit, 1.0) if limit else 0
        filled = int(pct * width)
        color = "green" if pct < 0.6 else "yellow" if pct < 0.85 else "red"
        return f"[{color}]{'#' * filled}[dim]{'.' * (width - filled)}[/] {pct*100:.0f}%"

    def ok(value):
        return f"[green]{value}[/]"

    def warn(value):
        return f"[yellow]{value}[/]"

    def bad(value):
        return f"[red bold]{value}[/]"

    from ops.profit_audit import collect_profit_audit

    profit = collect_profit_audit(max_gap_items=5)

    score_pts = 0
    score_pts += 2 if raw_today > 0 else 0
    score_pts += 2 if pages_today > 0 else 0
    score_pts += 1 if pending < 50 else 0
    score_pts += 2 if lf == 0 else 0
    score_pts += 1 if total_quota_limit == 0 or total_quota_used < total_quota_limit * 0.85 else 0
    score_pts += 2 if pages_total >= 10 else (1 if pages_total > 0 else 0)
    grade = {10: "A", 9: "A", 8: "B", 7: "B", 6: "C", 5: "C"}.get(score_pts, "D" if score_pts >= 3 else "F")
    grade_color = {"A": "green", "B": "cyan", "C": "yellow", "D": "orange1", "F": "red"}[grade]
    console.print(Align.center(f"[bold {grade_color}] HEALTH SCORE: {grade} ({score_pts}/10) [/]"))
    console.print()

    pipe_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    pipe_table.add_column(width=22)
    pipe_table.add_column()
    pipe_table.add_row("[cyan]Signals today[/]", ok(raw_today) if raw_today > 0 else warn("0  - harvester may be down"))
    pipe_table.add_row("[cyan]Signals total[/]", str(raw_total))
    pipe_table.add_row("[cyan]Pending scoring[/]", ok(pending) if pending < 20 else warn(f"{pending}  run: engine score"))
    pipe_table.add_row("[cyan]Scored total[/]", str(scored_total))
    pipe_table.add_row("[cyan]Pages today[/]", ok(pages_today) if pages_today > 0 else warn("0  - check GitHub Actions"))
    pipe_table.add_row("[cyan]Pages this week[/]", ok(pages_week) if pages_week >= 5 else warn(str(pages_week)))
    pipe_table.add_row("[cyan]Pages total[/]", ok(pages_total) if pages_total > 0 else bad("0"))
    pipe_table.add_row(
        "[cyan]CTA coverage[/]",
        ok(f"{profit['cta_coverage_pct']:.1f}%") if profit["pages_without_go_cta_total"] == 0 else warn(
            f"{profit['cta_coverage_pct']:.1f}%  ({profit['pages_without_go_cta_total']} missing)"
        ),
    )
    pipe_table.add_row("[cyan]Run failures (3d)[/]", ok("0") if lf == 0 else bad(str(lf)))
    console.print(Panel(pipe_table, title="[bold]Pipeline[/]", border_style="cyan"))

    quota_table = Table(show_header=True, box=None, padding=(0, 2), expand=True)
    quota_table.add_column("Provider", style="cyan", width=24)
    quota_table.add_column("Used today", min_width=20)
    quota_table.add_column("Remaining", justify="right")
    if provider_quota:
        for provider, stats in provider_quota.items():
            used = stats["used"]
            limit = stats["limit"]
            remaining = max(0, limit - used)
            quota_table.add_row(provider, pct_bar(used, limit), f"[dim]{remaining:,}[/]")
    total_pct = total_quota_used / total_quota_limit if total_quota_limit else 0
    quota_table.add_row(
        "[bold]TOTAL[/]",
        pct_bar(total_quota_used, total_quota_limit),
        f"[bold]{max(0, total_quota_limit - total_quota_used):,}[/]",
    )
    console.print(Panel(quota_table, title="[bold]LLM Quota Today[/]", border_style="blue"))

    if runs:
        runs_table = Table(show_header=True, box=None, padding=(0, 2), expand=True)
        runs_table.add_column("Job", style="cyan", width=20)
        runs_table.add_column("Status", width=10)
        runs_table.add_column("When", width=10)
        runs_table.add_column("Output", justify="right")
        for row in runs:
            ago = int((now - row["started_at"]) / 60)
            ago_str = f"{ago}m ago" if ago < 120 else f"{ago // 60}h ago"
            color = "green" if row["status"] == "ok" else "red" if row["status"] == "error" else "yellow"
            runs_table.add_row(
                row["job"],
                f"[{color}]{row['status']}[/]",
                f"[dim]{ago_str}[/]",
                str(row["signals_out"] or 0),
            )
        console.print(Panel(runs_table, title="[bold]Recent Pipeline Runs[/]", border_style="blue"))

    from publisher.affiliate_registry import get_best_programs_for_vertical

    vert_table = Table(show_header=True, box=None, padding=(0, 2), expand=True)
    vert_table.add_column("Vertical", style="cyan", width=22)
    vert_table.add_column("Pages", justify="right", width=7)
    vert_table.add_column("Top program", width=20)
    vert_table.add_column("Commission", width=20)
    vert_table.add_column("Est $/conv", justify="right")
    for vertical in verticals:
        vname = vertical["vertical"] or "?"
        prog = get_best_programs_for_vertical(vname, top_n=1)
        if prog:
            item = prog[0]
            pct = item.get("commission_pct", 0)
            avg = item.get("avg_plan_usd", 0)
            months = 12 if item.get("recurring") else 1
            est = (pct / 100) * avg * months
            est_str = f"[green]${est:.0f}[/]" if est > 50 else f"[yellow]${est:.0f}[/]" if est > 0 else "[red]$0[/]"
            vert_table.add_row(vname, str(vertical["pages"]), item["name"], item["commission"], est_str)
        else:
            vert_table.add_row(vname, str(vertical["pages"]), "[red]NONE[/]", "-", "[red]$0[/]")
    console.print(Panel(vert_table, title="[bold]Verticals + Affiliate Potential[/]", border_style="blue"))

    try:
        git_log = subprocess.check_output(
            ["git", "log", "--oneline", "--no-merges", "-8"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        git_text = Text()
        for line in git_log.split("\n"):
            sha, _, msg = line.partition(" ")
            color = "dim" if "[skip ci]" in msg or "chore: programmatic" in msg or "chore: harvest" in msg else "white"
            git_text.append(f"  {sha}  ", style="cyan")
            git_text.append(msg + "\n", style=color)
        console.print(Panel(git_text, title="[bold]Recent Git Commits[/]", border_style="dim"))
    except Exception:
        pass

    actions = []
    if raw_today == 0:
        actions.append(("[red][ERR][/]", "No signals today - harvester may be down or GitHub Actions not running"))
    if pages_today == 0 and pages_total > 0:
        actions.append(("[yellow][WARN][/]", "No new pages today - check GitHub Actions"))
    if pages_total == 0:
        actions.append(("[red][ERR][/]", "Zero pages ever - run: uv run engine programmatic --max-pages 50"))
    if pending > 50:
        actions.append(("[yellow][WARN][/]", f"{pending} signals unscored - run: uv run engine score"))
    if lf > 0:
        actions.append(("[red][ERR][/]", f"{lf} pipeline failures in last 3 days - check runs table above for errors"))
    if profit["pages_without_go_cta_total"] > 0:
        actions.append((
            "[yellow][WARN][/]",
            f"{profit['pages_without_go_cta_total']} pages missing affiliate CTA - run: uv run engine profit-audit",
        ))
    if profit["missing_partner_targets_total"] > 0:
        actions.append((
            "[yellow][WARN][/]",
            f"{profit['missing_partner_targets_total']} high-value tools still have no default redirect - prioritize partner coverage",
        ))
    if provider_count == 0:
        actions.append(("[red][ERR][/]", "No Cerebras API keys configured - check CEREBRAS_API_KEY secrets/env vars"))
    elif total_quota_used == 0:
        actions.append(("[dim][INFO][/]", "No LLM quota recorded today - first run has not fired yet or nothing needed scoring"))
    if total_pct > 0.9:
        actions.append(("[yellow][WARN][/]", f"LLM quota at {total_pct*100:.0f}% - reduce max-pages or wait until midnight UTC"))
    if not actions:
        actions.append(("[green][OK][/]", "All systems nominal - nothing to do"))

    action_text = Table(show_header=False, box=None, padding=(0, 1), expand=True)
    action_text.add_column(width=10)
    action_text.add_column()
    for icon, msg in actions:
        action_text.add_row(icon, msg)
    console.print(Panel(action_text, title="[bold yellow] Action Items [/]", border_style="yellow"))

    console.print()
    console.print("  [dim bold]Dashboards to check manually:[/]")
    console.print("  [dim]-> GitHub Actions    https://github.com/SoggyKitchen/intent-engine/actions[/]")
    console.print("  [dim]-> Scheduled agents  https://claude.ai/code/scheduled[/]")
    console.print("  [dim]-> Semrush affiliate https://www.semrush.com/partner/[/]")
    console.print("  [dim]-> PartnerStack      https://app.partnerstack.com[/]")
    console.print("  [dim]-> Impact.com        https://app.impact.com[/]")
    console.print("  [dim]-> ShareASale        https://www.shareasale.com[/]")
    console.print()


if __name__ == "__main__":
    cli()
