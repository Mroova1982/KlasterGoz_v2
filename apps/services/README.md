# apps.services

Usługi klastra (filar Klaster).

## Co robi
- `ServicesIndexPage` — katalog pod `/klaster/uslugi`; auto-listuje żywe podstrony `ServicePage` w `get_context`. `parent_page_types=["home.PillarPage"]`, `max_count=1`.
- `ServicePage` — pojedyncza usługa: hero (tag, lead, CTA, opcjonalny boczny box), opis, korzyści (`ServiceBenefit`), etapy procesu (`ServiceStep`), cennik, FAQ (`ServiceFAQ`), CTA strip. `parent_page_types=["services.ServicesIndexPage"]`.
- Sekcje renderują się warunkowo — puste znikają.

## Świadome uproszczenia
- FAQ jako per-page orderable (`ServiceFAQ`), nie globalny snippet FAQItem.
- Bez `related_projects` (ProjectPage = Faza 4) i bez `AbstractServiceLikePage` (ConsultingAreaPage = Faza 4).

## Zależności
`apps.shared` (BasePage), `apps.home` (PillarPage jako rodzic).
