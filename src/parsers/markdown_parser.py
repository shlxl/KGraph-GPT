import re
from typing import List, Dict, Any

class MarkdownMultiDocumentParser:
    def __init__(self):
        # Regex to find document blocks: starts with /corpus/ and ends before next /corpus/ or end of file
        # It captures the document ID, source, date, and the content with sentence IDs
        self.doc_block_regex = re.compile(
            r"^\s*#\s*/corpus/(?P<doc_id>[^\s]+)\.txt\s*\n"  # Matches /corpus/d1_news_2025-03-12.txt
            r"^\s*#\s*元数据:\s*source=(?P<source>[^,]+),\s*date=(?P<date>[^,]+),\s*id=(?P<meta_id>[^\s]+)\s*\n" # Matches metadata
            r"(?P<content>(?:(?!^\s*#\s*/corpus/).)*)", # Captures content until next doc block or EOF
            re.DOTALL | re.MULTILINE
        )
        self.sentence_regex = re.compile(r"^(S\d+\s+.*)", re.MULTILINE) # Matches S1, S2, ...

    def parse(self, markdown_content: str) -> List[Dict[str, Any]]:
        documents = []
        for match in self.doc_block_regex.finditer(markdown_content):
            doc_id = match.group("doc_id")
            source = match.group("source")
            date = match.group("date")
            meta_id = match.group("meta_id") # This should match doc_id, but we'll use doc_id for consistency
            content_block = match.group("content").strip()

            # Extract sentences with their IDs
            sentences_with_ids = []
            for sent_match in self.sentence_regex.finditer(content_block):
                sentences_with_ids.append(sent_match.group(1))
            
            # Reconstruct content with sentence IDs for the LLM prompt
            text_with_sentence_ids = "\n".join(sentences_with_ids)

            documents.append({
                "doc_id": doc_id,
                "source": source,
                "date": date,
                "text_with_sentence_ids": text_with_sentence_ids
            })
        return documents

if __name__ == '__main__':
    # Example usage (for testing the parser directly)
    sample_markdown = """
# /corpus/d1_news_2025-03-12.txt
# 元数据: source=《珊瑚湾日报》, date=2025-03-12, id=d1
S1 珊瑚湾市政府今日与南海电力集团（简称NPG）及蓝珊研究所（简称BCRI）签署“海曦一号海上风电场”与“珊瑚复育2026”联合备忘录。
S2 备忘录约定：NPG出资2.4亿元，市政府专项资金0.6亿元，BCRI筹集海洋基金0.2亿元，合计3.2亿元。

# /corpus/d2_brief_2025-05-01.txt
# 元数据: source=BCRI科研简报, date=2025-05-01, id=d2
S1 BCRI公布基线监测：南礁珊瑚保护区的平均活珊瑚覆盖度为27%（±3%）。
S2 监测表明保护区北界外12公里处拟设风机组团，不在保护区边界内。
"""
    parser = MarkdownMultiDocumentParser()
    parsed_docs = parser.parse(sample_markdown)
    for doc in parsed_docs:
        print(f"Doc ID: {doc['doc_id']}")
        print(f"Source: {doc['source']}")
        print(f"Date: {doc['date']}")
        print(f"Content:\n{doc['text_with_sentence_ids']}\n---")
