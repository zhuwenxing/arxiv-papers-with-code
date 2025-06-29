import json
import pandas as pd
from datetime import datetime
import argparse
from pathlib import Path
from src.arxiv_client import ArxivPaperFetcher
from tqdm import tqdm


def save_results(papers: list, output_format: str, output_dir: str = "data"):
    """
    Save fetched papers in specified format
    """
    output_path = Path(output_dir)
    if not output_path.is_absolute():
        output_path = Path(__file__).parent / output_path
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_format == "json":
        filename = output_path / f"papers_with_code_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        print(f"\nSaved {len(papers)} papers to {filename}")
        
    elif output_format == "csv":
        filename = output_path / f"papers_with_code_{timestamp}.csv"
        df = pd.DataFrame(papers)
        df['code_links'] = df['code_links'].apply(lambda x: '; '.join(x) if x else '')
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\nSaved {len(papers)} papers to {filename}")
        
    elif output_format == "both":
        json_filename = output_path / f"papers_with_code_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        
        csv_filename = output_path / f"papers_with_code_{timestamp}.csv"
        df = pd.DataFrame(papers)
        df['code_links'] = df['code_links'].apply(lambda x: '; '.join(x) if x else '')
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        print(f"\nSaved {len(papers)} papers to:")
        print(f"  - {json_filename}")
        print(f"  - {csv_filename}")


def print_summary(papers: list):
    """
    Print summary statistics
    """
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total papers with code found: {len(papers)}")
    
    category_counts = {}
    for paper in papers:
        cat = paper['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("\nPapers by category:")
    for cat, count in category_counts.items():
        print(f"  - {cat}: {count}")
    
    github_papers = [p for p in papers if any('github.com' in link for link in p['code_links'])]
    print(f"\nPapers with GitHub links: {len(github_papers)}")
    
    print("\nSample papers found:")
    for i, paper in enumerate(papers[:5], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Authors: {paper['authors'][:50]}...")
        print(f"   ArXiv: https://arxiv.org/abs/{paper['arxiv_id']}")
        if paper['code_links']:
            print(f"   Code: {paper['code_links'][0]}")


def main():
    parser = argparse.ArgumentParser(description='Fetch ArXiv papers with open source code')
    parser.add_argument('--categories', nargs='+', 
                       default=['information_retrieval', 'databases'],
                       choices=['information_retrieval', 'databases'],
                       help='Categories to search (default: both)')
    parser.add_argument('--max-results', type=int, default=100,
                       help='Maximum results per category (default: 100)')
    parser.add_argument('--days-back', type=int, default=30,
                       help='Number of days to look back (default: 30)')
    parser.add_argument('--output-format', choices=['json', 'csv', 'both'],
                       default='both',
                       help='Output format (default: both)')
    parser.add_argument('--check-pages', action='store_true', default=True,
                       help='Check paper pages for additional code links')
    parser.add_argument('--output-dir', default='data',
                       help='Output directory (default: data)')
    
    args = parser.parse_args()
    
    print("ArXiv Paper Fetcher - Papers with Open Source Code")
    print("="*60)
    print(f"Categories: {', '.join(args.categories)}")
    print(f"Max results per category: {args.max_results}")
    print(f"Looking back: {args.days_back} days")
    print(f"Checking paper pages: {args.check_pages}")
    print("="*60)
    
    fetcher = ArxivPaperFetcher()
    
    papers = fetcher.get_papers_with_code(
        categories=args.categories,
        max_results_per_category=args.max_results,
        days_back=args.days_back,
        check_paper_pages=args.check_pages
    )
    
    if papers:
        save_results(papers, args.output_format, args.output_dir)
        print_summary(papers)
    else:
        print("\nNo papers with code found in the specified criteria.")


if __name__ == "__main__":
    main()