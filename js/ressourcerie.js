const profiles = [
    {
        key: 'stagiaire',
        name: 'Stagiaire BAFA/BAFD',
        icon: '🎓',
        color: '#10b981',
        access: 'Accès public',
        description: 'Comprendre les bases du BAFA/BAFD, préparer son stage et sécuriser son parcours.',
        resourcesCount: 18,
        categories: ['Découverte du BAFA', 'Préparer son stage', 'Livret d’accueil'],
    },
    {
        key: 'animateur',
        name: 'Animateur·rice',
        icon: '🎯',
        color: '#3b82f6',
        access: 'Accès public',
        description: '77 ressources pratiques pour animer, gérer un groupe et proposer des activités variées.',
        resourcesCount: 77,
        categories: ['Activités manuelles et créatives', 'Jeux et divertissements', 'Recettes et cuisine'],
    },
    {
        key: 'directeur',
        name: 'Directeur·rice',
        icon: '🏢',
        color: '#f97316',
        access: 'Connexion requise',
        description: 'Outils de gestion et de management pour piloter une équipe et suivre la conformité.',
        resourcesCount: 10,
        categories: ['Gestion d’équipe', 'Cadre réglementaire', 'Communication'],
    },
    {
        key: 'formateur',
        name: 'Formateur·rice',
        icon: '📚',
        color: '#a855f7',
        access: 'Connexion requise',
        description: 'Approfondissements, supports de formation et parcours thématiques pour transmettre.',
        resourcesCount: 6,
        categories: ['Supports de session', 'Approfondissements', 'Parcours thématiques'],
    },
];

const resources = [
    {
        id: 1,
        title: 'Kit de démarrage BAFA',
        description: 'Un guide synthétique pour comprendre le déroulé de la formation BAFA et préparer son dossier.',
        type: 'Guide',
        profile: 'stagiaire',
        category: 'Découverte du BAFA',
        views: 2680,
        createdAt: '2025-01-04',
    },
    {
        id: 2,
        title: 'Activité manuelle - Kaléidoscope scientifique',
        description: 'Fiche pas-à-pas pour organiser une activité scientifique ludique avec du matériel simple.',
        type: 'Fiche',
        profile: 'animateur',
        category: 'Activités manuelles et créatives',
        views: 4320,
        createdAt: '2025-02-12',
    },
    {
        id: 3,
        title: 'Jeu coopératif : Mission Astronaute',
        description: 'Une activité de cohésion pour apprendre à coopérer en groupe, adaptable en intérieur comme en extérieur.',
        type: 'Fiche',
        profile: 'animateur',
        category: 'Jeux et divertissements',
        views: 3890,
        createdAt: '2025-02-20',
    },
    {
        id: 4,
        title: 'Tableau de bord pour directeur·rice',
        description: 'Outil de pilotage avec checklist sécurité, affectations d’équipe et suivi des autorisations.',
        type: 'Livret',
        profile: 'directeur',
        category: 'Gestion d’équipe',
        views: 1240,
        createdAt: '2025-01-28',
    },
    {
        id: 5,
        title: 'Parcours approfondissement animation nature',
        description: 'Une séquence de 5 ressources pour créer des ateliers autour de la nature et du développement durable.',
        type: 'Approfondissement',
        profile: 'formateur',
        category: 'Parcours thématiques',
        views: 980,
        createdAt: '2025-02-02',
    },
    {
        id: 6,
        title: 'Recette participative - Four solaire',
        description: 'Atelier cuisine plein air : construire un four solaire, sensibiliser au climat et préparer une recette simple.',
        type: 'Fiche',
        profile: 'animateur',
        category: 'Recettes et cuisine',
        views: 2410,
        createdAt: '2025-02-08',
    },
    {
        id: 7,
        title: 'Livret d’accueil stagiaire',
        description: 'Document d’accueil pour rassurer les stagiaires, présenter les référentiels et les contacts clés.',
        type: 'Livret',
        profile: 'stagiaire',
        category: 'Livret d’accueil',
        views: 1850,
        createdAt: '2025-01-18',
    },
    {
        id: 8,
        title: 'Check-list matériel récup’',
        description: 'Fiche pratique pour animer un atelier récupération et matériel de réemploi avec budget maîtrisé.',
        type: 'Fiche',
        profile: 'animateur',
        category: 'Récupération et matériel',
        views: 1990,
        createdAt: '2025-02-18',
    },
    {
        id: 9,
        title: 'Module formateur : posture et feedback',
        description: 'Support de formation pour accompagner les stagiaires, avec exemples de feedback constructif.',
        type: 'Approfondissement',
        profile: 'formateur',
        category: 'Supports de session',
        views: 860,
        createdAt: '2025-02-21',
    },
    {
        id: 10,
        title: 'Jeu grand groupe : Rallye des métiers de l’animation',
        description: 'Un jeu de pistes pour présenter les rôles BAFA/BAFD, avec énigmes et défis collaboratifs.',
        type: 'Guide',
        profile: 'animateur',
        category: 'Jeux et divertissements',
        views: 2140,
        createdAt: '2025-01-30',
    },
    {
        id: 11,
        title: 'Procédures sécurité - directeur·rice',
        description: 'Synthèse des obligations réglementaires, modèles de courriers et protocoles d’urgence.',
        type: 'Guide',
        profile: 'directeur',
        category: 'Cadre réglementaire',
        views: 1180,
        createdAt: '2025-02-16',
    },
    {
        id: 12,
        title: 'Fiche pratique : icebreaker 10 minutes',
        description: '5 idées d’icebreakers rapides pour démarrer une session avec un groupe varié.',
        type: 'Fiche',
        profile: 'animateur',
        category: 'Activités manuelles et créatives',
        views: 2010,
        createdAt: '2025-02-22',
    },
];

const typeStyles = {
    Fiche: { background: 'rgba(59, 130, 246, 0.12)', color: '#1d4ed8' },
    Approfondissement: { background: 'rgba(168, 85, 247, 0.14)', color: '#7e22ce' },
    Guide: { background: 'rgba(16, 185, 129, 0.14)', color: '#0f9f6e' },
    Livret: { background: 'rgba(249, 115, 22, 0.16)', color: '#c2410c' },
};

function createProfileCard(profile) {
    const tagStyle = `background:${profile.color}`;
    const categoryBadges = profile.categories
        .map((category) => `<span class="badge rounded-pill" style="background: rgba(0,0,0,0.04); color: #0f172a;">${category}</span>`)
        .join(' ');

    return `
        <div class="col-md-6 col-xl-3">
            <article class="profile-card h-100">
                <div class="d-flex align-items-center justify-content-between mb-3">
                    <span class="profile-tag" style="${tagStyle}">${profile.icon} ${profile.name}</span>
                    <span class="profile-count">${profile.resourcesCount} ressources</span>
                </div>
                <p class="profile-access mb-2">${profile.access}</p>
                <p class="mb-3">${profile.description}</p>
                <div class="resource-tags mb-3">${categoryBadges}</div>
                <div class="profile-actions d-flex align-items-center justify-content-between">
                    <a class="btn btn-link p-0" href="#popular-resources" style="color:${profile.color}">Voir les ressources populaires</a>
                    <a class="btn btn-outline-primary btn-sm" href="#recent-resources">Choisir ce profil</a>
                </div>
            </article>
        </div>
    `;
}

function createResourceCard(resource) {
    const profile = profiles.find((p) => p.key === resource.profile);
    const typeStyle = typeStyles[resource.type] || { background: 'rgba(0,0,0,0.08)', color: '#0f172a' };
    const formattedDate = new Date(resource.createdAt);
    const dateLabel = formattedDate.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });

    return `
        <div class="col-md-6 col-xl-4">
            <article class="resource-card h-100">
                <div class="card-body">
                    <div class="d-flex align-items-start justify-content-between gap-2">
                        <span class="resource-type" style="background:${typeStyle.background}; color:${typeStyle.color}">${resource.type}</span>
                        <span class="badge rounded-pill" style="background:${profile?.color || '#e2e8f0'}; color: white;">${profile?.icon || ''} ${profile?.name || ''}</span>
                    </div>
                    <h3 class="resource-title">${resource.title}</h3>
                    <p class="resource-description mb-2">${resource.description}</p>
                    <div class="resource-meta">
                        <span><i class="fas fa-folder-open me-2"></i>${resource.category}</span>
                        <span><i class="fas fa-eye me-2"></i>${resource.views.toLocaleString('fr-FR')} vues</span>
                        <span><i class="fas fa-clock me-2"></i>${dateLabel}</span>
                    </div>
                    <div class="resource-tags">
                        <span class="badge rounded-pill">${resource.profile}</span>
                        <span class="badge rounded-pill">${resource.category}</span>
                        <span class="badge rounded-pill">${resource.type}</span>
                    </div>
                </div>
            </article>
        </div>
    `;
}

function renderProfiles() {
    const container = document.getElementById('profileCards');
    if (!container) return;
    container.innerHTML = profiles.map(createProfileCard).join('');
}

function renderResources(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = data.map(createResourceCard).join('');
}

function getPopularResources() {
    return [...resources]
        .sort((a, b) => b.views - a.views)
        .slice(0, 6);
}

function getRecentResources() {
    return [...resources]
        .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
        .slice(0, 6);
}

function initSearch() {
    const form = document.getElementById('globalSearchForm');
    const input = document.getElementById('globalSearchInput');
    const resultsMessage = document.getElementById('globalSearchResults');
    if (!form || !input || !resultsMessage) return;

    const resultsGrid = document.createElement('div');
    resultsGrid.id = 'searchResultsGrid';
    resultsGrid.className = 'row g-4 mt-3';
    resultsGrid.setAttribute('aria-live', 'polite');
    resultsMessage.after(resultsGrid);

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const term = input.value.toLowerCase().trim();

        if (!term) {
            resultsMessage.textContent = '';
            resultsGrid.innerHTML = '';
            return;
        }

        const matches = resources.filter((resource) => {
            const profile = profiles.find((p) => p.key === resource.profile);
            const haystack = [
                resource.title,
                resource.description,
                resource.category,
                resource.type,
                profile?.name || '',
            ]
                .join(' ')
                .toLowerCase();
            return haystack.includes(term);
        });

        if (!matches.length) {
            resultsMessage.innerHTML = `<p>Aucun résultat pour "${term}"</p>`;
            resultsGrid.innerHTML = '';
            return;
        }

        resultsMessage.innerHTML = `<p>${matches.length} résultat${matches.length > 1 ? 's' : ''} trouvé${matches.length > 1 ? 's' : ''} pour "${term}"</p>`;
        resultsGrid.innerHTML = matches.map(createResourceCard).join('');
    });
}

function initPage() {
    renderProfiles();
    renderResources('popularResourcesGrid', getPopularResources());
    renderResources('recentResourcesGrid', getRecentResources());
    initSearch();
}

document.addEventListener('DOMContentLoaded', initPage);
