"""
Embedding Service - Dịch vụ tạo Embeddings
Xử lý việc chuyển đổi văn bản thành vectors sử dụng Gemini text-embedding-004

=============================================================================
                    LEARNING NOTES - HỌC VỀ EMBEDDINGS
=============================================================================

1. EMBEDDINGS LÀ GÌ? (What are Embeddings?)
   =========================================
   
   - Định nghĩa đơn giản (Simple definition):
     * Embeddings = cách biểu diễn text bằng số (numerical representation)
     * Chuyển đổi từ, câu, đoạn văn → mảng các số thực (array of floats)
     * Mỗi text → 1 điểm trong không gian nhiều chiều (multidimensional space)
   
   - Ví dụ cụ thể (Concrete example):
     * Input text: "con mèo"
     * Output vector: [0.1, 0.5, -0.3, ..., 0.2] (768 số thực)
     * Input text: "con mèo cute"  
     * Output vector: [0.12, 0.48, -0.28, ..., 0.21] (rất gần với "con mèo")
     * Input text: "xe hơi"
     * Output vector: [0.8, -0.2, 0.5, ..., -0.4] (rất khác "con mèo")
   
   - Tính chất quan trọng (Key properties):
     * Semantic similarity: Nghĩa giống → vectors gần nhau
     * Các text về "động vật" sẽ cluster lại gần nhau
     * Các text về "xe cộ" sẽ ở vùng khác
     * Distance between vectors = độ khác biệt về nghĩa

2. TẠI SAO CẦN EMBEDDINGS? (Why do we need Embeddings?)
   ====================================================
   
   - Vấn đề cơ bản (Core problem):
     * Máy tính chỉ hiểu số, không hiểu nghĩa của chữ
     * "Python programming" và "Python coding" = nghĩa gần giống
     * Nhưng máy tính thấy 2 strings khác nhau hoàn toàn!
   
   - Giải pháp (Solution):
     * Embeddings giúp máy tính "hiểu" semantic meaning
     * Hai câu nghĩa giống → embeddings giống nhau
     * Có thể tính toán độ tương đồng bằng math!
   
   - So sánh cách tìm kiếm (Search comparison):
   
     A. Keyword Search (Cách cũ):
        - Query: "học Python"
        - Chỉ match: documents có chữ "học" VÀ "Python"
        - Bỏ lỡ: "lập trình Python", "Python tutorial", "khóa Python"
        - Problem: Too strict, misses relevant content
     
     B. Semantic Search (Dùng Embeddings):
        - Query: "học Python"
        - Embed query → [0.2, 0.5, ...]
        - Tìm documents có embeddings gần với query embedding
        - Match: "lập trình Python" ✅, "Python tutorial" ✅, "khóa học coding" ✅
        - Smart: Hiểu nghĩa, không chỉ keywords!
   
   - Ứng dụng thực tế (Real-world applications):
     * RAG (Retrieval-Augmented Generation): Tìm context cho AI
     * Recommendation: "Users thích A cũng thích B"
     * Duplicate detection: Tìm câu hỏi trùng lặp
     * Classification: Phân loại theo chủ đề

3. GEMINI TEXT-EMBEDDING-004 MODEL
   =================================
   
   - Thông số kỹ thuật (Technical specs):
     * Model name: "text-embedding-004"
     * Dimensions: 768 (mỗi embedding = 768 số thực)
     * Max input: 2048 tokens (~8000 characters tiếng Anh)
     * Output type: Fixed-size vector [float32 x 768]
     * Pricing: FREE! 🎉 (1,500 requests/day limit)
   
   - Tại sao chọn 768 dimensions?
     * Trade-off: accuracy vs performance
     * 768 dims đủ để capture complex semantic relationships
     * Không quá lớn → fast computation và storage
     * Industry standard (BERT, nhiều models khác cũng dùng 768)
   
   - Quality benchmark:
     * SOTA (State-of-the-art) cho semantic search
     * Multilingual: Support tiếng Việt, English, etc.
     * Trained trên massive text corpus
     * Very good at capturing nuanced meanings

4. CHUNKING STRATEGY (Chiến lược chia nhỏ văn bản)
   ================================================
   
   - Tại sao phải chunk? (Why chunk?)
     * Giới hạn model: Max 2048 tokens per request
     * Long documents: Sách 300 trang = hàng triệu tokens!
     * Cannot embed entire book in one go
   
   - Chunk size: ~500 words (Kích thước mỗi đoạn)
     * Lý do chọn 500 words:
       1. Đủ context: Đoạn văn có ý nghĩa hoàn chỉnh
       2. Not too long: Trong giới hạn model
       3. Not too short: Tránh mất ngữ cảnh
       4. Optimal for search: Balance between precision và recall
   
   - Overlap: 50 words (Phần chồng lấp)
     * Ví dụ:
       Chunk 1: words 1-500
       Chunk 2: words 451-950 (overlap 50 words with chunk 1)
       Chunk 3: words 901-1400
     
     * Tại sao overlap?
       - Tránh mất thông tin ở boundaries (ranh giới chunks)
       - Câu bị cắt giữa 2 chunks vẫn xuất hiện hoàn chỉnh ở 1 chunk
       - Improves recall: Tăng khả năng tìm thấy relevant info
   
   - Visual example (Minh họa):
     ```
     Original text: "... AI is powerful. Machine learning helps AI. Deep learning is advanced..."
     
     Without overlap:
     Chunk 1: "... AI is powerful."
     Chunk 2: "Machine learning helps AI."  ❌ Lost connection!
     
     With overlap:
     Chunk 1: "... AI is powerful. Machine learning helps AI."
     Chunk 2: "Machine learning helps AI. Deep learning is advanced..."  ✅ Context preserved!
     ```

5. COMPLETE WORKFLOW (Quy trình hoàn chỉnh)
   =========================================
   
   Step 1: Upload document
   → PDF/DOCX file
   
   Step 2: Extract text  
   → Raw text string
   
   Step 3: Chunk text (chia nhỏ)
   → List of ~500-word chunks with overlap
   
   Step 4: Embed each chunk (tạo embeddings)
   → List of 768-d vectors
   
   Step 5: Store in Vector DB (lưu vào ChromaDB)
   → Ready for semantic search!
   
   Step 6: Query (khi user hỏi)
   → Embed question → Find similar chunks → Send to AI → Get answer

=============================================================================
"""

from google import genai
from google.genai import types
import os
from typing import List, Dict, Any
import time
from app.core import settings

class EmbeddingService:
    """
    Service to handle text embeddings using Gemini
    """
    
    def __init__(self):
        """
        Initialize Gemini client for embeddings
        
        LEARNING: Gemini SDK cung cấp riêng embedding API
        Không cần gọi generate_content, dùng embed_content()
        """
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize client
        self.client = genai.Client(api_key=api_key)
        
        # Model name cho embedding
        # LEARNING: text-embedding-004 là latest và best cho semantic search
        self.model = "models/text-embedding-004"
        
        print(f"✅ Embedding service initialized with model: {self.model}")
    
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Chia văn bản thành các chunks có overlap (Split text into overlapping chunks)
        
        =============================================================================
        LEARNING - CHIẾN LƯỢC CHUNKING (CHUNKING STRATEGY)
        =============================================================================
        
        Parameters giải thích (Parameters explained):
        --------------------------------------------
        - chunk_size: Số WORDS (từ) per chunk, KHÔNG phải characters!
          * Default: 500 words ≈ 2-3 paragraphs
          * Đủ context để câu có nghĩa hoàn chỉnh
          * Không quá dài → vẫn trong giới hạn embedding model
        
        - overlap: Số words CHỒNG LẤP giữa các chunks
          * Default: 50 words ≈ 2-3 sentences
          * Ensures continuity between chunks
          * Prevents information loss at boundaries
        
        Tại sao phải chunk? (Why chunking is necessary?)
        -----------------------------------------------
        1. Technical limit: Gemini max 2048 tokens (~8000 chars)
        2. Precision: Smaller chunks = more accurate retrieval
        3. Performance: Faster embedding và search
        4. Context: Mỗi chunk độc lập nhưng vẫn có nghĩa
        
        Tại sao cần overlap? (Why overlapping chunks?)
        ----------------------------------------------
        Problem without overlap:
          Chunk 1: "...AI is powerful."
          Chunk 2: "Deep learning helps AI."
          → Connection between "powerful" và "deep learning" bị mất!
        
        Solution with overlap:
          Chunk 1: "...AI is powerful. Deep learning helps AI."
          Chunk 2: "Deep learning helps AI. It uses neural networks."
          → Context preserved! ✅
        
        Visual Example (Ví dụ trực quan):
        ---------------------------------
        Với chunk_size=3, overlap=1:
        
        Text: "The quick brown fox jumps over lazy dog"
        Words: [The, quick, brown, fox, jumps, over, lazy, dog]
                 0    1      2     3     4     5     6     7
        
        Chunks created:
        1. words[0:3]  → "The quick brown"
        2. words[2:5]  → "brown fox jumps"     <- "brown" overlaps với chunk 1
        3. words[4:7]  → "jumps over lazy"     <- "jumps" overlaps với chunk 2
        4. words[6:8]  → "lazy dog"            <- "lazy" overlaps với chunk 3
        
        Real-world example (Ví dụ thực tế):
        ----------------------------------
        Document: 5000 words
        chunk_size=500, overlap=50
        
        Step calculation:
        - step = chunk_size - overlap = 500 - 50 = 450 words
        - Mỗi iteration nhảy 450 words (not 500!)
        
        Chunks:
        - Chunk 1: words 0-500     (500 words)
        - Chunk 2: words 450-950   (500 words, overlap 50 with chunk 1)
        - Chunk 3: words 900-1400  (500 words, overlap 50 with chunk 2)
        - ...
        - Total chunks: ~11 chunks
        
        Math behind:
        -----------
        - No overlap: 5000 / 500 = 10 chunks
        - With overlap: 5000 / (500-50) ≈ 11 chunks
        - Trade-off: Thêm 10% storage cho better accuracy
        
        Args:
            text: Full document text cần chia nhỏ
            chunk_size: Target số words per chunk (mặc định 500)
            overlap: Số words chồng lấp between chunks (mặc định 50)
            
        Returns:
            List of text chunks (strings), mỗi chunk ~chunk_size words
        """
        # Split text into words
        words = text.split()
        chunks = []
        
        # Calculate step size (how many words to advance each time)
        step = chunk_size - overlap
        
        # LEARNING: range(start, stop, step)
        # Ví dụ: range(0, 100, 50) → [0, 50]
        for i in range(0, len(words), step):
            # Get chunk of words
            chunk_words = words[i:i + chunk_size]
            
            # Join back into string
            chunk = ' '.join(chunk_words)
            
            # Only add if chunk has meaningful content
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        
        print(f"📄 Split text into {len(chunks)} chunks")
        return chunks
    
    
    def embed_text(self, text: str) -> List[float]:
        """
        Chuyển đổi text thành embedding vector (Convert text to embedding vector)
        
        =============================================================================
        LEARNING - CÁCH EMBEDDING HOẠT ĐỘNG (HOW EMBEDDING WORKS)
        =============================================================================
        
        Quy trình xử lý (Processing pipeline):
        --------------------------------------
        Input text: "con mèo màu trắng"
        
        Step 1 - Tokenization (Tách từ):
          * Gemini chia text thành tokens (sub-word units)
          * Example: "con mèo" → ["con", "mèo"] hoặc ["con", " m", "èo"]
          * Tại sao sub-words? Handle unknown words tốt hơn
        
        Step 2 - Neural Network Processing:
          * Tokens đi qua multiple layers của transformer model
          * Mỗi layer học features khác nhau:
            - Layer đầu: syntax, grammar patterns
            - Layer giữa: semantic relationships
            - Layer cuối: high-level concepts
        
        Step 3 - Output Layer (768 neurons):
          * Final layer có 768 neurons
          * Mỗi neuron output = 1 số thực (float)
          * Kết quả: [0.123, -0.456, 0.789, ..., 0.234]
        
        Output: 768-dimensional vector (768 số thực)
        
        Tại sao 768 dimensions? (Why 768?)
        ----------------------------------
        - Đủ để encode complex semantic information
        - Not too large → efficient storage & computation
        - Industry standard (BERT, many models use 768)
        - Each dimension captures một aspect của meaning
        
        Visual representation (Hình dung):
        ---------------------------------
        Imagine 768-dimensional space (không gian 768 chiều):
        
        "con mèo"     → Point A: [0.1, 0.5, -0.3, ..., 0.2]
        "con chó"     → Point B: [0.12, 0.48, -0.28, ..., 0.19]  (gần A)
        "ô tô"        → Point C: [0.8, -0.2, 0.5, ..., -0.4]     (xa A & B)
        "xe hơi"      → Point D: [0.79, -0.19, 0.51, ..., -0.39] (gần C)
        
        Distance in space = semantic difference (khác biệt nghĩa)
        
        The magic behind similarity (Phép màu của similarity):
        ------------------------------------------------------
        1. Cosine Similarity formula:
           similarity = (A · B) / (||A|| × ||B||)
           
        2. Range: -1 to 1
           * 1.0 = hoàn toàn giống nhau (identical meaning)
           * 0.8-0.9 = rất giống (very similar)
           * 0.5-0.7 = có liên quan (related)
           * 0.0 = không liên quan (unrelated)
           * -1.0 = trái ngược (opposite)
        
        3. Example scores:
           * "học Python" vs "học lập trình Python": 0.92 ✅
           * "học Python" vs "Python tutorial": 0.85 ✅
           * "học Python" vs "học nấu ăn": 0.12 ❌
        
        Real-world example (Ví dụ thực tế):
        ----------------------------------
        Scenario: User asks "Cách cài đặt Python?"
        
        1. Embed question:
           → [0.234, -0.567, 0.123, ..., 0.890]
        
        2. Embed all document chunks:
           Chunk 1: "How to install Python on Windows"
           → [0.240, -0.560, 0.130, ..., 0.885]  (score: 0.95) ✅
           
           Chunk 2: "Python list comprehension tutorial"
           → [0.100, 0.200, -0.300, ..., 0.400]  (score: 0.45) ❌
           
           Chunk 3: "Installing Python: A beginner's guide"
           → [0.238, -0.565, 0.125, ..., 0.888]  (score: 0.93) ✅
        
        3. Return top-k highest scored chunks
        
        Why embeddings beat keywords (Tại sao tốt hơn từ khóa):
        -------------------------------------------------------
        Keyword search:
          Query: "cài đặt Python"
          Misses: "install Python", "Python setup", "getting started Python"
        
        Embedding search:
          Query: "cài đặt Python" 
          Finds: ALL above! Because semantic meaning is captured.
        
        Args:
            text: Text cần chuyển thành embedding (có thể là câu, đoạn, chunk)
            
        Returns:
            768-dimensional vector (list of 768 floats)
            Example: [0.123, -0.456, ..., 0.789]
        """
        try:
            # Call Gemini embedding API
            # LEARNING: embed_content() is specifically for embeddings
            # NOTE: API updated - use 'contents' instead of 'content'
            response = self.client.models.embed_content(
                model=self.model,
                contents=text  # Changed from 'content' to 'contents'
            )
            
            # Extract embedding vector
            # LEARNING: Response structure từ Gemini
            embedding = response.embeddings[0].values
            
            # Verify dimensions
            if len(embedding) != 768:
                raise ValueError(f"Expected 768 dimensions, got {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            print(f"❌ Embedding error: {str(e)}")
            raise
    
    
    def embed_chunks(self, chunks: List[str], batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Embed multiple text chunks with rate limiting
        
        LEARNING - BATCH PROCESSING:
        ============================
        Tại sao batch?
        - API có rate limits (requests per minute)
        - Batch = group nhiều chunks, process together
        - Efficient hơn là call API từng chunk
        
        Rate limiting:
        - Free tier: 60 requests/minute
        - Batch 5 chunks = safer, avoid hitting limits
        - Sleep between batches để respect limits
        
        Args:
            chunks: List of text chunks to embed
            batch_size: Number of chunks per batch
            
        Returns:
            List of dicts with:
                - chunk_index: Position in original list
                - text: The chunk text
                - embedding: 768d vector
                - metadata: Additional info (length, etc.)
        """
        results = []
        
        print(f"🔄 Starting to embed {len(chunks)} chunks...")
        
        # Process in batches
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            
            print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)")
            
            # Embed each chunk in batch
            for j, chunk in enumerate(batch):
                chunk_index = i + j
                
                try:
                    # Get embedding
                    embedding = self.embed_text(chunk)
                    
                    # Store result with metadata
                    results.append({
                        "chunk_index": chunk_index,
                        "text": chunk,
                        "embedding": embedding,
                        "metadata": {
                            "length": len(chunk),
                            "words": len(chunk.split()),
                        }
                    })
                    
                    print(f"  ✓ Embedded chunk {chunk_index + 1}")
                    
                except Exception as e:
                    print(f"  ✗ Failed chunk {chunk_index + 1}: {str(e)}")
                    continue
            
            # Rate limiting: wait between batches
            # LEARNING: Avoid hitting API rate limits
            if i + batch_size < len(chunks):
                wait_time = 2  # seconds
                print(f"⏳ Waiting {wait_time}s before next batch...")
                time.sleep(wait_time)
        
        print(f"✅ Successfully embedded {len(results)}/{len(chunks)} chunks")
        return results
    
    
    def process_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Complete pipeline: chunk text → embed all chunks
        
        LEARNING - FULL PIPELINE:
        ========================
        This is the main function you'll call for a document
        
        Steps:
        1. Receive full document text
        2. Split into manageable chunks
        3. Embed each chunk
        4. Return all embeddings with metadata
        
        Usage:
            text = "Your long document text here..."
            results = service.process_document(text)
            # Now save results to vector database (ChromaDB)
        
        Args:
            text: Full document text
            
        Returns:
            List of embeddings with text and metadata
        """
        print("\n" + "="*60)
        print("📚 DOCUMENT EMBEDDING PIPELINE")
        print("="*60)
        
        # Step 1: Chunk
        print("\n📄 Step 1: Chunking document...")
        chunks = self.chunk_text(text, chunk_size=500, overlap=50)
        
        # Step 2: Embed
        print(f"\n🎯 Step 2: Embedding {len(chunks)} chunks...")
        embeddings = self.embed_chunks(chunks, batch_size=5)
        
        print("\n" + "="*60)
        print(f"✅ COMPLETE! Processed {len(embeddings)} embeddings")
        print("="*60 + "\n")
        
        return embeddings


# LEARNING - HOW TO USE THIS SERVICE:
# ===================================
"""
Example usage:

# 1. Initialize service
service = EmbeddingService()

# 2. Your document text
document_text = '''
Your long PDF or DOCX content here.
This could be many pages of text.
The service will automatically chunk and embed it.
'''

# 3. Process document
embeddings = service.process_document(document_text)

# 4. Each embedding looks like:
# {
#     "chunk_index": 0,
#     "text": "Your first chunk of text here...",
#     "embedding": [0.1, 0.2, ..., 0.8],  # 768 numbers
#     "metadata": {
#         "length": 2543,
#         "words": 450
#     }
# }

# 5. Next step: Save to ChromaDB for vector search!
"""
