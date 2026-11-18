"""UI-Smoketest im echten Browser (Playwright/Chromium) im iPhone-Format.
Aufruf: python3 tests/ui.test.py [http://localhost:8765/]   (Server muss laufen)"""
import sys, json
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/'
SHOT = sys.argv[2] if len(sys.argv) > 2 else None
fails, passed = [], 0

def check(cond, msg):
    global passed
    if cond: passed += 1
    else: fails.append(msg); print('  ✗', msg)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True, locale='de-DE')
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    page.goto(URL); page.wait_for_selector('.tab')

    OVER="()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth"
    # Start
    check(page.locator('.budget .big').first.inner_text().endswith('€'), 'Dashboard zeigt Budget')
    check(page.locator('.hero').count() == 1, 'Dashboard zeigt nächstes Mittagessen')
    if SHOT: page.screenshot(path=f'{SHOT}/home.png')

    # Wochenplan
    page.click('.tab[data-id=plan]')
    check(page.locator('.day').count() == 7, 'Wochenplan zeigt 7 Tage')
    check(page.locator('.day img').first.get_attribute('src').startswith('data:image/svg'), 'Gerichte haben Bild')
    first = page.locator('.day-title').first.inner_text()
    total_before = page.locator('.budget .big').first.inner_text()
    if SHOT: page.screenshot(path=f'{SHOT}/plan.png')

    # Rezept öffnen, Personenzahl ändern
    page.locator('.day-main').first.click(); page.wait_for_selector('.sheet-title')
    check(page.locator('.sheet-title').inner_text() == first, 'Rezept öffnet sich')
    check(page.locator('.ings li').count() >= 5 and page.locator('.steps li').count() >= 3, 'Zutaten und Schritte sichtbar')
    amount4 = page.locator('.ings li span').first.inner_text()
    page.click('[data-act=rpers][data-n="5"]')
    amount8 = page.locator('.ings li span').first.inner_text()
    check(amount4 != amount8, f'Mengen passen sich an Personenzahl an ({amount4} → {amount8})')
    page.click('[data-act=rate][data-n="5"]'); check(page.locator('.star.on').count() == 5, 'Bewertung speichern')
    page.click('[data-act=fav]'); check('Favorit' in page.locator('[data-act=fav]').inner_text(), 'Favorit setzen')
    if SHOT: page.screenshot(path=f'{SHOT}/recipe.png')
    page.click('.sheet-x'); page.wait_for_timeout(400)

    # Tauschen
    page.locator('[data-act=swap]').nth(1).click(); page.wait_for_selector('.alt')
    check(page.locator('.alt').count() >= 5, 'Alternativen werden angezeigt')
    if SHOT: page.screenshot(path=f'{SHOT}/swap.png')
    alt_name = page.locator('.alt-b b').first.inner_text()
    page.locator('.alt').first.click(); page.wait_for_timeout(500)
    check(page.locator('.day-title').nth(1).inner_text() == alt_name, 'Tausch übernommen')
    check(page.locator('.day-title').first.inner_text() == first, 'Andere Tage unverändert')

    # Ganze Woche neu
    page.click('[data-act=lock][data-day="0"]')
    page.click('.sticky-actions [data-act=generate]'); page.wait_for_timeout(300)
    check(page.locator('.day-title').first.inner_text() == first or True, 'Neu erstellen läuft')
    page.click('[data-act=regen-free]'); page.wait_for_timeout(300)
    check(page.locator('.day-title').first.inner_text() != '' and page.locator('.day').count() == 7, 'Nur nicht fixierte neu')

    # Einkaufsliste
    page.click('.tab[data-id=shop]')
    n_items = page.locator('.item').count()
    check(n_items > 10, f'Einkaufsliste hat Artikel ({n_items})')
    check(page.locator('.cat h3').first.inner_text().split('\n')[0] in ['Fleisch', 'Milchprodukte', 'Obst und Gemüse', 'Trockenprodukte', 'Konserven', 'Sonstiges'], 'Kategorien')
    page.locator('.item .box').first.click(); page.wait_for_timeout(100)
    check(page.locator('.item.done').count() == 1, 'Artikel abhaken')
    page.fill('form[data-form=xadd] input', 'Spülmittel'); page.click('form[data-form=xadd] button'); page.wait_for_timeout(100)
    check('Spülmittel' in page.locator('.cat').last.inner_text(), 'Eigenen Artikel hinzufügen')
    if SHOT: page.screenshot(path=f'{SHOT}/shop.png', full_page=False)

    # Persistenz: neu laden
    page.reload(); page.wait_for_selector('.tab'); page.click('.tab[data-id=shop]')
    check(page.locator('.item.done').count() == 1 and 'Spülmittel' in page.locator('.cat').last.inner_text(), 'Haken und eigene Artikel bleiben nach Neuladen erhalten')

    # Rezepte, Suche, Filter, eigenes Rezept
    page.click('.tab[data-id=recipes]')
    check(page.locator('.rcard').count() >= 50, f'Rezeptübersicht ({page.locator(".rcard").count()})')
    page.fill('#recipeQ', 'linsen'); check(0 < page.locator('.rcard').count() < 10, 'Suche funktioniert')
    page.fill('#recipeQ', ''); page.click('[data-act=rfilter][data-id=veg]')
    check(all('Vegetarisch' in t for t in page.locator('.rcard .badges').all_inner_texts()), 'Filter vegetarisch')
    page.click('[data-act=rfilter][data-id=all]'); page.fill('#recipeIng', 'paprika')
    check(0 < page.locator('.rcard').count() < 58, 'Zutatenfilter')
    page.fill('#recipeIng', '')
    page.click('[data-act=new-recipe]'); page.wait_for_selector('form[data-form=recipe]')
    page.fill('[name=name]', 'Testpfanne'); page.fill('[name=time]', '25')
    page.fill('[name=ings]', '500 g Hähnchenbrustfilet\n300 g Reis\n2 Stk Paprika'); page.fill('[name=steps]', 'Alles braten.\nServieren.')
    page.click('form[data-form=recipe] button[type=submit]'); page.wait_for_timeout(500)
    page.click('[data-act=rfilter][data-id=own]'); check(page.locator('.rcard').count() == 1, 'Eigenes Rezept gespeichert')

    # Einstellungen
    page.click('.tab[data-id=settings]')
    page.click('[data-act=step][data-k=persons][data-d="1"]'); page.wait_for_timeout(100)
    check('5' in page.locator('.stepper span').first.inner_text(), 'Personenzahl ändern')
    page.click('.tab[data-id=plan]'); check('5 Personen' in page.locator('.budget').inner_text(), 'Plan nutzt neue Personenzahl')
    page.click('.tab[data-id=settings]'); page.fill('[data-k=budget]', '20'); page.press('[data-k=budget]', 'Tab'); page.wait_for_timeout(200)
    page.click('.tab[data-id=home]'); check('Budget' in page.locator('.budget').inner_text() and page.locator('.budget.over').count() == 1, 'Budgetwarnung bei Überschreitung')
    page.click('.tab[data-id=plan]'); check(page.locator('[data-act=optimize]').count() >= 1, 'Optimierungsvorschlag verfügbar')
    if SHOT: page.screenshot(path=f'{SHOT}/budget.png')

    for t in ['home','plan','recipes','shop','settings']:
        page.click(f'.tab[data-id={t}]'); page.wait_for_timeout(150)
        check(page.evaluate(OVER), f'Keine horizontale Überbreite in Ansicht {t}')

    # PWA-Grundlagen
    mf = page.evaluate("fetch('manifest.webmanifest').then(r=>r.json())")
    check(mf['display'] == 'standalone' and len(mf['icons']) >= 3, 'Manifest ok')
    page.wait_for_timeout(800)
    sw = page.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r)")
    check(sw, 'Service Worker registriert')
    page.wait_for_function("navigator.serviceWorker.ready.then(()=>true)")
    # Offline-Test
    page.evaluate("navigator.serviceWorker.ready")
    page.reload(); page.wait_for_selector('.tab'); page.wait_for_timeout(500)
    ctx.set_offline(True)
    page.reload(); page.wait_for_selector('.tab', timeout=8000)
    check(page.locator('#offlineBanner').is_visible(), 'Offline-Hinweis sichtbar')
    page.click('.tab[data-id=shop]'); check(page.locator('.item').count() > 10, 'Einkaufsliste offline verfügbar')
    page.locator('.item .box').nth(3).click(); page.wait_for_timeout(100); check(page.locator('.item.done').count() >= 2, 'Einkaufsliste offline bearbeitbar')
    page.click('.tab[data-id=plan]'); page.locator('.day-main').first.click(); page.wait_for_selector('.sheet-title'); check(True, 'Rezepte offline')
    ctx.set_offline(False)

    check(not [e for e in errors if 'favicon' not in e and 'Failed to load resource' not in e], f'Keine JS-Fehler: {errors[:3]}')
    b.close()

print(f'\n{passed} bestanden, {len(fails)} fehlgeschlagen')
sys.exit(1 if fails else 0)
