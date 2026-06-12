# apps.cluster

Filar Klaster — ludzie i organizacja.

## Co robi
- Snippety (reużywalne): `Member` (członek; sektor, logo, WWW, initials()), `TeamMember` (osoba; grupa zarzad/biuro/rada), `Partner` (typ instytucja/uczelnia/klaster_ue/branzowy).
- Strony pod `/klaster`: `AboutClusterPage` (StreamField body: text_section/cards/steps), `MembersIndexPage` (filtr po sektorze przez `?sektor=`), `TeamPage` (grupowanie po `group`), `PartnersPage` (grupowanie po `type`). Każda `max_count=1`, parent = `home.PillarPage`.

## Zależności
`apps.shared` (BasePage), `apps.home` (PillarPage jako rodzic). Snippet `Member` używany też przez Showroom/B2B w Fazie 2c.
