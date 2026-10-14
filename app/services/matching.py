"""Расчёт процента совместимости анкет (UC-5).

Алгоритм сравнивает предпочтения ищущего (``viewer``) с данными кандидата и
возвращает целое число 0..100. Каждый критерий имеет равный вес.
"""

from app.db.models import BadHabits, Hobbies, Preferences, Profile

HOBBY_FIELDS = (
    "films",
    "music",
    "sports",
    "reading",
    "gaming",
    "books",
    "photography",
    "cooking",
    "arts",
    "table_games",
    "travel",
    "walking",
    "dancing",
    "singing",
)


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def _locations_match(prefs: Preferences, profile: Profile) -> bool:
    districts = {_norm(item) for item in (prefs.district_preference or [])}
    metros = {_norm(item) for item in (prefs.metro_preference or [])}
    return _norm(profile.district) in districts or _norm(profile.metro_station) in metros


def _hobby_overlap(first: Hobbies | None, second: Hobbies | None) -> float:
    if first is None or second is None:
        return 0.0
    first_set = {field for field in HOBBY_FIELDS if getattr(first, field)}
    second_set = {field for field in HOBBY_FIELDS if getattr(second, field)}
    union = first_set | second_set
    if not union:
        return 1.0
    return len(first_set & second_set) / len(union)


def compute_compatibility(
    viewer_prefs: Preferences | None,
    candidate: Profile,
    candidate_bad: BadHabits | None,
    viewer_hobbies: Hobbies | None,
    candidate_hobbies: Hobbies | None,
) -> int:
    """Вернуть процент совместимости кандидата с предпочтениями ищущего."""
    if viewer_prefs is None:
        return 0

    score = 0.0
    total = 0.0

    total += 1
    if viewer_prefs.age_min <= candidate.age <= viewer_prefs.age_max:
        score += 1

    total += 1
    if viewer_prefs.gender_preference in ("any", candidate.gender):
        score += 1

    total += 1
    if _norm(viewer_prefs.city_preference) == _norm(candidate.city):
        score += 1

    total += 1
    if _locations_match(viewer_prefs, candidate):
        score += 1

    for pref_attr, habit_attr in (
        ("smoking_preference", "smoking"),
        ("pets_preference", "pets"),
        ("guests_preference", "guests"),
    ):
        pref = getattr(viewer_prefs, pref_attr)
        if pref != "any":
            total += 1
            want = pref == "yes"
            if candidate_bad is not None and bool(getattr(candidate_bad, habit_attr)) == want:
                score += 1

    if viewer_prefs.sleep_mode_preference != "any":
        total += 1
        if (
            candidate_bad is not None
            and candidate_bad.sleep_mode == viewer_prefs.sleep_mode_preference
        ):
            score += 1

    total += 1
    score += _hobby_overlap(viewer_hobbies, candidate_hobbies)

    return int(round(100 * score / total))
