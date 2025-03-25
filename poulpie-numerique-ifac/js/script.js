// Fonctionnalités de recherche et de filtrage
document.addEventListener('DOMContentLoaded', function() {
    // Gestion des filtres
    const filterButtons = document.querySelectorAll('.filter-btn');
    const toolCards = document.querySelectorAll('.tool-card');
    
    // Fonction pour filtrer les outils
    function filterTools(filter) {
        toolCards.forEach(card => {
            if (filter === 'all') {
                card.style.display = 'flex';
            } else {
                if (card.getAttribute('data-type') === filter) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    }
    
    // Ajouter les écouteurs d'événements aux boutons de filtre
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Retirer la classe active de tous les boutons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Ajouter la classe active au bouton cliqué
            this.classList.add('active');
            
            // Récupérer le filtre sélectionné
            const filter = this.getAttribute('data-filter');
            
            // Filtrer les cartes d'outils
            filterTools(filter);
            
            // Mettre à jour l'URL avec le filtre sélectionné
            updateUrlParams('filter', filter);
        });
    });
    
    // Fonctionnalité de recherche
    const searchInput = document.querySelector('.search-bar input');
    const searchButton = document.querySelector('.search-bar button');
    
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        
        // Si le terme de recherche est vide, afficher tous les outils
        if (searchTerm === '') {
            toolCards.forEach(card => {
                card.style.display = 'flex';
            });
            
            // Réinitialiser les filtres
            filterButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelector('[data-filter="all"]').classList.add('active');
            
            // Mettre à jour l'URL en supprimant le paramètre de recherche
            updateUrlParams('search', null);
            return;
        }
        
        // Compter le nombre de résultats
        let resultCount = 0;
        
        toolCards.forEach(card => {
            const toolName = card.querySelector('.tool-name').textContent.toLowerCase();
            const toolDescription = card.querySelector('.tool-description').textContent.toLowerCase();
            const toolUsage = card.querySelector('.tool-usage p').textContent.toLowerCase();
            
            // Recherche améliorée qui prend en compte le nom, la description et l'utilisation
            if (toolName.includes(searchTerm) || 
                toolDescription.includes(searchTerm) || 
                toolUsage.includes(searchTerm)) {
                card.style.display = 'flex';
                resultCount++;
                
                // Mettre en surbrillance les termes de recherche
                highlightSearchTerm(card, searchTerm);
            } else {
                card.style.display = 'none';
            }
        });
        
        // Réinitialiser les filtres
        filterButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelector('[data-filter="all"]').classList.add('active');
        
        // Mettre à jour l'URL avec le terme de recherche
        updateUrlParams('search', searchTerm);
        
        // Afficher un message de résultats
        displaySearchResults(resultCount, searchTerm);
    }
    
    // Fonction pour mettre en surbrillance les termes de recherche
    function highlightSearchTerm(card, term) {
        // Réinitialiser d'abord tout surlignage précédent
        resetHighlighting(card);
        
        // Fonction pour surligner le texte dans un élément
        function highlightText(element, term) {
            const originalText = element.textContent;
            const lowerText = originalText.toLowerCase();
            const startIndex = lowerText.indexOf(term);
            
            if (startIndex >= 0) {
                const endIndex = startIndex + term.length;
                const beforeTerm = originalText.substring(0, startIndex);
                const matchedTerm = originalText.substring(startIndex, endIndex);
                const afterTerm = originalText.substring(endIndex);
                
                element.innerHTML = beforeTerm + '<span class="highlight">' + matchedTerm + '</span>' + afterTerm;
            }
        }
        
        // Surligner dans le nom, la description et l'utilisation
        highlightText(card.querySelector('.tool-name'), term);
        highlightText(card.querySelector('.tool-description'), term);
        highlightText(card.querySelector('.tool-usage p'), term);
    }
    
    // Fonction pour réinitialiser le surlignage
    function resetHighlighting(card) {
        card.querySelector('.tool-name').innerHTML = card.querySelector('.tool-name').textContent;
        card.querySelector('.tool-description').innerHTML = card.querySelector('.tool-description').textContent;
        card.querySelector('.tool-usage p').innerHTML = card.querySelector('.tool-usage p').textContent;
    }
    
    // Fonction pour afficher les résultats de recherche
    function displaySearchResults(count, term) {
        // Vérifier si un élément de résultats existe déjà
        let resultsElement = document.querySelector('.search-results');
        
        // Si non, créer un nouvel élément
        if (!resultsElement) {
            resultsElement = document.createElement('div');
            resultsElement.className = 'search-results';
            document.querySelector('.search-bar').after(resultsElement);
        }
        
        // Mettre à jour le contenu
        if (count === 0) {
            resultsElement.innerHTML = `<p>Aucun résultat trouvé pour "${term}"</p>`;
        } else {
            resultsElement.innerHTML = `<p>${count} outil${count > 1 ? 's' : ''} trouvé${count > 1 ? 's' : ''} pour "${term}"</p>`;
        }
        
        // Afficher l'élément
        resultsElement.style.display = 'block';
    }
    
    // Fonction pour mettre à jour les paramètres d'URL
    function updateUrlParams(key, value) {
        const url = new URL(window.location.href);
        
        if (value === null || value === 'all') {
            url.searchParams.delete(key);
        } else {
            url.searchParams.set(key, value);
        }
        
        // Mettre à jour l'URL sans recharger la page
        window.history.pushState({}, '', url);
    }
    
    // Ajouter les écouteurs d'événements pour la recherche
    searchButton.addEventListener('click', performSearch);
    
    searchInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            performSearch();
        }
        
        // Recherche en temps réel après 500ms d'inactivité
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(performSearch, 500);
    });
    
    // Effacer les résultats quand l'utilisateur efface le champ de recherche
    searchInput.addEventListener('input', function() {
        if (this.value === '') {
            // Réinitialiser l'affichage
            toolCards.forEach(card => {
                card.style.display = 'flex';
                resetHighlighting(card);
            });
            
            // Cacher le message de résultats
            const resultsElement = document.querySelector('.search-results');
            if (resultsElement) {
                resultsElement.style.display = 'none';
            }
            
            // Réinitialiser les filtres
            filterButtons.forEach(btn => btn.classList.remove('active'));
            document.querySelector('[data-filter="all"]').classList.add('active');
            
            // Mettre à jour l'URL
            updateUrlParams('search', null);
        }
    });
    
    // Animation au survol des cartes
    toolCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 3px 10px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Charger les paramètres d'URL au chargement de la page
    function loadUrlParams() {
        const url = new URL(window.location.href);
        
        // Charger le filtre depuis l'URL
        const filter = url.searchParams.get('filter');
        if (filter) {
            const filterButton = document.querySelector(`[data-filter="${filter}"]`);
            if (filterButton) {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                filterButton.classList.add('active');
                filterTools(filter);
            }
        }
        
        // Charger la recherche depuis l'URL
        const search = url.searchParams.get('search');
        if (search) {
            searchInput.value = search;
            performSearch();
        }
    }
    
    // Charger les paramètres d'URL au démarrage
    loadUrlParams();
    
    // Ajouter des styles CSS pour le surlignage
    const style = document.createElement('style');
    style.textContent = `
        .highlight {
            background-color: #ffed00;
            font-weight: bold;
            padding: 0 2px;
            border-radius: 2px;
        }
        .search-results {
            margin-top: 10px;
            padding: 8px 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            color: #0069b4;
        }
    `;
    document.head.appendChild(style);
});
