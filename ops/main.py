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


if __name__ == "__main__":
    cli()
