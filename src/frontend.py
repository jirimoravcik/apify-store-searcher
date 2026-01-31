"""Frontend HTML/CSS/JS generator with neobrutalism design."""

from .categories import CATEGORIES, CATEGORY_DISPLAY_NAMES

# Apify brand colors
COLORS = {
    "blue": "#246dff",
    "green": "#20a34e",
    "orange": "#f86606",
    "black": "#000000",
    "white": "#ffffff",
    "cream": "#fffef0",
    "light_blue": "#e8f0ff",
    "light_green": "#e6f7ec",
    "light_orange": "#fff4eb",
}


def get_html() -> str:
    """Generate the main HTML page with neobrutalism styling."""

    # Generate category buttons
    category_buttons = "\n".join(
        f'<button class="category-btn" data-category="{cat}">{CATEGORY_DISPLAY_NAMES.get(cat, cat)}</button>'
        for cat in CATEGORIES
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apify Store - ML Enhanced Search</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        {get_css()}
    </style>
</head>
<body>
    <div class="page-wrapper">
        <!-- Decorative shapes -->
        <div class="deco-shape deco-1"></div>
        <div class="deco-shape deco-2"></div>
        <div class="deco-shape deco-3"></div>

        <div class="container">
            <!-- Header -->
            <header class="header">
                <div class="logo">
                    <span class="logo-icon">
                        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                            <rect x="2" y="2" width="16" height="16" fill="{COLORS['blue']}" stroke="{COLORS['black']}" stroke-width="3"/>
                            <rect x="22" y="2" width="16" height="16" fill="{COLORS['green']}" stroke="{COLORS['black']}" stroke-width="3"/>
                            <rect x="12" y="22" width="16" height="16" fill="{COLORS['orange']}" stroke="{COLORS['black']}" stroke-width="3"/>
                        </svg>
                    </span>
                    <h1 class="logo-text">Apify Store</h1>
                </div>
                <p class="tagline">ML-Enhanced Actor Discovery</p>
            </header>

            <!-- Search Section -->
            <div class="search-section">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search for Actors..." class="search-input">
                    <button id="searchBtn" class="btn btn-search">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                            <circle cx="11" cy="11" r="8"/>
                            <path d="M21 21l-4.35-4.35"/>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Category Pills -->
            <div class="categories-section">
                <button class="category-btn active" data-category="">All</button>
                {category_buttons}
            </div>

            <!-- Results Info -->
            <div class="results-header">
                <h2 class="results-title" id="resultsTitle">All Actors</h2>
                <span class="results-count" id="resultsCount"></span>
            </div>

            <!-- Results Grid -->
            <div id="results" class="results-grid">
                <!-- Results will be inserted here -->
            </div>

            <!-- Pagination -->
            <div id="pagination" class="pagination hidden">
                <button id="prevBtn" class="pagination-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M15 18l-6-6 6-6"/>
                    </svg>
                    Previous
                </button>
                <span id="pageInfo" class="page-info">Page 1</span>
                <button id="nextBtn" class="pagination-btn">
                    Next
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M9 18l6-6-6-6"/>
                    </svg>
                </button>
            </div>

            <!-- Loading State -->
            <div id="loading" class="loading hidden">
                <div class="loading-spinner">
                    <div class="spinner-ring spinner-blue"></div>
                    <div class="spinner-ring spinner-green"></div>
                    <div class="spinner-ring spinner-orange"></div>
                </div>
                <p>Loading Actors...</p>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p>Powered by <strong>ML Classification</strong> for better category matching</p>
        </footer>
    </div>

    <script>
        {get_js()}
    </script>
</body>
</html>"""


def get_css() -> str:
    """Generate neobrutalism CSS styles."""
    return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
            background: {COLORS['cream']};
            color: {COLORS['black']};
            line-height: 1.5;
            min-height: 100vh;
        }}

        .page-wrapper {{
            position: relative;
            overflow-x: hidden;
            min-height: 100vh;
        }}

        /* Decorative shapes */
        .deco-shape {{
            position: fixed;
            border: 4px solid {COLORS['black']};
            z-index: -1;
            pointer-events: none;
        }}

        .deco-1 {{
            width: 200px;
            height: 200px;
            background: {COLORS['light_blue']};
            top: 10%;
            left: -100px;
            transform: rotate(15deg);
        }}

        .deco-2 {{
            width: 150px;
            height: 150px;
            background: {COLORS['light_green']};
            top: 40%;
            right: -75px;
            border-radius: 50%;
        }}

        .deco-3 {{
            width: 120px;
            height: 120px;
            background: {COLORS['light_orange']};
            bottom: 20%;
            left: 5%;
            transform: rotate(-10deg);
        }}

        .container {{
            max-width: 1300px;
            margin: 0 auto;
            padding: 2rem;
        }}

        /* Header */
        .header {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding-top: 1rem;
        }}

        .logo {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 0.75rem;
        }}

        .logo-text {{
            font-size: 3rem;
            font-weight: 700;
            letter-spacing: -2px;
            color: {COLORS['black']};
        }}

        .tagline {{
            font-size: 1.1rem;
            color: #555;
            font-weight: 500;
        }}

        /* Search Section */
        .search-section {{
            max-width: 700px;
            margin: 0 auto 2rem;
        }}

        .search-box {{
            display: flex;
            gap: 0;
            background: {COLORS['white']};
            border: 4px solid {COLORS['black']};
            box-shadow: 6px 6px 0 {COLORS['black']};
        }}

        .search-input {{
            flex: 1;
            padding: 1.25rem 1.5rem;
            font-size: 1.1rem;
            font-family: inherit;
            border: none;
            outline: none;
            background: transparent;
        }}

        .search-input::placeholder {{
            color: #888;
        }}

        .btn-search {{
            padding: 1rem 1.5rem;
            background: {COLORS['blue']};
            color: {COLORS['white']};
            border: none;
            border-left: 4px solid {COLORS['black']};
            cursor: pointer;
            transition: background 0.2s;
        }}

        .btn-search:hover {{
            background: #1a5ad4;
        }}

        /* Category Pills */
        .categories-section {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            justify-content: center;
            margin-bottom: 2.5rem;
            padding: 0 1rem;
        }}

        .category-btn {{
            padding: 0.6rem 1.25rem;
            font-size: 0.9rem;
            font-weight: 600;
            font-family: inherit;
            background: {COLORS['white']};
            color: {COLORS['black']};
            border: 3px solid {COLORS['black']};
            cursor: pointer;
            transition: all 0.15s ease;
            box-shadow: 3px 3px 0 {COLORS['black']};
        }}

        .category-btn:hover {{
            transform: translate(-2px, -2px);
            box-shadow: 5px 5px 0 {COLORS['black']};
        }}

        .category-btn:active {{
            transform: translate(1px, 1px);
            box-shadow: 2px 2px 0 {COLORS['black']};
        }}

        .category-btn.active {{
            background: {COLORS['blue']};
            color: {COLORS['white']};
        }}

        .category-btn[data-category="AGENTS"].active {{
            background: {COLORS['green']};
        }}

        .category-btn[data-category="AI"].active {{
            background: {COLORS['orange']};
        }}

        .category-btn[data-category="MCP_SERVERS"].active {{
            background: {COLORS['green']};
        }}

        /* Results Header */
        .results-header {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 1.5rem;
            padding: 0 0.25rem;
        }}

        .results-title {{
            font-size: 1.75rem;
            font-weight: 700;
        }}

        .results-count {{
            font-size: 0.95rem;
            color: #666;
            font-weight: 500;
        }}

        /* Results Grid */
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.5rem;
        }}

        /* Actor Card */
        .actor-card {{
            background: {COLORS['white']};
            border: 4px solid {COLORS['black']};
            box-shadow: 6px 6px 0 {COLORS['black']};
            padding: 1.5rem;
            transition: all 0.2s ease;
            position: relative;
        }}

        .actor-card:hover {{
            transform: translate(-4px, -4px);
            box-shadow: 10px 10px 0 {COLORS['black']};
        }}

        .actor-header {{
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            margin-bottom: 1rem;
        }}

        .actor-icon {{
            width: 60px;
            height: 60px;
            border: 3px solid {COLORS['black']};
            object-fit: cover;
            flex-shrink: 0;
            background: {COLORS['white']};
        }}

        .actor-icon-placeholder {{
            width: 60px;
            height: 60px;
            border: 3px solid {COLORS['black']};
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.5rem;
            flex-shrink: 0;
        }}

        .actor-icon-placeholder.blue {{ background: {COLORS['light_blue']}; color: {COLORS['blue']}; }}
        .actor-icon-placeholder.green {{ background: {COLORS['light_green']}; color: {COLORS['green']}; }}
        .actor-icon-placeholder.orange {{ background: {COLORS['light_orange']}; color: {COLORS['orange']}; }}

        .actor-title-section {{
            flex: 1;
            min-width: 0;
        }}

        .actor-title {{
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
            line-height: 1.3;
        }}

        .actor-title a {{
            color: {COLORS['black']};
            text-decoration: none;
        }}

        .actor-title a:hover {{
            color: {COLORS['blue']};
        }}

        .actor-author {{
            font-size: 0.85rem;
            color: #666;
        }}

        .actor-author a {{
            color: inherit;
            text-decoration: none;
        }}

        .actor-author a:hover {{
            color: {COLORS['blue']};
        }}

        .actor-description {{
            font-size: 0.95rem;
            color: #444;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.5;
        }}

        .actor-categories {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-bottom: 1rem;
        }}

        .category-tag {{
            padding: 0.2rem 0.6rem;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            border: 2px solid {COLORS['black']};
            background: {COLORS['cream']};
        }}

        .category-tag.agents {{
            background: {COLORS['light_green']};
            color: {COLORS['green']};
        }}

        .category-tag.ai {{
            background: {COLORS['light_orange']};
            color: {COLORS['orange']};
        }}

        .category-tag.mcp {{
            background: {COLORS['light_blue']};
            color: {COLORS['blue']};
        }}

        .actor-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 0.75rem;
            border-top: 2px solid {COLORS['black']};
        }}

        .actor-stats {{
            display: flex;
            gap: 1.25rem;
            font-size: 0.85rem;
            color: #555;
            font-weight: 500;
        }}

        .stat {{
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}

        .stat-icon {{
            font-size: 1rem;
        }}

        .actor-pricing {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.6rem;
            background: {COLORS['cream']};
            border: 2px solid {COLORS['black']};
        }}

        .actor-pricing.compute {{
            background: {COLORS['light_green']};
            color: {COLORS['green']};
        }}

        .actor-pricing.subscription {{
            background: {COLORS['light_orange']};
            color: #b34700;
        }}

        .actor-pricing.per-result,
        .actor-pricing.per-event {{
            background: {COLORS['light_blue']};
            color: #1a4db3;
        }}

        /* Pagination */
        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1.5rem;
            margin-top: 2.5rem;
            padding: 1rem;
        }}

        .pagination.hidden {{
            display: none;
        }}

        .pagination-btn {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.25rem;
            font-size: 0.95rem;
            font-weight: 600;
            font-family: inherit;
            background: {COLORS['white']};
            color: {COLORS['black']};
            border: 3px solid {COLORS['black']};
            cursor: pointer;
            transition: all 0.15s ease;
            box-shadow: 4px 4px 0 {COLORS['black']};
        }}

        .pagination-btn:hover:not(:disabled) {{
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0 {COLORS['black']};
            background: {COLORS['blue']};
            color: {COLORS['white']};
        }}

        .pagination-btn:active:not(:disabled) {{
            transform: translate(1px, 1px);
            box-shadow: 2px 2px 0 {COLORS['black']};
        }}

        .pagination-btn:disabled {{
            opacity: 0.4;
            cursor: not-allowed;
        }}

        .page-info {{
            font-size: 1rem;
            font-weight: 600;
            color: {COLORS['black']};
            padding: 0.5rem 1rem;
            background: {COLORS['light_blue']};
            border: 3px solid {COLORS['black']};
        }}

        /* Loading State */
        .loading {{
            text-align: center;
            padding: 4rem 2rem;
        }}

        .loading.hidden {{
            display: none;
        }}

        .loading-spinner {{
            position: relative;
            width: 60px;
            height: 60px;
            margin: 0 auto 1.5rem;
        }}

        .spinner-ring {{
            position: absolute;
            width: 100%;
            height: 100%;
            border: 4px solid transparent;
            border-radius: 50%;
            animation: spin 1.2s linear infinite;
        }}

        .spinner-blue {{
            border-top-color: {COLORS['blue']};
            animation-delay: 0s;
        }}

        .spinner-green {{
            border-right-color: {COLORS['green']};
            animation-delay: 0.15s;
        }}

        .spinner-orange {{
            border-bottom-color: {COLORS['orange']};
            animation-delay: 0.3s;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        .loading p {{
            font-weight: 600;
            color: #555;
        }}

        /* Empty State */
        .empty-state {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 2rem;
            background: {COLORS['white']};
            border: 4px solid {COLORS['black']};
            box-shadow: 6px 6px 0 {COLORS['black']};
        }}

        .empty-state h3 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        .empty-state p {{
            color: #666;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 2rem;
            margin-top: 3rem;
            color: #666;
            font-size: 0.9rem;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            .logo-text {{
                font-size: 2rem;
            }}

            .search-box {{
                box-shadow: 4px 4px 0 {COLORS['black']};
            }}

            .categories-section {{
                gap: 0.5rem;
            }}

            .category-btn {{
                padding: 0.5rem 1rem;
                font-size: 0.85rem;
            }}

            .results-grid {{
                grid-template-columns: 1fr;
                gap: 1.25rem;
            }}

            .actor-card {{
                box-shadow: 4px 4px 0 {COLORS['black']};
            }}

            .deco-shape {{
                display: none;
            }}
        }}
    """


def get_js() -> str:
    """Generate frontend JavaScript."""
    return """
        const searchInput = document.getElementById('searchInput');
        const searchBtn = document.getElementById('searchBtn');
        const resultsContainer = document.getElementById('results');
        const resultsCount = document.getElementById('resultsCount');
        const resultsTitle = document.getElementById('resultsTitle');
        const loading = document.getElementById('loading');
        const categoryBtns = document.querySelectorAll('.category-btn');
        const pagination = document.getElementById('pagination');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const pageInfo = document.getElementById('pageInfo');

        let currentCategory = '';
        let currentActors = [];
        let currentOffset = 0;
        let currentTotal = 0;
        const PAGE_SIZE = 24;
        const categoryNames = {
            '': 'All Actors',
            'SOCIAL_MEDIA': 'Social Media',
            'AI': 'AI',
            'AGENTS': 'Agents',
            'LEAD_GENERATION': 'Lead Generation',
            'ECOMMERCE': 'E-commerce',
            'SEO_TOOLS': 'SEO Tools',
            'JOBS': 'Jobs',
            'MCP_SERVERS': 'MCP Servers',
            'NEWS': 'News',
            'REAL_ESTATE': 'Real Estate',
            'DEVELOPER_TOOLS': 'Developer Tools',
            'TRAVEL': 'Travel',
            'VIDEOS': 'Videos',
            'AUTOMATION': 'Automation',
            'INTEGRATIONS': 'Integrations',
            'OPEN_SOURCE': 'Open Source',
            'OTHER': 'Other'
        };

        // Initial load
        search();

        // Event listeners
        searchBtn.addEventListener('click', () => {
            // Search within current category (don't clear category)
            currentOffset = 0;
            search();
        });
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                // Search within current category (don't clear category)
                currentOffset = 0;
                search();
            }
        });

        categoryBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Keep search term when changing category
                categoryBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentCategory = btn.dataset.category;
                currentOffset = 0;
                search();
            });
        });

        prevBtn.addEventListener('click', () => {
            if (currentOffset >= PAGE_SIZE) {
                currentOffset -= PAGE_SIZE;
                search();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentOffset + PAGE_SIZE < currentTotal) {
                currentOffset += PAGE_SIZE;
                search();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });

        async function search() {
            const query = searchInput.value.trim();

            showLoading();

            try {
                const params = new URLSearchParams();
                if (query) params.append('q', query);
                if (currentCategory) params.append('category', currentCategory);
                params.append('limit', PAGE_SIZE.toString());
                params.append('offset', currentOffset.toString());

                const response = await fetch(`/api/search?${params}`);
                const data = await response.json();

                currentActors = data.actors || [];
                currentTotal = data.total || 0;

                let title;
                if (query && currentCategory) {
                    title = `"${query}" in ${categoryNames[currentCategory]}`;
                } else if (query) {
                    title = `Results for "${query}"`;
                } else {
                    title = categoryNames[currentCategory] || 'All Actors';
                }
                resultsTitle.textContent = title;

                renderResults(currentActors, currentTotal);
                updatePagination();
            } catch (error) {
                console.error('Search error:', error);
                renderError('Failed to load Actors. Please try again.');
                pagination.classList.add('hidden');
            }

            hideLoading();
        }

        function showLoading() {
            loading.classList.remove('hidden');
            resultsContainer.innerHTML = '';
        }

        function hideLoading() {
            loading.classList.add('hidden');
        }

        function renderResults(actors, total) {
            const start = currentOffset + 1;
            const end = Math.min(currentOffset + actors.length, total);
            resultsCount.textContent = `${start}-${end} of ${total} Actors`;

            if (actors.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="empty-state">
                        <h3>No Actors found</h3>
                        <p>Try adjusting your search or category filter</p>
                    </div>
                `;
                return;
            }

            resultsContainer.innerHTML = actors.map(actor => renderActorCard(actor)).join('');
        }

        function updatePagination() {
            const totalPages = Math.ceil(currentTotal / PAGE_SIZE);
            const currentPage = Math.floor(currentOffset / PAGE_SIZE) + 1;

            if (totalPages <= 1) {
                pagination.classList.add('hidden');
                return;
            }

            pagination.classList.remove('hidden');
            pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;

            prevBtn.disabled = currentOffset === 0;
            nextBtn.disabled = currentOffset + PAGE_SIZE >= currentTotal;
        }

        function renderActorCard(actor) {
            const colors = ['blue', 'green', 'orange'];
            const colorClass = colors[Math.abs(hashCode(actor.title || '')) % colors.length];

            const iconHtml = actor.pictureUrl
                ? `<img src="${actor.pictureUrl}" alt="${escapeHtml(actor.title)}" class="actor-icon" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="actor-icon-placeholder ${colorClass}" style="display:none">${(actor.title || '?')[0].toUpperCase()}</div>`
                : `<div class="actor-icon-placeholder ${colorClass}">${(actor.title || '?')[0].toUpperCase()}</div>`;

            const categories = (actor.categories || []).slice(0, 3).map(cat => {
                const catLower = cat.toLowerCase();
                let specialClass = '';
                if (catLower === 'agents') specialClass = 'agents';
                else if (catLower === 'ai') specialClass = 'ai';
                else if (catLower === 'mcp_servers') specialClass = 'mcp';
                return `<span class="category-tag ${specialClass}">${cat.replace(/_/g, ' ')}</span>`;
            }).join('');

            const stats = actor.stats || {};
            const users = formatNumber(stats.totalUsers || 0);
            const rating = stats.actorReviewRating ? stats.actorReviewRating.toFixed(1) : null;
            const reviews = stats.actorReviewCount || 0;

            const actorUrl = actor.url || `https://apify.com/${actor.username}/${actor.name}`;
            const authorUrl = `https://apify.com/${actor.username}`;

            // Pricing display
            const pricing = actor.currentPricingInfo || {};
            const pricingModel = pricing.pricingModel || 'FREE';
            let pricingLabel = '';
            let pricingClass = '';

            if (pricingModel === 'FREE') {
                pricingLabel = 'Pay for compute';
                pricingClass = 'compute';
            } else if (pricingModel === 'FLAT_PRICE_PER_MONTH') {
                const price = pricing.pricePerUnitUsd;
                pricingLabel = price ? `$${Math.round(price)}/mo` : 'Subscription';
                pricingClass = 'subscription';
            } else if (pricingModel === 'PRICE_PER_DATASET_ITEM') {
                pricingLabel = 'Pay per result';
                pricingClass = 'per-result';
            } else if (pricingModel === 'PAY_PER_EVENT') {
                pricingLabel = 'Pay per event';
                pricingClass = 'per-event';
            } else {
                pricingLabel = 'Paid';
            }

            const ratingHtml = rating
                ? `<span class="stat"><span class="stat-icon">&#9733;</span> ${rating} (${reviews})</span>`
                : '';

            return `
                <div class="actor-card">
                    <div class="actor-header">
                        ${iconHtml}
                        <div class="actor-title-section">
                            <div class="actor-title">
                                <a href="${actorUrl}" target="_blank" rel="noopener">${escapeHtml(actor.title || 'Untitled')}</a>
                            </div>
                            <div class="actor-author">
                                <a href="${authorUrl}" target="_blank" rel="noopener">${escapeHtml(actor.username || '')}</a>
                            </div>
                        </div>
                    </div>
                    <div class="actor-description">${escapeHtml(actor.description || 'No description available')}</div>
                    <div class="actor-categories">${categories}</div>
                    <div class="actor-footer">
                        <div class="actor-stats">
                            <span class="stat"><span class="stat-icon">&#128101;</span> ${users}</span>
                            ${ratingHtml}
                        </div>
                        <span class="actor-pricing ${pricingClass}">${pricingLabel}</span>
                    </div>
                </div>
            `;
        }

        function renderError(message) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <h3>Error</h3>
                    <p>${escapeHtml(message)}</p>
                </div>
            `;
        }

        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function hashCode(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                const char = str.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash;
            }
            return hash;
        }
    """
