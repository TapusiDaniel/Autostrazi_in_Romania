from config import TIMELINE_END_YEAR, TIMELINE_PRESENT_YEAR, TIMELINE_START_YEAR


def calculate_km_by_year(highways):
    yearly_km = {}

    def parse_completion_year(section):
        status = section.get("status")
        projected_date = section.get("projected_completion_date")
        if projected_date:
            try:
                clean_date = str(projected_date).replace("~", "").strip()
                return int(clean_date[:4])
            except (ValueError, TypeError):
                pass

        if status in ("finished", "in_construction"):
            completion_date = section.get("completion_date", "")
            try:
                return int(str(completion_date)[:4])
            except (ValueError, TypeError):
                return None

        if status == "tendered":
            try:
                tender_year = int(section.get("tender_end_date", "2026"))
                duration_str = section.get("construction_duration", "0 de luni")
                months = int(duration_str.split()[0])
                years = months / 12
                return int(tender_year + years)
            except (ValueError, TypeError, AttributeError):
                return TIMELINE_END_YEAR

        if status == "planned":
            return TIMELINE_END_YEAR

        return None

    for highway in highways.values():
        for section in highway.get("sections", {}).values():
            year = parse_completion_year(section)
            if year:
                length_str = section.get("length", "0 km")
                try:
                    length = float(length_str.replace(" km", "").replace(",", "."))
                    yearly_km[year] = yearly_km.get(year, 0) + length
                except (ValueError, TypeError):
                    continue

    return yearly_km


def calculate_current_state_total(highways):
    total = 0
    for highway in highways.values():
        for section in highway.get("sections", {}).values():
            if section.get("status") != "finished":
                continue

            length_str = section.get("length", "0 km")
            try:
                total += float(length_str.replace(" km", "").replace(",", "."))
            except (ValueError, TypeError):
                continue

    return round(total, 2)


def build_timeline_payload(highways):
    yearly_km = calculate_km_by_year(highways)

    cumulative_data = {}
    cumulative = 0
    for year in range(TIMELINE_START_YEAR, TIMELINE_END_YEAR + 1):
        if year in yearly_km:
            cumulative += yearly_km[year]
        cumulative_data[year] = round(cumulative, 2)

    current_state_total = calculate_current_state_total(highways)

    payload = {
        "timelineData": {
            y: km
            for y, km in sorted(cumulative_data.items())
            if y >= TIMELINE_START_YEAR
        },
        "yearlyAdditions": {
            y: km for y, km in sorted(yearly_km.items()) if y >= TIMELINE_START_YEAR
        },
        "currentStateTotal": current_state_total,
        "presentYear": TIMELINE_PRESENT_YEAR,
    }
    return payload, current_state_total
