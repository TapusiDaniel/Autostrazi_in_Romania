from datetime import datetime

from config import (
    DNS_PREFETCH_URLS,
    META_AUTHOR,
    META_DESCRIPTION,
    META_KEYWORDS,
    META_ROBOTS,
    META_TITLE,
    PRECONNECT_URLS,
    ROMANIAN_MONTHS,
    TIMELINE_LABELS,
    TIMELINE_LABEL_POSITIONS,
    TIMELINE_SLIDER_DEFAULT,
)
from utils.template_loader import render_template


def build_meta_tags():
    resource_hints = []
    for url in PRECONNECT_URLS:
        resource_hints.append(f'<link rel="preconnect" href="{url}" crossorigin>')
    for url in DNS_PREFETCH_URLS:
        resource_hints.append(f'<link rel="dns-prefetch" href="{url}">')
    resource_hints_html = "\n".join(resource_hints)

    return render_template(
        "meta_tags",
        meta_title=META_TITLE,
        meta_description=META_DESCRIPTION,
        meta_keywords=META_KEYWORDS,
        meta_author=META_AUTHOR,
        meta_robots=META_ROBOTS,
        resource_hints=resource_hints_html,
    )


def build_skip_link():
    return render_template("skip_link")


def build_map_controls():
    return render_template("map_controls")


def build_dark_mode_toggle():
    return render_template("dark_mode_toggle")


def build_loading_overlay():
    return render_template("loading_overlay")


def build_ux_enhancements():
    return render_template("ux_enhancements")


def build_sidebar(items_html):
    return render_template("sidebar", items=items_html)


def build_timeline(timeline_payload_json, current_state_total):
    labels = []
    for idx, label in enumerate(TIMELINE_LABELS):
        if idx < len(TIMELINE_LABEL_POSITIONS):
            pos = TIMELINE_LABEL_POSITIONS[idx]
            offset = 10 - (20 * pos / 100)
            labels.append(
                f'<span style="left: calc({pos}% + {offset:g}px)">{label}</span>'
            )
        else:
            labels.append(f"<span>{label}</span>")
    labels_html = "\n".join(labels)
    return render_template(
        "timeline",
        timeline_payload_json=timeline_payload_json,
        current_state_total=current_state_total,
        timeline_labels=labels_html,
        timeline_slider_default=TIMELINE_SLIDER_DEFAULT,
    )


def build_update_footer():
    now = datetime.now()
    last_update = f"{now.day} {ROMANIAN_MONTHS[now.month]} {now.year}"
    return render_template("update_info", last_update=last_update)
