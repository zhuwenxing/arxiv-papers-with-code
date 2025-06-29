import arxiv
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import requests
import time


class ArxivPaperFetcher:
    def __init__(self):
        self.categories = {
            'information_retrieval': 'cs.IR',
            'databases': 'cs.DB'
        }
        self.code_patterns = [
            r'github\.com/[\w-]+/[\w-]+',
            r'gitlab\.com/[\w-]+/[\w-]+',
            r'bitbucket\.org/[\w-]+/[\w-]+',
            r'code\.google\.com/[\w-]+',
            r'sourceforge\.net/projects/[\w-]+',
            r'our code is available at',
            r'code is available at',
            r'implementation is available at',
            r'source code:',
            r'code repository:',
        ]
        
    def search_papers(self, 
                     category: str, 
                     max_results: int = 100,
                     days_back: int = 30) -> List[arxiv.Result]:
        """
        Search for papers in specific category within the last N days
        """
        if category not in self.categories:
            raise ValueError(f"Category {category} not supported")
        
        query = f"cat:{self.categories[category]}"
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        results = []
        
        for result in search.results():
            if result.published.replace(tzinfo=None) < cutoff_date:
                break
            results.append(result)
            
        return results
    
    def has_code_link(self, paper: arxiv.Result) -> Dict[str, any]:
        """
        Check if paper has code links in abstract or comments
        """
        text_to_check = f"{paper.summary} {paper.comment or ''}"
        
        code_links = []
        has_code = False
        
        for pattern in self.code_patterns:
            matches = re.findall(pattern, text_to_check.lower())
            if matches:
                has_code = True
                if 'github.com' in pattern or 'gitlab.com' in pattern:
                    for match in matches:
                        if match not in code_links:
                            code_links.append(match)
        
        github_matches = re.findall(r'github\.com/([\w-]+/[\w-]+)', text_to_check, re.IGNORECASE)
        for match in github_matches:
            full_url = f"https://github.com/{match}"
            if full_url not in code_links:
                code_links.append(full_url)
                has_code = True
        
        return {
            'has_code': has_code,
            'code_links': code_links
        }
    
    def check_paper_page_for_code(self, arxiv_id: str) -> Dict[str, any]:
        """
        Check the paper's ArXiv page for code links
        """
        url = f"https://arxiv.org/abs/{arxiv_id}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                text_content = soup.get_text().lower()
                code_info = {'has_code': False, 'code_links': []}
                
                for pattern in self.code_patterns:
                    if re.search(pattern, text_content):
                        code_info['has_code'] = True
                
                github_links = soup.find_all('a', href=re.compile(r'github\.com/[\w-]+/[\w-]+'))
                for link in github_links:
                    href = link.get('href')
                    if href and href not in code_info['code_links']:
                        code_info['code_links'].append(href)
                        code_info['has_code'] = True
                
                return code_info
        except Exception as e:
            print(f"Error checking paper page {arxiv_id}: {e}")
            
        return {'has_code': False, 'code_links': []}
    
    def get_papers_with_code(self, 
                           categories: List[str], 
                           max_results_per_category: int = 100,
                           days_back: int = 30,
                           check_paper_pages: bool = True) -> List[Dict]:
        """
        Get papers with code from specified categories
        """
        papers_with_code = []
        
        for category in categories:
            print(f"\nSearching {category} papers...")
            papers = self.search_papers(category, max_results_per_category, days_back)
            
            for paper in papers:
                code_info = self.has_code_link(paper)
                
                if not code_info['has_code'] and check_paper_pages:
                    time.sleep(0.5)  # Be respectful to the server
                    page_code_info = self.check_paper_page_for_code(paper.entry_id.split('/')[-1])
                    if page_code_info['has_code']:
                        code_info = page_code_info
                
                if code_info['has_code']:
                    paper_data = {
                        'title': paper.title,
                        'authors': ', '.join([author.name for author in paper.authors]),
                        'published': paper.published.strftime('%Y-%m-%d'),
                        'arxiv_id': paper.entry_id.split('/')[-1],
                        'url': paper.entry_id,
                        'pdf_url': paper.pdf_url,
                        'category': category,
                        'primary_category': paper.primary_category,
                        'abstract': paper.summary,
                        'code_links': code_info['code_links'],
                        'comment': paper.comment
                    }
                    papers_with_code.append(paper_data)
                    print(f"Found paper with code: {paper.title[:60]}...")
        
        return papers_with_code