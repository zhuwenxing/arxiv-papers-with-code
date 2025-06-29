import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import pandas as pd


def load_all_papers(data_dir="docs/data"):
    """Load all paper JSON files and merge them"""
    papers_by_id = {}
    data_path = Path(data_dir)
    
    if not data_path.exists():
        return []
    
    for json_file in sorted(data_path.glob("papers_with_code_*.json")):
        with open(json_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
            for paper in papers:
                # Use arxiv_id as unique identifier
                papers_by_id[paper['arxiv_id']] = paper
    
    # Sort by published date (newest first)
    return sorted(papers_by_id.values(), 
                  key=lambda x: x['published'], 
                  reverse=True)


def generate_paper_card(paper):
    """Generate HTML card for a paper"""
    code_links_html = ""
    if paper['code_links']:
        links = []
        for link in paper['code_links']:
            if 'github.com' in link:
                links.append(f'<a href="{link}" target="_blank" class="code-link github">GitHub</a>')
            else:
                links.append(f'<a href="{link}" target="_blank" class="code-link">Code</a>')
        code_links_html = ' '.join(links)
    
    abstract_short = paper['abstract'][:300] + "..." if len(paper['abstract']) > 300 else paper['abstract']
    
    return f"""
    <div class="paper-card" data-category="{paper['category']}" data-date="{paper['published']}">
        <h3 class="paper-title">{paper['title']}</h3>
        <div class="paper-meta">
            <span class="authors">{paper['authors']}</span>
            <span class="date">{paper['published']}</span>
            <span class="category {paper['category']}">{paper['category'].replace('_', ' ').title()}</span>
        </div>
        <p class="abstract">{abstract_short}</p>
        <div class="paper-links">
            <a href="{paper['url']}" target="_blank" class="arxiv-link">ArXiv</a>
            <a href="{paper['pdf_url']}" target="_blank" class="pdf-link">PDF</a>
            {code_links_html}
        </div>
    </div>
    """


def generate_statistics(papers):
    """Generate statistics HTML"""
    total = len(papers)
    by_category = defaultdict(int)
    with_github = 0
    
    for paper in papers:
        by_category[paper['category']] += 1
        if any('github.com' in link for link in paper.get('code_links', [])):
            with_github += 1
    
    # Get recent papers (last 7 days)
    week_ago = (datetime.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
    recent = len([p for p in papers if p['published'] >= week_ago])
    
    stats_html = f"""
    <div class="statistics">
        <div class="stat-card">
            <h3>{total}</h3>
            <p>Total Papers</p>
        </div>
        <div class="stat-card">
            <h3>{with_github}</h3>
            <p>With GitHub</p>
        </div>
        <div class="stat-card">
            <h3>{recent}</h3>
            <p>Last 7 Days</p>
        </div>
        <div class="stat-card">
            <h3>{by_category.get('information_retrieval', 0)}</h3>
            <p>Information Retrieval</p>
        </div>
        <div class="stat-card">
            <h3>{by_category.get('databases', 0)}</h3>
            <p>Databases</p>
        </div>
    </div>
    """
    return stats_html


def generate_html(papers):
    """Generate the main HTML page"""
    papers_html = '\n'.join(generate_paper_card(paper) for paper in papers)
    stats_html = generate_statistics(papers)
    last_update = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ArXiv Papers with Code - IR & DB</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            border-radius: 8px;
            padding: 30px;
        }}
        
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .last-update {{
            color: #95a5a6;
            font-size: 0.9em;
        }}
        
        .statistics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card h3 {{
            color: #3498db;
            font-size: 2em;
            margin-bottom: 5px;
        }}
        
        .filters {{
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: #fff;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        
        .filter-btn:hover {{
            background: #f8f9fa;
        }}
        
        .filter-btn.active {{
            background: #3498db;
            color: #fff;
            border-color: #3498db;
        }}
        
        .search-box {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        
        .papers-grid {{
            display: grid;
            gap: 20px;
        }}
        
        .paper-card {{
            background: #fff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .paper-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        .paper-title {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        .paper-meta {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        
        .authors {{
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .category {{
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .category.information_retrieval {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        
        .category.databases {{
            background: #e3f2fd;
            color: #1565c0;
        }}
        
        .abstract {{
            color: #555;
            margin-bottom: 15px;
            line-height: 1.5;
        }}
        
        .paper-links {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .paper-links a {{
            padding: 6px 12px;
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        
        .arxiv-link {{
            background: #f44336;
            color: #fff;
        }}
        
        .arxiv-link:hover {{
            background: #d32f2f;
        }}
        
        .pdf-link {{
            background: #ff9800;
            color: #fff;
        }}
        
        .pdf-link:hover {{
            background: #f57c00;
        }}
        
        .code-link {{
            background: #4caf50;
            color: #fff;
        }}
        
        .code-link:hover {{
            background: #388e3c;
        }}
        
        .code-link.github {{
            background: #24292e;
        }}
        
        .code-link.github:hover {{
            background: #1a1e22;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            header {{
                padding: 20px;
            }}
            
            .paper-meta {{
                flex-direction: column;
                gap: 5px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>ArXiv Papers with Open Source Code</h1>
            <p class="subtitle">Information Retrieval & Database Research Papers</p>
            <p class="last-update">Last updated: {last_update}</p>
        </header>
        
        {stats_html}
        
        <div class="filters">
            <input type="text" class="search-box" id="searchBox" placeholder="Search papers by title, authors, or abstract...">
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">All Papers</button>
                <button class="filter-btn" data-filter="information_retrieval">Information Retrieval</button>
                <button class="filter-btn" data-filter="databases">Databases</button>
                <button class="filter-btn" data-filter="recent">Last 7 Days</button>
                <button class="filter-btn" data-filter="github">With GitHub</button>
            </div>
        </div>
        
        <div class="papers-grid" id="papersGrid">
            {papers_html}
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            No papers found matching your criteria.
        </div>
    </div>
    
    <script>
        // Filter functionality
        const filterButtons = document.querySelectorAll('.filter-btn');
        const paperCards = document.querySelectorAll('.paper-card');
        const searchBox = document.getElementById('searchBox');
        const noResults = document.getElementById('noResults');
        
        function filterPapers() {{
            const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
            const searchTerm = searchBox.value.toLowerCase();
            let visibleCount = 0;
            
            paperCards.forEach(card => {{
                let showCard = true;
                
                // Category filter
                if (activeFilter !== 'all') {{
                    if (activeFilter === 'recent') {{
                        const paperDate = new Date(card.dataset.date);
                        const weekAgo = new Date();
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        showCard = paperDate >= weekAgo;
                    }} else if (activeFilter === 'github') {{
                        showCard = card.innerHTML.includes('github.com');
                    }} else {{
                        showCard = card.dataset.category === activeFilter;
                    }}
                }}
                
                // Search filter
                if (showCard && searchTerm) {{
                    const text = card.textContent.toLowerCase();
                    showCard = text.includes(searchTerm);
                }}
                
                card.style.display = showCard ? 'block' : 'none';
                if (showCard) visibleCount++;
            }});
            
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }}
        
        filterButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filterPapers();
            }});
        }});
        
        searchBox.addEventListener('input', filterPapers);
        
        // Initialize
        filterPapers();
    </script>
</body>
</html>"""
    
    return html_content


def main():
    # Create docs directory if it doesn't exist
    script_dir = Path(__file__).parent
    docs_dir = script_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    data_dir = docs_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Load all papers
    papers = load_all_papers(str(data_dir))
    
    # Generate HTML
    html_content = generate_html(papers)
    
    # Save HTML file
    index_path = docs_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated website with {len(papers)} papers")
    print(f"Website saved to: {index_path}")


if __name__ == "__main__":
    main()