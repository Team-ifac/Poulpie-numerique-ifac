import base64
import cgi
import datetime as dt
import hmac
import json
import os
import secrets
import sqlite3
from http import cookies
from urllib.parse import parse_qs, urlencode
from wsgiref.simple_server import make_server
from wsgiref.util import FileWrapper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data.sqlite")
STATIC_DIR = os.path.join(BASE_DIR, "public")
SECRET_KEY = (os.environ.get("APP_SECRET") or "ressourcerie-ifac-secret").encode()


def slugify(value: str) -> str:
    return "-".join(value.lower().strip().replace("'", "").split())


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'USER',
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT,
            age_range TEXT,
            duration TEXT,
            level TEXT,
            prep_time TEXT,
            visibility TEXT NOT NULL,
            thumbnail_url TEXT,
            file_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resource_themes (
            resource_id INTEGER NOT NULL,
            theme_id INTEGER NOT NULL,
            PRIMARY KEY (resource_id, theme_id),
            FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
            FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, resource_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    return conn


def hash_password(raw: str) -> str:
    salt = secrets.token_hex(8)
    derived = hmac.new(salt.encode(), raw.encode(), "sha256").hexdigest()
    return f"{salt}${derived}"


def check_password(raw: str, hashed: str) -> bool:
    try:
        salt, digest = hashed.split("$")
    except ValueError:
        return False
    check = hmac.new(salt.encode(), raw.encode(), "sha256").hexdigest()
    return hmac.compare_digest(check, digest)


def encode_session(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"))
    signature = hmac.new(SECRET_KEY, raw.encode(), "sha256").hexdigest()
    token = base64.urlsafe_b64encode(raw.encode()).decode()
    return f"{token}.{signature}"


def decode_session(token: str):
    try:
        raw_b64, signature = token.split(".")
        raw = base64.urlsafe_b64decode(raw_b64.encode()).decode()
        expected = hmac.new(SECRET_KEY, raw.encode(), "sha256").hexdigest()
        if not hmac.compare_digest(expected, signature):
            return None
        data = json.loads(raw)
        if data.get("exp") and dt.datetime.utcnow().timestamp() > data["exp"]:
            return None
        return data
    except Exception:
        return None


def seed_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM themes")
    if cur.fetchone()[0] == 0:
        themes = [
            "Environnement",
            "Harcèlement",
            "Discriminations",
            "Jeux coopératifs",
            "Projet pédagogique",
            "Réglementation",
            "Posture professionnelle",
            "Ingénierie de formation",
        ]
        for name in themes:
            cur.execute(
                "INSERT INTO themes (name, slug) VALUES (?, ?)",
                (name, slugify(name)),
            )
        conn.commit()

    cur.execute("SELECT COUNT(*) FROM resources")
    if cur.fetchone()[0] == 0:
        now = dt.datetime.utcnow().isoformat()
        resources = [
            {
                "title": "Atelier fresque biodiversité locale",
                "summary": "Animer une fresque participative pour sensibiliser aux écosystèmes de quartier.",
                "content": "Objectifs : faire émerger des solutions locales. Matériel : post-it recyclés, grands papiers. Déroulé en 4 temps : brise-glace, cartographie sensible, priorisation, engagements.",
                "type": "Fiche d'animation",
                "age_range": "10-15 ans",
                "duration": "1h30",
                "level": "Découverte",
                "prep_time": "20 minutes",
                "visibility": "PUBLIC",
                "themes": ["Environnement", "Jeux coopératifs"],
            },
            {
                "title": "Kit clé en main anti-harcèlement",
                "summary": "Séquence de prévention en 3 séances avec outils prêts à l'emploi.",
                "content": "Séance 1 : définir le harcèlement par des mises en situation. Séance 2 : vidéo témoignage et débat mouvant. Séance 3 : création d'une charte. Inclut fiches rôle, script vidéo, affiches.",
                "type": "Kit clé en main",
                "age_range": "12-16 ans",
                "duration": "3 x 1h",
                "level": "Intermédiaire",
                "prep_time": "40 minutes",
                "visibility": "PUBLIC",
                "themes": ["Harcèlement", "Discriminations"],
            },
            {
                "title": "Cercle coopératif express",
                "summary": "5 mini-jeux sans matériel pour ressouder un groupe en 15 minutes.",
                "content": "Suite de 5 jeux : statue, miroir, passage de message, applaudissements croisés, météo collective. Chaque jeu inclut intention pédagogique et débrief express.",
                "type": "Jeu coopératif",
                "age_range": "8-14 ans",
                "duration": "20 minutes",
                "level": "Découverte",
                "prep_time": "5 minutes",
                "visibility": "PUBLIC",
                "themes": ["Jeux coopératifs"],
            },
            {
                "title": "Mini-projet potager urbain",
                "summary": "Planifier et lancer un micro-potager en pied d'immeuble avec des jeunes.",
                "content": "Démarche : diagnostic terrain, co-conception des bacs, plan d'arrosage tournant, valorisation auprès des habitant·es. Inclut budget prévisionnel et planning sur 8 semaines.",
                "type": "Projet",
                "age_range": "14-18 ans",
                "duration": "8 semaines",
                "level": "Avancé",
                "prep_time": "1h",
                "visibility": "PUBLIC",
                "themes": ["Environnement", "Projet pédagogique"],
            },
            {
                "title": "Cadre légal des accueils de mineurs",
                "summary": "Synthèse claire des obligations réglementaires pour les équipes d'animation.",
                "content": "Comprendre les niveaux de responsabilité, les taux d'encadrement, les protocoles santé et sécurité, et les documents à conserver. Inclut check-list téléchargeable.",
                "type": "Article",
                "age_range": "Professionnel·les",
                "duration": "Lecture 20 minutes",
                "level": "Fondamentaux",
                "prep_time": "10 minutes",
                "visibility": "PUBLIC",
                "themes": ["Réglementation"],
            },
            {
                "title": "Posture professionnelle IFAC",
                "summary": "Référentiel interne pour harmoniser l'accompagnement des publics.",
                "content": "Cadre IFAC autour de l'écoute active, de la co-construction et de la sécurité affective. Exemples de formulations inclusives, gestes professionnels et points de vigilance.",
                "type": "Référentiel",
                "age_range": "Équipes IFAC",
                "duration": "Lecture 30 minutes",
                "level": "Interne",
                "prep_time": "20 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Posture professionnelle"],
            },
            {
                "title": "Ingénierie de formation : trame IFAC",
                "summary": "Modèle interne pour concevoir un module : objectifs, séquence, évaluations.",
                "content": "Trame détaillée incluant la progression pédagogique, les modalités d'évaluation, l'ancrage terrain et l'adaptation aux publics. Feuilles de route prêtes à compléter.",
                "type": "Trame",
                "age_range": "Formateur·rices IFAC",
                "duration": "Variable",
                "level": "Interne",
                "prep_time": "45 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Ingénierie de formation"],
            },
            {
                "title": "Modèles IFAC : courriers familles",
                "summary": "Pack de modèles prêts à personnaliser pour communiquer avec les familles.",
                "content": "Courrier d'information, rappel sécurité, autorisation de sortie, bilan de fin de cycle. Ton chaleureux et professionnel, adapté aux familles éloignées du numérique.",
                "type": "Modèle",
                "age_range": "Équipes IFAC",
                "duration": "Selon usage",
                "level": "Interne",
                "prep_time": "15 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Réglementation", "Posture professionnelle"],
            },
            {
                "title": "Offre interne IFAC aux collectivités",
                "summary": "Argumentaire synthétique pour présenter l'offre IFAC aux partenaires.",
                "content": "Points forts, impacts mesurés, accompagnements possibles, témoignages courts. Slide de pitch et script de prise de parole de 3 minutes inclus.",
                "type": "Kit communication",
                "age_range": "Équipes IFAC",
                "duration": "Pitch 3 minutes",
                "level": "Interne",
                "prep_time": "30 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Projet pédagogique", "Posture professionnelle"],
            },
            {
                "title": "Gestion de crise en accueil collectif",
                "summary": "Scénarios types et fiches réflexes pour sécuriser l'équipe et le public.",
                "content": "6 scénarios (blessure, conflit, météo, incident transport, comportement à risque, suspicion de harcèlement). Pour chaque : conduite à tenir, messages clés, trace écrite.",
                "type": "Fiche réflexe",
                "age_range": "Équipes IFAC",
                "duration": "Lecture 20 minutes",
                "level": "Interne",
                "prep_time": "25 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Réglementation", "Harcèlement"],
            },
            {
                "title": "Boîte à outils inclusion et discriminations",
                "summary": "Rituels et outils pour animer des temps d'échanges sécurisés.",
                "content": "Fiches pour nommer les discriminations, exemples d'aménagements, grille d'auto-positionnement équipe, ressources partenaires.",
                "type": "Dossier",
                "age_range": "Adolescent·es",
                "duration": "2h",
                "level": "Intermédiaire",
                "prep_time": "35 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Discriminations", "Projet pédagogique"],
            },
            {
                "title": "Trame d'évaluation rapide d'activité",
                "summary": "Questionnaire minute à chaud + débrief animé en 10 minutes.",
                "content": "Inclut les questions clés, une roue d'émotions imprimable, et un guide pour récolter la parole des jeunes avec bienveillance.",
                "type": "Outil d'évaluation",
                "age_range": "8-17 ans",
                "duration": "10 minutes",
                "level": "Découverte",
                "prep_time": "10 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Projet pédagogique", "Jeux coopératifs"],
            },
            {
                "title": "Co-développement flash entre directeurs·rices",
                "summary": "Méthode rapide pour échanger entre pairs sur une difficulté pro.",
                "content": "Format 30 minutes : exposé, clarification, idées flash, plan d'action. Fiche d'animation et minuteur prêts à imprimer.",
                "type": "Atelier pair-à-pair",
                "age_range": "Direction IFAC",
                "duration": "30 minutes",
                "level": "Avancé",
                "prep_time": "15 minutes",
                "visibility": "INTERNAL_IFAC",
                "themes": ["Posture professionnelle", "Ingénierie de formation"],
            },
        ]
        for idx, res in enumerate(resources, start=1):
            cur.execute(
                """
                INSERT INTO resources (
                    title, summary, content, type, age_range, duration, level, prep_time, visibility, thumbnail_url, file_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    res["title"],
                    res["summary"],
                    res["content"],
                    res.get("type"),
                    res.get("age_range"),
                    res.get("duration"),
                    res.get("level"),
                    res.get("prep_time"),
                    res["visibility"],
                    f"/static/uploads/placeholder.svg",
                    f"/static/files/ressource-{idx}.pdf",
                    now,
                    now,
                ),
            )
            resource_id = cur.lastrowid
            for theme_name in res.get("themes", []):
                cur.execute("SELECT id FROM themes WHERE name = ?", (theme_name,))
                theme_row = cur.fetchone()
                if theme_row:
                    cur.execute(
                        "INSERT INTO resource_themes (resource_id, theme_id) VALUES (?, ?)",
                        (resource_id, theme_row[0]),
                    )
        conn.commit()


def render_layout(title: str, body: str, user=None, extra_head: str = "") -> bytes:
    nav_links = [
        ("/", "Accueil"),
        ("/resources", "Ressources"),
        ("/about", "À propos"),
    ]
    nav_html = "".join(
        f'<a class="nav-link" href="{href}">{label}</a>' for href, label in nav_links
    )
    auth_html = ""
    if user:
        auth_html = (
            f'<div class="nav-auth">'
            f'<a class="button ghost" href="/favorites">Ma bibliothèque</a>'
            f'<a class="button ghost" href="/logout">Déconnexion</a>'
        )
        if user.get("role") == "ADMIN":
            auth_html += '<a class="button" href="/admin">Espace admin</a>'
        auth_html += "</div>"
    else:
        auth_html = (
            '<div class="nav-auth">'
            '<a class="button ghost" href="/login">Connexion</a>'
            '<a class="button" href="/register">Inscription</a>'
            '</div>'
        )
    html = f"""
    <!DOCTYPE html>
    <html lang=\"fr\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>{title} – Ressourcerie IFAC</title>
        <link rel=\"stylesheet\" href=\"/static/css/app.css\" />
        {extra_head}
    </head>
    <body>
        <header class=\"site-header\">
            <div class=\"brand\">Ressourcerie IFAC</div>
            <nav>{nav_html}</nav>
            {auth_html}
        </header>
        <main class=\"page\">{body}</main>
        <footer class=\"site-footer\">Ressourcerie IFAC – ressources pédagogiques et internes. Langage inclusif et accessible.</footer>
    </body>
    </html>
    """
    return html.encode()


def parse_post(environ):
    form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ, keep_blank_values=True)
    data = {key: form.getvalue(key) for key in form.keys()}
    files = {}
    for key in form.keys():
        if isinstance(form[key], cgi.FieldStorage) and form[key].filename:
            files[key] = form[key]
    return data, files


def set_cookie(headers, name, value, max_age=None):
    c = cookies.SimpleCookie()
    c[name] = value
    c[name]["path"] = "/"
    if max_age:
        c[name]["max-age"] = str(max_age)
    headers.append(("Set-Cookie", c.output(header="")))


def clear_cookie(headers, name):
    set_cookie(headers, name, "", max_age=0)


def get_current_user(environ, conn):
    cookie_header = environ.get("HTTP_COOKIE", "")
    cookie = cookies.SimpleCookie()
    cookie.load(cookie_header)
    token = cookie.get("session")
    if not token:
        return None
    data = decode_session(token.value)
    if not data:
        return None
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role FROM users WHERE id = ?", (data.get("uid"),))
    row = cur.fetchone()
    if not row:
        return None
    return {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}


def redirect(location):
    return "302 Found", [("Location", location)], b""


def send_response(start_response, status_code, headers, body):
    start_response(status_code, headers)
    return [body]


def serve_file(path, start_response):
    abs_path = os.path.join(STATIC_DIR, path)
    if not os.path.isfile(abs_path):
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not found"]
    content_type = "text/plain"
    if abs_path.endswith(".css"):
        content_type = "text/css"
    elif abs_path.endswith(".svg"):
        content_type = "image/svg+xml"
    elif abs_path.endswith(".pdf"):
        content_type = "application/pdf"
    elif abs_path.endswith(".png"):
        content_type = "image/png"
    size = os.path.getsize(abs_path)
    start_response("200 OK", [("Content-Type", content_type), ("Content-Length", str(size))])
    return FileWrapper(open(abs_path, "rb"))


def render_home(user):
    buttons_profile = [
        ("Animateur·rice", "theme:jeux-cooperatifs"),
        ("Formateur·rice", "theme:ingenierie-de-formation"),
        ("Directeur·rice", "theme:reglementation"),
        ("Stagiaire", "theme:projet-pedagogique"),
        ("Découvrir", "theme:environnement"),
    ]
    buttons_need = [
        ("Préparer rapidement", "duration:20 minutes"),
        ("Monter un projet", "theme:projet-pedagogique"),
        ("Gérer une situation", "theme:reglementation"),
        ("Monter en compétences", "theme:ingenierie-de-formation"),
    ]
    profile_html = "".join(
        f'<a class="cta" href="/resources?quick={slug}">{label}</a>' for label, slug in buttons_profile
    )
    need_html = "".join(
        f'<a class="cta ghost" href="/resources?quick={slug}">{label}</a>' for label, slug in buttons_need
    )
    body = f"""
    <section class=\"hero\">
        <div>
            <p class=\"eyebrow\">Ressourcerie pédagogique et interne</p>
            <h1>Ressourcerie IFAC</h1>
            <p class=\"lead\">Ressources prêtes à l'emploi, trames internes et outils de formation pour les équipes IFAC. Navigation claire et accessible.</p>
            <div class=\"hero-actions\">
                <a class=\"cta\" href=\"/resources\">Explorer le catalogue</a>
                <a class=\"cta ghost\" href=\"#entrer\">Choisir mon entrée</a>
            </div>
        </div>
        <div class=\"hero-card\">
            <h3>Ce que vous trouverez</h3>
            <ul>
                <li>Fiches d'animation et kits prêts à diffuser</li>
                <li>Documents internes IFAC sécurisés après connexion</li>
                <li>Badges clairs : durée, tranche d'âge, visibilité</li>
            </ul>
        </div>
    </section>
    <section id=\"entrer\" class=\"grid\">
        <div class=\"panel\">
            <h2>Entrer par profil</h2>
            <p>Choisissez votre posture pour aller à l'essentiel.</p>
            <div class=\"pill-group\">{profile_html}</div>
        </div>
        <div class=\"panel\">
            <h2>Entrer par besoin</h2>
            <p>Un filtre rapide vous attend dans le catalogue.</p>
            <div class=\"pill-group\">{need_html}</div>
        </div>
    </section>
    <section class=\"highlight\">
        <div>
            <h3>Favoris synchronisés</h3>
            <p>Ajoutez vos ressources en un clic et retrouvez-les dans "Ma bibliothèque".</p>
        </div>
        <div>
            <h3>Espace sécurisé IFAC</h3>
            <p>Les documents internes sont visibles après connexion. Les comptes admin peuvent publier en autonomie.</p>
        </div>
        <div>
            <h3>Filtres rapides</h3>
            <p>Thématique, type, durée, tranche d'âge et accès Interne IFAC (après connexion).</p>
        </div>
    </section>
    """
    return render_layout("Accueil", body, user)


def fetch_themes(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, slug FROM themes ORDER BY name")
    return [dict(row) for row in cur.fetchall()]


def fetch_resource(conn, resource_id, include_internal=False):
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM resources WHERE id = ?" + ("" if include_internal else " AND visibility = 'PUBLIC'"),
        (resource_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    res = dict(zip([col[0] for col in cur.description], row))
    cur.execute(
        """
        SELECT t.id, t.name FROM themes t
        JOIN resource_themes rt ON rt.theme_id = t.id
        WHERE rt.resource_id = ?
        ORDER BY t.name
        """,
        (resource_id,),
    )
    res["themes"] = [dict(r) for r in cur.fetchall()]
    return res


def list_resources(conn, filters, include_internal=False):
    params = []
    clauses = []
    search = filters.get("q")
    if search:
        clauses.append("(title LIKE ? OR summary LIKE ? OR content LIKE ?)")
        key = f"%{search}%"
        params.extend([key, key, key])
    theme = filters.get("theme")
    if theme:
        clauses.append("id IN (SELECT resource_id FROM resource_themes WHERE theme_id = ?)")
        params.append(theme)
    res_type = filters.get("type")
    if res_type:
        clauses.append("type = ?")
        params.append(res_type)
    age = filters.get("age")
    if age:
        clauses.append("age_range = ?")
        params.append(age)
    duration = filters.get("duration")
    if duration:
        clauses.append("duration = ?")
        params.append(duration)
    if include_internal:
        visibility = filters.get("visibility")
        if visibility:
            clauses.append("visibility = ?")
            params.append(visibility)
    else:
        clauses.append("visibility = 'PUBLIC'")
    where = " WHERE " + " AND ".join(clauses) if clauses else ("" if include_internal else " WHERE visibility = 'PUBLIC'")
    cur = conn.cursor()
    cur.execute("SELECT * FROM resources" + where + " ORDER BY created_at DESC", params)
    rows = cur.fetchall()
    resources = []
    theme_map = {t["id"]: t for t in fetch_themes(conn)}
    for row in rows:
        res = dict(zip([c[0] for c in cur.description], row))
        cur.execute("SELECT theme_id FROM resource_themes WHERE resource_id = ?", (res["id"],))
        theme_ids = [r[0] for r in cur.fetchall()]
        res["themes"] = [theme_map[tid] for tid in theme_ids if tid in theme_map]
        resources.append(res)
    return resources


def render_resource_cards(resources, user_favorites):
    cards = []
    for res in resources:
        badge = "Public" if res["visibility"] == "PUBLIC" else "Interne IFAC"
        fav_label = "Retirer des favoris" if res["id"] in user_favorites else "Ajouter aux favoris"
        themes = "".join(f'<span class="chip">{t["name"]}</span>' for t in res.get("themes", []))
        cards.append(
            f"""
            <article class=\"card\">
                <div class=\"card-top\">
                    <span class=\"badge {res['visibility'].lower()}\">{badge}</span>
                    <span class=\"type\">{res.get('type','')}</span>
                </div>
                <h3><a href=\"/resources/{res['id']}\">{res['title']}</a></h3>
                <p>{res['summary']}</p>
                <div class=\"meta\">
                    <span>{res.get('age_range','')}</span>
                    <span>{res.get('duration','')}</span>
                    <span>Préparation : {res.get('prep_time','')}</span>
                </div>
                <div class=\"themes\">{themes}</div>
                <form method=\"POST\" action=\"/resources/{res['id']}/favorite\">\n<button class=\"small\" type=\"submit\">{fav_label}</button></form>
            </article>
            """
        )
    return "".join(cards) if cards else "<p>Aucune ressource trouvée.</p>"


def render_resources_page(conn, user, query):
    filters = {
        "q": query.get("q", [""])[0].strip(),
        "theme": query.get("theme", [""])[0],
        "type": query.get("type", [""])[0],
        "age": query.get("age", [""])[0],
        "duration": query.get("duration", [""])[0],
        "visibility": query.get("visibility", [""])[0],
    }
    quick = query.get("quick", [""])[0]
    if quick:
        if quick.startswith("theme:"):
            filters["theme"] = quick.replace("theme:", "")
        elif quick.startswith("duration:"):
            filters["duration"] = quick.replace("duration:", "")
        else:
            filters["theme"] = quick
    themes = fetch_themes(conn)
    theme_id = None
    if filters.get("theme"):
        if filters["theme"].isdigit():
            theme_id = filters["theme"]
        else:
            for t in themes:
                if t["slug"] == filters["theme"]:
                    theme_id = t["id"]
                    break
        filters["theme"] = theme_id
    user_favs = set()
    include_internal = user is not None
    if user:
        cur = conn.cursor()
        cur.execute("SELECT resource_id FROM favorites WHERE user_id = ?", (user["id"],))
        user_favs = {r[0] for r in cur.fetchall()}
    resources = list_resources(conn, filters, include_internal=include_internal)
    cards_html = render_resource_cards(resources, user_favs)
    options_theme = "<option value=''>Toutes les thématiques</option>" + "".join(
        f"<option value='{t['id']}' {'selected' if str(theme_id)==str(t['id']) else ''}>{t['name']}</option>" for t in themes
    )
    visibility_filter = ""
    if user:
        visibility_filter = """
        <label>Visibilité
            <select name=\"visibility\">
                <option value=\"\">Public + Interne IFAC</option>
                <option value=\"PUBLIC\" {public_sel}>Public</option>
                <option value=\"INTERNAL_IFAC\" {internal_sel}>Interne IFAC</option>
            </select>
        </label>
        """.format(
            public_sel="selected" if filters.get("visibility") == "PUBLIC" else "",
            internal_sel="selected" if filters.get("visibility") == "INTERNAL_IFAC" else "",
        )
    body = f"""
    <section class=\"page-header\">
        <div>
            <p class=\"eyebrow\">Catalogue</p>
            <h1>Ressources IFAC</h1>
            <p>Filtrez par thématique, type, durée ou tranche d'âge. Les ressources internes apparaissent après connexion.</p>
        </div>
        <div><a class=\"cta ghost\" href=\"/\">Retour à l'accueil</a></div>
    </section>
    <form class=\"filters\" method=\"GET\" action=\"/resources\">
        <label>Recherche
            <input type=\"search\" name=\"q\" value=\"{filters.get('q','')}\" placeholder=\"Mots-clés\" />
        </label>
        <label>Thématique
            <select name=\"theme\">{options_theme}</select>
        </label>
        <label>Type
            <input name=\"type\" value=\"{filters.get('type','')}\" placeholder=\"Fiche, kit...\" />
        </label>
        <label>Tranche d'âge
            <input name=\"age\" value=\"{filters.get('age','')}\" placeholder=\"8-12 ans, adultes...\" />
        </label>
        <label>Durée
            <input name=\"duration\" value=\"{filters.get('duration','')}\" placeholder=\"20 min, 2h...\" />
        </label>
        {visibility_filter}
        <button class=\"cta\" type=\"submit\">Filtrer</button>
    </form>
    <div class=\"cards\">{cards_html}</div>
    """
    return render_layout("Ressources", body, user)


def render_resource_detail(conn, user, resource_id):
    resource = fetch_resource(conn, resource_id, include_internal=user is not None)
    if not resource:
        return "404 Not Found", [], render_layout("Introuvable", "<p>Ressource indisponible.</p>", user)
    badge = "Public" if resource["visibility"] == "PUBLIC" else "Interne IFAC"
    themes = "".join(f"<span class='chip'>{t['name']}</span>" for t in resource.get("themes", []))
    body = f"""
    <nav class=\"breadcrumb\"><a href=\"/resources\">Retour au catalogue</a></nav>
    <section class=\"detail\">
        <div class=\"detail-header\">
            <div>
                <p class=\"eyebrow\">{badge}</p>
                <h1>{resource['title']}</h1>
                <p class=\"lead\">{resource['summary']}</p>
                <div class=\"meta\">
                    <span>{resource.get('type','')}</span>
                    <span>{resource.get('age_range','')}</span>
                    <span>{resource.get('duration','')}</span>
                    <span>Préparation : {resource.get('prep_time','')}</span>
                </div>
                <div class=\"themes\">{themes}</div>
                <div class=\"actions\">
                    <a class=\"cta\" href=\"{resource['file_url']}\">Télécharger la ressource</a>
                    <form method=\"POST\" action=\"/resources/{resource_id}/favorite\">
                        <button class=\"ghost\" type=\"submit\">Ajouter à ma bibliothèque</button>
                    </form>
                </div>
            </div>
            <div class=\"thumb\"><img src=\"{resource['thumbnail_url']}\" alt=\"Vignette\" /></div>
        </div>
        <article class=\"content\">{resource['content']}</article>
    </section>
    """
    return "200 OK", [("Content-Type", "text/html; charset=utf-8")], render_layout(resource["title"], body, user)


def render_auth_page(kind, message=""):
    title = "Connexion" if kind == "login" else "Inscription"
    action = "/login" if kind == "login" else "/register"
    swap = ("Pas encore de compte ?", "/register", "Créer mon compte") if kind == "login" else ("Déjà inscrit·e ?", "/login", "Me connecter")
    alert = f"<div class='alert'>{message}</div>" if message else ""
    name_field = "" if kind == "login" else """
            <label>Nom et prénom
                <input required name=\"name\" placeholder=\"Alex Dupont\" />
            </label>
    """
    body = f"""
    <section class=\"auth\">
        <h1>{title}</h1>
        <p>Accès sécurisé à la ressourcerie IFAC.</p>
        {alert}
        <form method=\"POST\" action=\"{action}\">
            {name_field}
            <label>Adresse e-mail
                <input required type=\"email\" name=\"email\" placeholder=\"vous@exemple.fr\" />
            </label>
            <label>Mot de passe
                <input required type=\"password\" name=\"password\" />
            </label>
            <button class=\"cta\" type=\"submit\">{title}</button>
        </form>
        <p class=\"switch\">{swap[0]} <a href=\"{swap[1]}\">{swap[2]}</a></p>
    </section>
    """
    return render_layout(title, body)


def render_about():
    body = """
    <section class=\"page-header\">
        <div>
            <p class=\"eyebrow\">IFAC</p>
            <h1>Qui sommes-nous ?</h1>
            <p>L'IFAC accompagne les territoires avec des équipes engagées. Cette ressourcerie rassemble les outils partagés et les documents internes pour gagner en autonomie.</p>
        </div>
    </section>
    <div class=\"grid\">
        <div class=\"panel\">
            <h3>Mission</h3>
            <p>Soutenir les équipes d'animation et de formation avec des ressources fiables, inclusives et faciles à adapter.</p>
        </div>
        <div class=\"panel\">
            <h3>Engagement</h3>
            <p>Accessibilité, sobriété numérique et partage sécurisé des contenus internes IFAC.</p>
        </div>
    </div>
    """
    return render_layout("À propos", body)


def save_upload(field, folder):
    filename = field.filename
    ext = os.path.splitext(filename)[1] or ""
    unique = f"{int(dt.datetime.utcnow().timestamp())}-{secrets.token_hex(4)}{ext}"
    target_path = os.path.join(STATIC_DIR, folder, unique)
    with open(target_path, "wb") as f:
        f.write(field.file.read())
    return f"/static/{folder}/{unique}"


def handle_register(environ, conn):
    data, _ = parse_post(environ)
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not (name and email and password):
        return render_auth_page("register", "Merci de compléter tous les champs.")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    is_first = cur.fetchone()[0] == 0
    try:
        cur.execute(
            "INSERT INTO users (name, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, hash_password(password), "ADMIN" if is_first else "USER", dt.datetime.utcnow().isoformat()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return render_auth_page("register", "Un compte existe déjà avec cet e-mail.")
    payload = {"uid": cur.lastrowid, "exp": (dt.datetime.utcnow() + dt.timedelta(days=7)).timestamp()}
    token = encode_session(payload)
    headers = [("Content-Type", "text/html; charset=utf-8")]
    set_cookie(headers, "session", token, max_age=7 * 24 * 3600)
    return "302 Found", headers + [("Location", "/resources")], b""


def handle_login(environ, conn):
    data, _ = parse_post(environ)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, role, name FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    if not row or not check_password(password, row[1]):
        return render_auth_page("login", "Identifiants incorrects.")
    payload = {"uid": row[0], "exp": (dt.datetime.utcnow() + dt.timedelta(days=7)).timestamp()}
    token = encode_session(payload)
    headers = [("Content-Type", "text/html; charset=utf-8")]
    set_cookie(headers, "session", token, max_age=7 * 24 * 3600)
    return "302 Found", headers + [("Location", "/resources")], b""


def ensure_admin(user):
    return user and user.get("role") == "ADMIN"


def render_favorites(conn, user):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT r.* FROM resources r
        JOIN favorites f ON f.resource_id = r.id
        WHERE f.user_id = ?
        ORDER BY r.title
        """,
        (user["id"],),
    )
    rows = cur.fetchall()
    theme_map = {t["id"]: t for t in fetch_themes(conn)}
    resources = []
    for row in rows:
        res = dict(zip([c[0] for c in cur.description], row))
        cur.execute("SELECT theme_id FROM resource_themes WHERE resource_id = ?", (res["id"],))
        res["themes"] = [theme_map[r[0]] for r in cur.fetchall() if r[0] in theme_map]
        resources.append(res)
    cards = render_resource_cards(resources, {r["id"] for r in resources})
    body = f"""
    <section class=\"page-header\">
        <div>
            <p class=\"eyebrow\">Favoris</p>
            <h1>Ma bibliothèque</h1>
            <p>Vos ressources enregistrées. Retirez-les en un clic.</p>
        </div>
    </section>
    <div class=\"cards\">{cards}</div>
    """
    return render_layout("Ma bibliothèque", body, user)


def toggle_favorite(conn, user, resource_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM favorites WHERE user_id = ? AND resource_id = ?", (user["id"], resource_id))
    if cur.fetchone():
        cur.execute("DELETE FROM favorites WHERE user_id = ? AND resource_id = ?", (user["id"], resource_id))
    else:
        cur.execute("INSERT INTO favorites (user_id, resource_id) VALUES (?, ?)", (user["id"], resource_id))
    conn.commit()


def render_admin_dashboard(conn, user):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM resources")
    res_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM themes")
    theme_count = cur.fetchone()[0]
    body = f"""
    <section class=\"page-header\">
        <div>
            <p class=\"eyebrow\">Administration</p>
            <h1>Tableau de bord</h1>
            <p>Publiez des ressources, gérez les thématiques et les rôles utilisateurs.</p>
        </div>
    </section>
    <div class=\"grid\">
        <div class=\"panel\"><h3>Ressources</h3><p>{res_count}</p><a class=\"cta ghost\" href=\"/admin/resources\">Gérer</a></div>
        <div class=\"panel\"><h3>Thématiques</h3><p>{theme_count}</p><a class=\"cta ghost\" href=\"/admin/themes\">Gérer</a></div>
        <div class=\"panel\"><h3>Utilisateurs</h3><p>{user_count}</p><a class=\"cta ghost\" href=\"/admin/users\">Gérer</a></div>
    </div>
    """
    return render_layout("Admin", body, user)


def render_admin_resources(conn, user):
    resources = list_resources(conn, {}, include_internal=True)
    rows = "".join(
        f"<tr><td>{r['title']}</td><td>{r['visibility']}</td><td>{r.get('type','')}</td><td><a href='/admin/resources/{r['id']}/edit'>Modifier</a></td></tr>"
        for r in resources
    )
    body = f"""
    <section class=\"page-header\"><div><p class=\"eyebrow\">Administration</p><h1>Gestion des ressources</h1></div><div><a class=\"cta\" href=\"/admin/resources/new\">Créer une ressource</a></div></section>
    <table class=\"table\"> <thead><tr><th>Titre</th><th>Visibilité</th><th>Type</th><th></th></tr></thead><tbody>{rows}</tbody></table>
    """
    return render_layout("Ressources admin", body, user)


def admin_resource_form(conn, resource=None):
    themes = fetch_themes(conn)
    selected = {t["id"] for t in resource.get("themes", [])} if resource else set()
    theme_checks = "".join(
        f"<label class='checkbox'><input type='checkbox' name='themes' value='{t['id']}' {'checked' if t['id'] in selected else ''}/> {t['name']}</label>"
        for t in themes
    )
    values = resource or {}
    thumb_preview = f"<p>Vignette actuelle : <a href='{values.get('thumbnail_url','')}'>voir</a></p>" if resource else ""
    file_preview = f"<p>Fichier actuel : <a href='{values.get('file_url','')}'>télécharger</a></p>" if resource else ""
    form = f"""
    <form class=\"form\" method=\"POST\" enctype=\"multipart/form-data\">
        <label>Titre<input name=\"title\" required value=\"{values.get('title','')}\" /></label>
        <label>Résumé<textarea name=\"summary\" required>{values.get('summary','')}</textarea></label>
        <label>Contenu détaillé<textarea name=\"content\" required>{values.get('content','')}</textarea></label>
        <label>Type<input name=\"type\" value=\"{values.get('type','')}\" /></label>
        <label>Tranche d'âge<input name=\"age_range\" value=\"{values.get('age_range','')}\" /></label>
        <label>Durée<input name=\"duration\" value=\"{values.get('duration','')}\" /></label>
        <label>Niveau<input name=\"level\" value=\"{values.get('level','')}\" /></label>
        <label>Temps de préparation<input name=\"prep_time\" value=\"{values.get('prep_time','')}\" /></label>
        <label>Visibilité
            <select name=\"visibility\">
                <option value=\"PUBLIC\" {'selected' if values.get('visibility')=='PUBLIC' else ''}>Public</option>
                <option value=\"INTERNAL_IFAC\" {'selected' if values.get('visibility')=='INTERNAL_IFAC' else ''}>Interne IFAC</option>
            </select>
        </label>
        <fieldset><legend>Thématiques</legend>{theme_checks}</fieldset>
        {thumb_preview}
        <label>Vignette (image)<input type=\"file\" name=\"thumbnail\" accept=\"image/*\" /></label>
        {file_preview}
        <label>Fichier ressource (PDF)<input type=\"file\" name=\"file\" accept=\"application/pdf\" /></label>
        <div class=\"form-actions\">
            <button class=\"cta\" type=\"submit\">Enregistrer</button>
            {'<button class="ghost" name="delete" value="1">Supprimer</button>' if resource else ''}
        </div>
    </form>
    """
    return form


def render_admin_resource_edit(conn, user, resource_id=None):
    resource = None
    if resource_id:
        resource = fetch_resource(conn, resource_id, include_internal=True)
        if not resource:
            return "404 Not Found", [], render_layout("Introuvable", "<p>Ressource introuvable.</p>", user)
    heading = "Créer une ressource" if resource is None else "Modifier la ressource"
    body = f"<section class='page-header'><h1>{heading}</h1></section>" + admin_resource_form(conn, resource)
    return "200 OK", [("Content-Type", "text/html; charset=utf-8")], render_layout(heading, body, user)


def persist_resource(conn, data, files, resource_id=None):
    now = dt.datetime.utcnow().isoformat()
    fields = {
        "title": data.get("title", "").strip(),
        "summary": data.get("summary", "").strip(),
        "content": data.get("content", "").strip(),
        "type": data.get("type"),
        "age_range": data.get("age_range"),
        "duration": data.get("duration"),
        "level": data.get("level"),
        "prep_time": data.get("prep_time"),
        "visibility": data.get("visibility", "PUBLIC"),
    }
    if not (fields["title"] and fields["summary"] and fields["content"]):
        raise ValueError("Champs requis manquants")
    if "thumbnail" in files and files["thumbnail"].filename:
        fields["thumbnail_url"] = save_upload(files["thumbnail"], "uploads")
    if "file" in files and files["file"].filename:
        fields["file_url"] = save_upload(files["file"], "files")
    cur = conn.cursor()
    if resource_id:
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        cur.execute(
            f"UPDATE resources SET {set_clause}, updated_at = ? WHERE id = ?",
            [*fields.values(), now, resource_id],
        )
        cur.execute("DELETE FROM resource_themes WHERE resource_id = ?", (resource_id,))
        res_id = resource_id
    else:
        cur.execute(
            """
            INSERT INTO resources (title, summary, content, type, age_range, duration, level, prep_time, visibility, thumbnail_url, file_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fields["title"],
                fields["summary"],
                fields["content"],
                fields.get("type"),
                fields.get("age_range"),
                fields.get("duration"),
                fields.get("level"),
                fields.get("prep_time"),
                fields["visibility"],
                fields.get("thumbnail_url", "/static/uploads/placeholder.svg"),
                fields.get("file_url", "/static/files/ressource-1.pdf"),
                now,
                now,
            ),
        )
        res_id = cur.lastrowid
    theme_ids = data.get("themes")
    if theme_ids:
        if not isinstance(theme_ids, list):
            theme_ids = [theme_ids]
        for tid in theme_ids:
            cur.execute("INSERT OR IGNORE INTO resource_themes (resource_id, theme_id) VALUES (?, ?)", (res_id, tid))
    conn.commit()
    return res_id


def render_admin_themes(conn, user):
    themes = fetch_themes(conn)
    rows = "".join(f"<tr><td>{t['name']}</td><td>{t['slug']}</td></tr>" for t in themes)
    body = f"""
    <section class=\"page-header\"><h1>Gestion des thématiques</h1></section>
    <form class=\"form inline\" method=\"POST\" action=\"/admin/themes\">
        <label>Nom de la thématique<input name=\"name\" required /></label>
        <button class=\"cta\" type=\"submit\">Ajouter</button>
    </form>
    <table class=\"table\"><thead><tr><th>Nom</th><th>Slug</th></tr></thead><tbody>{rows}</tbody></table>
    """
    return render_layout("Thématiques", body, user)


def render_admin_users(conn, user):
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC")
    rows = cur.fetchall()
    body_rows = "".join(
        f"<tr><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><form method='POST' action='/admin/users/{r[0]}/role'><select name='role'><option value='USER' {'selected' if r[3]=='USER' else ''}>USER</option><option value='ADMIN' {'selected' if r[3]=='ADMIN' else ''}>ADMIN</option></select><button class='small' type='submit'>Mettre à jour</button></form></td></tr>"
        for r in rows
    )
    body = f"""
    <section class=\"page-header\"><h1>Gestion des utilisateurs</h1></section>
    <table class=\"table\"><thead><tr><th>Nom</th><th>Email</th><th>Rôle</th><th>Action</th></tr></thead><tbody>{body_rows}</tbody></table>
    """
    return render_layout("Utilisateurs", body, user)


def application(environ, start_response):
    conn = init_db()
    seed_data(conn)
    user = get_current_user(environ, conn)
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path.startswith("/static/"):
        subpath = path.replace("/static/", "")
        return serve_file(subpath, start_response)

    # Public routes
    if path == "/":
        body = render_home(user)
        return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)

    if path == "/about":
        body = render_about()
        return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)

    if path == "/login":
        if method == "POST":
            status, headers, body = handle_login(environ, conn)
            start_response(status, headers)
            return [body]
        body = render_auth_page("login")
        return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)

    if path == "/register":
        if method == "POST":
            status, headers, body = handle_register(environ, conn)
            start_response(status, headers)
            return [body]
        body = render_auth_page("register")
        return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)

    if path == "/logout":
        headers = [("Content-Type", "text/html; charset=utf-8")]
        clear_cookie(headers, "session")
        start_response("302 Found", headers + [("Location", "/")])
        return [b""]

    if path.startswith("/resources"):
        parts = [p for p in path.split("/") if p]
        if len(parts) == 1:
            query = parse_qs(environ.get("QUERY_STRING", ""))
            body = render_resources_page(conn, user, query)
            return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)
        elif len(parts) >= 2:
            res_id = parts[1]
            if len(parts) == 3 and parts[2] == "favorite":
                if not user:
                    start_response("302 Found", [("Location", "/login")])
                    return [b""]
                toggle_favorite(conn, user, res_id)
                start_response("302 Found", [("Location", environ.get("HTTP_REFERER", "/resources") )])
                return [b""]
            status, headers, body = render_resource_detail(conn, user, res_id)
            start_response(status, [("Content-Type", "text/html; charset=utf-8"), *headers])
            return [body]

    if path == "/favorites":
        if not user:
            start_response("302 Found", [("Location", "/login")])
            return [b""]
        body = render_favorites(conn, user)
        return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)

    # Admin routes
    if path.startswith("/admin"):
        if not ensure_admin(user):
            start_response("302 Found", [("Location", "/login")])
            return [b""]
        if path == "/admin":
            body = render_admin_dashboard(conn, user)
            return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)
        if path == "/admin/resources":
            body = render_admin_resources(conn, user)
            return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)
        if path == "/admin/resources/new":
            if method == "POST":
                data, files = parse_post(environ)
                persist_resource(conn, data, files, None)
                start_response("302 Found", [("Location", "/admin/resources")])
                return [b""]
            status, headers, body = render_admin_resource_edit(conn, user, None)
            start_response(status, [("Content-Type", "text/html; charset=utf-8"), *headers])
            return [body]
        if path.startswith("/admin/resources/"):
            parts = path.split("/")
            resource_id = parts[3]
            if method == "POST":
                data, files = parse_post(environ)
                if data.get("delete"):
                    cur = conn.cursor()
                    cur.execute("DELETE FROM resources WHERE id = ?", (resource_id,))
                    conn.commit()
                    start_response("302 Found", [("Location", "/admin/resources")])
                    return [b""]
                persist_resource(conn, data, files, resource_id)
                start_response("302 Found", [("Location", "/admin/resources")])
                return [b""]
            status, headers, body = render_admin_resource_edit(conn, user, resource_id)
            start_response(status, [("Content-Type", "text/html; charset=utf-8"), *headers])
            return [body]
        if path == "/admin/themes":
            if method == "POST":
                data, _ = parse_post(environ)
                name = data.get("name", "").strip()
                if name:
                    cur = conn.cursor()
                    cur.execute("INSERT OR IGNORE INTO themes (name, slug) VALUES (?, ?)", (name, slugify(name)))
                    conn.commit()
                start_response("302 Found", [("Location", "/admin/themes")])
                return [b""]
            body = render_admin_themes(conn, user)
            return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)
        if path.startswith("/admin/users/") and path.endswith("/role"):
            user_id = path.split("/")[3]
            data, _ = parse_post(environ)
            role = data.get("role")
            if role in {"USER", "ADMIN"}:
                cur = conn.cursor()
                cur.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
                conn.commit()
            start_response("302 Found", [("Location", "/admin/users")])
            return [b""]
        if path == "/admin/users":
            body = render_admin_users(conn, user)
            return send_response(start_response, "200 OK", [("Content-Type", "text/html; charset=utf-8")], body)

    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return ["Page non trouvée".encode()]


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Serveur lancé sur http://localhost:{port}")
    with make_server("0.0.0.0", port, application) as httpd:
        httpd.serve_forever()
