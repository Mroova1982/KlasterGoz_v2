import pytest

from apps.cluster.models import Member, TeamMember, Partner


@pytest.mark.django_db
def test_member_initials_and_str():
    m = Member.objects.create(name="Stena Recycling", slug="stena", sector="recykling")
    assert m.initials() == "SR"
    assert str(m) == "Stena Recycling"


@pytest.mark.django_db
def test_member_ordering_alphabetical():
    Member.objects.create(name="Zeta", slug="zeta")
    Member.objects.create(name="Alfa", slug="alfa")
    assert list(Member.objects.values_list("name", flat=True)) == ["Alfa", "Zeta"]


@pytest.mark.django_db
def test_teammember_group_and_order():
    TeamMember.objects.create(name="Jan Kowalski", group="zarzad", sort_order=1)
    TeamMember.objects.create(name="Anna Nowak", group="zarzad", sort_order=0)
    first = TeamMember.objects.filter(group="zarzad").first()
    assert first.name == "Anna Nowak"
    assert first.initials() == "AN"


@pytest.mark.django_db
def test_partner_type_choices():
    p = Partner.objects.create(name="PARP", type="instytucja")
    assert p.get_type_display() == "Instytucja publiczna"
