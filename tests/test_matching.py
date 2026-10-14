"""Юнит-тесты алгоритма совместимости анкет (UC-5)."""

from app.db.models import BadHabits, Hobbies, Preferences, Profile
from app.services.matching import compute_compatibility


def _profile(age=25, gender="male", city="Москва", district="Центральный", metro="Охотный Ряд"):
    return Profile(
        id=None,
        user_id=None,
        first_name="Тест",
        last_name="Тестов",
        age=age,
        gender=gender,
        city=city,
        district=district,
        metro_station=metro,
    )


def _prefs(**overrides):
    data = {
        "age_min": 18,
        "age_max": 40,
        "gender_preference": "any",
        "budget_max": 50000,
        "city_preference": "Москва",
        "district_preference": ["Центральный"],
        "metro_preference": ["Охотный Ряд"],
        "smoking_preference": "any",
        "pets_preference": "any",
        "guests_preference": "any",
        "sleep_mode_preference": "any",
        "noise_preference": "any",
    }
    data.update(overrides)
    return Preferences(**data)


def test_without_preferences_returns_zero():
    assert compute_compatibility(None, _profile(), None, None, None) == 0


def test_perfect_match_is_100():
    prefs = _prefs()
    habits = BadHabits(
        smoking=False, pets=False, sleep_mode="early", noise_preference="quiet", guests=False
    )
    hobbies = Hobbies(films=True, music=True)
    score = compute_compatibility(prefs, _profile(), habits, hobbies, hobbies)
    assert score == 100


def test_age_out_of_range_lowers_score():
    prefs = _prefs(age_min=30, age_max=35)
    perfect = compute_compatibility(prefs, _profile(age=32), None, None, None)
    too_young = compute_compatibility(prefs, _profile(age=25), None, None, None)
    assert too_young < perfect


def test_gender_preference_respected():
    prefs = _prefs(gender_preference="female")
    male = compute_compatibility(prefs, _profile(gender="male"), None, None, None)
    female = compute_compatibility(prefs, _profile(gender="female"), None, None, None)
    assert male < female


def test_hobby_overlap_affects_score():
    prefs = _prefs()
    liked = Hobbies(films=True, music=True)
    other = Hobbies(films=True, sports=True)
    same = compute_compatibility(prefs, _profile(), None, liked, liked)
    partial = compute_compatibility(prefs, _profile(), None, liked, other)
    assert partial < same
