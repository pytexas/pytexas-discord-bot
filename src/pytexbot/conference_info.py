import importlib.resources
import tomllib
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

import discord


@dataclass
class CFPConfig:
    open_date: date | None = None
    close_date: date | None = None
    url: str | None = None


@dataclass
class ConferenceConfig:
    name: str
    start_date: date
    end_date: date
    description: str = ""
    location: str | None = None
    website: str | None = None
    tickets_url: str | None = None
    tickets_open_date: date | None = None
    cfp: CFPConfig = field(default_factory=CFPConfig)


def _load_config() -> ConferenceConfig:
    config_file = importlib.resources.files("pytexbot").joinpath("conference_info.toml")
    with config_file.open("rb") as f:
        raw = tomllib.load(f)

    cfp_raw = raw.get("cfp", {})
    conf_raw = raw["conference"]

    return ConferenceConfig(
        name=conf_raw["name"],
        start_date=conf_raw["start_date"],
        end_date=conf_raw["end_date"],
        description=conf_raw.get("description", ""),
        location=conf_raw.get("location"),
        website=conf_raw.get("website"),
        tickets_url=conf_raw.get("tickets_url"),
        tickets_open_date=conf_raw.get("tickets_open_date"),
        cfp=CFPConfig(
            open_date=cfp_raw.get("open_date"),
            close_date=cfp_raw.get("close_date"),
            url=cfp_raw.get("url"),
        ),
    )


def _to_unix(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, 12, tzinfo=timezone.utc).timestamp())


def build_conference_embed() -> discord.Embed:
    conf = _load_config()
    today = date.today()

    start_ts = _to_unix(conf.start_date)
    end_ts = _to_unix(conf.end_date)

    embed = discord.Embed(
        title=conf.name,
        url=conf.website or "https://pytexas.org",
        description=conf.description,
        color=0x7B4EA0,
    )

    embed.add_field(
        name="📅 Conference Dates",
        value=f"<t:{start_ts}:D> – <t:{end_ts}:D> (<t:{start_ts}:R>)",
        inline=False,
    )

    if conf.location:
        embed.add_field(name="📍 Location", value=conf.location, inline=True)

    if conf.website:
        embed.add_field(name="🌐 Website", value=conf.website, inline=True)

    cfp = conf.cfp
    if cfp.open_date is None:
        cfp_value = "CFP dates TBA"
    elif today < cfp.open_date:
        ts = _to_unix(cfp.open_date)
        cfp_value = f"Opens <t:{ts}:D> (<t:{ts}:R>)"
    elif cfp.close_date is None or today <= cfp.close_date:
        cfp_value = "**CFP is open now!**"
        if cfp.close_date:
            ts = _to_unix(cfp.close_date)
            cfp_value += f"\nCloses <t:{ts}:D> (<t:{ts}:R>)"
    else:
        cfp_value = "CFP is closed"

    if cfp.url:
        cfp_value += f"\n[Submit a proposal]({cfp.url})"

    embed.add_field(name="📋 Call for Proposals", value=cfp_value, inline=False)

    if conf.tickets_url:
        if conf.tickets_open_date and today < conf.tickets_open_date:
            ts = _to_unix(conf.tickets_open_date)
            ticket_value = f"Sales open <t:{ts}:D> (<t:{ts}:R>)"
        else:
            ticket_value = f"[Get your tickets!]({conf.tickets_url})"
        embed.add_field(name="🎟️ Tickets", value=ticket_value, inline=False)
    elif conf.tickets_open_date:
        ts = _to_unix(conf.tickets_open_date)
        embed.add_field(
            name="🎟️ Tickets",
            value=f"Sales open <t:{ts}:D> (<t:{ts}:R>)",
            inline=False,
        )

    return embed
