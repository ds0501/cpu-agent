"""
PDF Indexer
PDF 파일을 읽어서 Chroma DB에 저장
"""
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.rag.store import ChromaStore
from pathlib import Path

class PDFIndexer:
    """PDF 색인"""
    
    def __init__(self):
        self.store = ChromaStore()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text(self, pdf_path: str) -> str:
        """PDF에서 텍스트 추출"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n[페이지 {page_num + 1}]\n{page_text}"
        
        return text
    
    def chunk_text(self, text: str, source: str) -> list:
        """텍스트를 청크로 분할"""
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk,
                "metadata": {
                    "source": source,
                    "chunk_id": i
                }
            })
        
        return documents
    
    def index_pdf(self, pdf_path: str) -> int:
        """
        PDF 색인
        
        Args:
            pdf_path: PDF 파일 경로
        
        Returns:
            색인된 청크 개수
        """
        print(f"📄 PDF 읽는 중: {pdf_path}")
        text = self.extract_text(pdf_path)
        
        print(f"✂️  텍스트 분할 중...")
        source = Path(pdf_path).name
        documents = self.chunk_text(text, source)
        
        print(f"💾 Chroma DB에 저장 중... ({len(documents)} 청크)")
        self.store.add_documents(documents)
        
        print(f"✅ 색인 완료!")
        return len(documents)


# CLI 사용
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python -m app.rag.indexer <PDF 파일 경로>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    indexer = PDFIndexer()
    indexer.index_pdf(pdf_path)