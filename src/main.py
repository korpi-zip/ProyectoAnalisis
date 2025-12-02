import os
import sys
from .parser import Tokenizer, Parser
from .analyzer import Analyzer
from .knowledge_base import KnowledgeBase

def analyze_file(filepath: str, analyzer: Analyzer):
    print(f"Analyzing {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        
        parser = Parser(tokens)
        program = parser.parse_program()
        
        complexity = analyzer.analyze(program)
        
        print(f"  Complexity: {complexity}")
        print("-" * 20)
        
    except Exception as e:
        print(f"  Error: {e}")
        print("-" * 20)

def main():
    # Initialize Knowledge Base
    kb_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base.json')
    kb = KnowledgeBase(kb_path)
    
    analyzer = Analyzer(kb)
    
    # Algorithms directory
    algo_dir = os.path.join(os.path.dirname(__file__), '..', 'algorithms')
    
    if not os.path.exists(algo_dir):
        print(f"Directory {algo_dir} not found.")
        return

    files = [f for f in os.listdir(algo_dir) if f.endswith('.txt') or f.endswith('.psc')]
    
    if not files:
        print("No algorithm files found in algorithms/ directory.")
        return
        
    for filename in files:
        filepath = os.path.join(algo_dir, filename)
        analyze_file(filepath, analyzer)

if __name__ == "__main__":
    main()
