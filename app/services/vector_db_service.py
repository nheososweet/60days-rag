"""
Vector Database Service using ChromaDB
Dịch vụ Vector Database sử dụng ChromaDB để lưu trữ và tìm kiếm embeddings

=============================================================================
                    LEARNING NOTES - HỌC VỀ VECTOR DATABASE
=============================================================================

1. VECTOR DATABASE LÀ GÌ? (What is a Vector Database?)
   =====================================================
   
   Định nghĩa (Definition):
   - Vector Database = Database chuyên biệt để lưu và tìm kiếm vectors (embeddings)
   - Khác với SQL Database: SQL search theo exact match (tìm chính xác)
   - Vector DB: Search theo "similarity" (độ tương đồng/giống nhau)
   
   Tại sao cần? (Why needed?):
   - SQL: "SELECT * WHERE name = 'Python'" → chỉ tìm chữ "Python"
   - Vector DB: Query "học Python" → tìm "Python tutorial", "lập trình Python", "Python course"
   - Hiểu nghĩa thay vì chỉ match chữ!
   
   Use cases (Ứng dụng):
   - RAG (Retrieval-Augmented Generation): Tìm context cho AI
   - Semantic Search: Tìm kiếm theo nghĩa
   - Recommendation Systems: "Users thích A cũng thích B"
   - Duplicate Detection: Tìm nội dung trùng lặp
   - Image/Video Search: Tìm ảnh tương tự

2. CHROMADB - VECTOR DATABASE LIBRARY
   ====================================
   
   Đặc điểm (Features):
   - Open-source: Miễn phí, code mở
   - Runs locally: Chạy trên máy bạn, không cần server riêng
   - Easy to use: API đơn giản, dễ học
   - Perfect for prototyping: Tuyệt vời để học và thử nghiệm
   - Production-ready: Có thể scale lên production sau
   
   So sánh với alternatives:
   - Pinecone: Cloud-based, phải trả tiền
   - Weaviate: Phức tạp hơn, cần setup server
   - Milvus: Enterprise-grade, phức tạp
   - ChromaDB: Đơn giản nhất để bắt đầu! ✅
   
   Cài đặt (Installation):
   ```bash
   pip install chromadb
   ```

3. SIMILARITY SEARCH - TÌM KIẾM THEO ĐỘ TƯƠNG ĐỒNG
   ================================================
   
   Cách hoạt động (How it works):
   
   Bước 1: User hỏi câu hỏi
   - Query: "tôi muốn học Python"
   
   Bước 2: Embed query thành vector
   - "tôi muốn học Python" → [0.2, 0.5, -0.3, ..., 0.8] (768 số)
   
   Bước 3: ChromaDB so sánh với ALL stored vectors
   - Vector DB có sẵn 1000 chunks
   - Compare query vector với 1000 vectors
   - Tính cosine similarity (độ giống nhau)
   
   Bước 4: Trả về top-k most similar chunks
   - Chunk 1: "Python tutorial for beginners" (similarity: 0.92)
   - Chunk 2: "How to learn Python programming" (similarity: 0.89)
   - Chunk 3: "Python course online" (similarity: 0.85)
   
   Cosine Similarity - Độ đo tương đồng:
   -------------------------------------
   - Formula: similarity = cos(angle between vectors)
   - Range: -1 đến 1
   - 1 = hoàn toàn giống nhau (identical meaning)
   - 0.8-0.9 = rất giống (very similar)
   - 0.5-0.7 = có liên quan (related)
   - 0 = không liên quan (unrelated)
   - -1 = trái ngược (opposite meaning)
   
   Tại sao không dùng exact text match?
   -------------------------------------
   - Exact match: "học Python" chỉ match "học Python"
   - Bỏ lỡ: "lập trình Python", "Python tutorial", "học code"
   - Similarity search: Tìm theo NGHĨA, không chỉ từ khóa!
   - Kết quả: Tìm được nhiều tài liệu liên quan hơn

4. HOW VECTOR DB WORKS - CÁCH HOẠT ĐỘNG
   ======================================
   
   A. STORING DATA (Lưu trữ dữ liệu):
   -----------------------------------
   Input: Document chunks + embeddings
   
   Step 1: Prepare data
   - Text chunk: "Python is a programming language"
   - Embedding: [0.1, 0.5, -0.3, ..., 0.2] (768 floats)
   - Metadata: {"document_id": "doc_123", "chunk_index": 0}
   
   Step 2: Add to ChromaDB
   - collection.add(ids, embeddings, documents, metadatas)
   - ChromaDB tạo index để search nhanh
   - Data saved to disk (persist)
   
   Step 3: Ready for search!
   - Vectors indexed bằng HNSW algorithm
   - Search speed: O(log n) thay vì O(n)
   
   B. SEARCHING DATA (Tìm kiếm):
   ------------------------------
   Input: User question
   
   Step 1: Embed question
   - Question: "Cách cài đặt Python?"
   - Embedding: [0.15, 0.48, -0.25, ..., 0.18]
   
   Step 2: Find similar vectors
   - ChromaDB.query(question_embedding)
   - Compare với all stored vectors
   - Use cosine similarity
   
   Step 3: Return top matches
   - Top 5 most similar chunks
   - Include text + metadata + similarity score
   
   Step 4: Use in RAG
   - Send chunks to AI as context
   - AI generates answer based on context

5. COMPLETE WORKFLOW EXAMPLE
   ==========================
   
   Scenario: Bạn có 3 PDFs về Python programming
   
   Step 1: Upload & Process
   ```
   PDF 1: "Python Basics" → 10 chunks → 10 embeddings
   PDF 2: "Advanced Python" → 15 chunks → 15 embeddings  
   PDF 3: "Python Projects" → 8 chunks → 8 embeddings
   Total: 33 chunks trong ChromaDB
   ```
   
   Step 2: User hỏi
   ```
   Question: "Làm sao để học Python cho người mới bắt đầu?"
   ```
   
   Step 3: Search
   ```
   - Embed question → vector
   - Search trong 33 chunks
   - Find top 5 similar:
     1. "Python basics for beginners" (from PDF 1)
     2. "Getting started with Python" (from PDF 1)
     3. "Python tutorial introduction" (from PDF 1)
     4. "How to start learning Python" (from PDF 2)
     5. "Python beginner projects" (from PDF 3)
   ```
   
   Step 4: Build Context
   ```
   Context = Combine 5 chunks into one text
   Send to AI: "Based on this context, answer: [question]"
   AI generates answer using the retrieved information
   ```
   
   Kết quả (Result):
   - User gets accurate answer từ documents
   - AI không "hallucinate" (bịa đặt)
   - Có source citations (trích dẫn nguồn)

=============================================================================
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import os
import uuid


class VectorDBService:
    """
    Service for managing vector storage and retrieval with ChromaDB
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Khởi tạo ChromaDB client (Initialize ChromaDB client)
        
        =============================================================================
        LEARNING - CHROMADB SETUP (THIẾT LẬP CHROMADB)
        =============================================================================
        
        persist_directory - Thư mục lưu trữ dữ liệu:
        --------------------------------------------
        - Path: Where ChromaDB saves data on disk (Nơi ChromaDB lưu data lên đĩa)
        - Default: "./chroma_db" (thư mục trong project)
        
        Tại sao cần persist_directory?
        - Nếu KHÔNG specify: Data chỉ lưu trong RAM
        - Khi restart program → Data mất hết! ❌
        - With persist_directory: Data save to disk permanently ✅
        - Restart program → Data vẫn còn!
        
        Collections - Giống như "tables" trong SQL:
        ------------------------------------------
        - Mỗi collection = một nhóm documents
        - Example:
          * Collection "products": Lưu product descriptions
          * Collection "articles": Lưu blog articles
          * Collection "documents": Lưu uploaded PDFs/DOCXs
        
        - Có thể có nhiều collections trong 1 database
        - Mỗi collection có settings riêng (distance metric, etc.)
        
        PersistentClient vs Client:
        --------------------------
        - PersistentClient: Lưu data to disk (dùng cho production)
        - Client: Chỉ lưu trong memory (dùng cho testing)
        - Chúng ta dùng PersistentClient để data không mất!
        
        Args:
            persist_directory: Path đến thư mục lưu ChromaDB data
                              Mặc định: "./chroma_db"
        
        Creates:
            - Thư mục chroma_db/ nếu chưa tồn tại
            - File chroma.sqlite3 (metadata database)
            - UUID folders chứa vector data
        """
        self.persist_directory = persist_directory
        
        # Create directory if not exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        # LEARNING: PersistentClient saves data to disk
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        
        # Default collection name
        self.collection_name = "documents"
        
        print(f"✅ Vector DB initialized at: {persist_directory}")
    
    
    def get_or_create_collection(self, name: str = None) -> chromadb.Collection:
        """
        Lấy collection đã có hoặc tạo mới (Get existing collection or create new one)
        
        =============================================================================
        LEARNING - COLLECTIONS (BỘ SƯU TẬP)
        =============================================================================
        
        Collection là gì? (What is a Collection?)
        -----------------------------------------
        - Collection = container (thùng chứa) for embeddings
        - Giống như "table" trong SQL database
        - Mỗi collection có name riêng: "documents", "products", etc.
        - Mỗi collection có settings riêng (distance metric, index type)
        
        Metadata của Collection:
        -----------------------
        Khi tạo collection, chúng ta config:
        
        1. Distance Metric (Cách đo khoảng cách):
           - "cosine": Most common cho text (đo góc giữa vectors)
           - "l2": Euclidean distance (khoảng cách thẳng)
           - "ip": Inner product (tích vô hướng)
        
        2. HNSW (Hierarchical Navigable Small World):
           - Algorithm để search nhanh
           - Thay vì check ALL vectors → chỉ check một phần
           - Speed: O(log n) instead of O(n)
           - Trade-off: Speed vs Accuracy
        
        Distance Metrics Chi Tiết:
        --------------------------
        
        A. COSINE SIMILARITY (Chúng ta dùng cái này):
           - Measures: Góc giữa 2 vectors
           - Range: -1 to 1
           - Use case: Text similarity (nghĩa giống nhau)
           - Example:
             * "Python programming" vs "Python coding" → 0.95 (gần)
             * "Python" vs "Java" → 0.5 (có liên quan)
             * "Python" vs "banana" → 0.1 (không liên quan)
           
           - Tại sao tốt cho text?
             * Không bị ảnh hưởng bởi length (độ dài)
             * "Python" và "Python programming language" → vẫn similar
             * Focus on direction (hướng), not magnitude (độ lớn)
        
        B. L2 (EUCLIDEAN DISTANCE):
           - Measures: Khoảng cách thẳng giữa 2 điểm
           - Range: 0 to ∞
           - Use case: Image embeddings, spatial data
           - Problem với text: Bị ảnh hưởng bởi vector length
        
        C. IP (INNER PRODUCT):
           - Measures: Dot product của 2 vectors
           - Range: -∞ to ∞
           - Use case: Recommendation systems
           - Fast nhưng less intuitive cho text
        
        Try-Except Pattern:
        ------------------
        ```python
        try:
            collection = self.client.get_collection(name)  # Thử lấy
            # Nếu collection đã tồn tại → success!
        except:
            collection = self.client.create_collection(name)  # Không có → tạo mới
        ```
        
        - Tại sao dùng pattern này?
          * Avoid duplicate collections (tránh tạo trùng)
          * Safe: Không crash nếu collection đã tồn tại
          * Idempotent: Gọi nhiều lần cũng OK
        
        Args:
            name: Tên collection (default: "documents")
                  String identifier, unique trong database
            
        Returns:
            chromadb.Collection object để thực hiện operations:
            - collection.add(): Thêm embeddings
            - collection.query(): Tìm kiếm
            - collection.get(): Lấy data
            - collection.delete(): Xóa
            - collection.count(): Đếm số lượng
        """
        if name is None:
            name = self.collection_name
        
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=name)
            print(f"📚 Retrieved existing collection: {name}")
            
        except:
            # Create new collection if doesn't exist
            # LEARNING: metadata configures behavior
            collection = self.client.create_collection(
                name=name,
                metadata={
                    "hnsw:space": "cosine"  # Use cosine similarity
                }
            )
            print(f"📚 Created new collection: {name}")
        
        return collection
    
    
    def add_document(
        self,
        document_id: str,
        embeddings_data: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Thêm document embeddings vào vector database (Add document embeddings to vector database)
        
        =============================================================================
        LEARNING - STORING EMBEDDINGS (LƯU TRỮ EMBEDDINGS)
        =============================================================================
        
        ChromaDB lưu 4 thứ cho mỗi entry:
        ---------------------------------
        1. ID (Định danh duy nhất):
           - Format: "doc_123::chunk_0", "doc_123::chunk_1"
           - Mỗi chunk có ID riêng
           - Dùng để retrieve/delete specific chunks sau này
        
        2. Embedding (Vector 768 chiều):
           - Array of 768 floats: [0.123, -0.456, ..., 0.789]
           - Đây là "bản chất" của text dưới dạng số
           - ChromaDB dùng vector này để tính similarity
        
        3. Document (Text thực tế):
           - Original text của chunk
           - Ví dụ: "Python is a programming language..."
           - Để return cho user khi search
        
        4. Metadata (Thông tin bổ sung):
           - document_id: ID của document gốc
           - chunk_index: Vị trí chunk (0, 1, 2, ...)
           - filename: Tên file gốc
           - words: Số từ trong chunk
           - length: Số ký tự
           - Custom fields: Bất kỳ info nào bạn muốn
        
        Tại sao cần ID riêng cho mỗi chunk?
        ------------------------------------
        Problem: 1 document → nhiều chunks
        - Document: "report.pdf" có 50 pages
        - After chunking: 100 chunks
        
        Solution: Unique ID format
        - Chunk 1: "doc_123::chunk_0"
        - Chunk 2: "doc_123::chunk_1"
        - ...
        - Chunk 100: "doc_123::chunk_99"
        
        Benefits:
        - Can delete all chunks of 1 document: Filter by "doc_123"
        - Can get specific chunk: Get by "doc_123::chunk_5"
        - Track source: Know which document a chunk came from
        - Order preserved: chunk_index maintains sequence
        
        Data Structure Example:
        ----------------------
        embeddings_data = [
            {
                "chunk_index": 0,
                "text": "Python is a programming language...",
                "embedding": [0.1, 0.5, -0.3, ..., 0.2],  # 768 floats
                "metadata": {
                    "length": 3000,
                    "words": 500
                }
            },
            {
                "chunk_index": 1,
                "text": "Python supports multiple paradigms...",
                "embedding": [0.15, 0.48, -0.25, ..., 0.18],
                "metadata": {
                    "length": 2950,
                    "words": 495
                }
            }
        ]
        
        Metadata Merging:
        ----------------
        - Chunk-level metadata: length, words, chunk_index
        - Document-level metadata: filename, upload_time, file_path
        - Combined: chunk_metadata.update(document_metadata)
        - Result: Mỗi chunk có BOTH types of metadata
        
        Why?
        - Search by document: where={"filename": "report.pdf"}
        - Filter by chunk size: where={"words": {"$gte": 400}}
        - Flexible querying!
        
        Args:
            document_id: Unique ID cho document (UUID string)
                        Ví dụ: "550e8400-e29b-41d4-a716-446655440000"
            
            embeddings_data: List of dicts từ EmbeddingService.process_document()
                            Mỗi dict chứa: text, embedding, chunk_index, metadata
            
            metadata: Optional document-level metadata (dict)
                     Ví dụ: {"filename": "report.pdf", "upload_time": "2024-01-01"}
                     Sẽ được add vào ALL chunks của document
            
        Returns:
            Dict với stats về chunks đã lưu:
            {
                "document_id": "doc_123",
                "chunks_stored": 100,
                "collection": "documents"
            }
        
        Process Flow:
        ------------
        1. Prepare 4 lists: ids, embeddings, documents, metadatas
        2. Loop through embeddings_data
        3. For each chunk:
           - Generate unique ID
           - Extract embedding vector
           - Extract text
           - Merge metadata
           - Append to lists
        4. Call collection.add() with all 4 lists
        5. ChromaDB indexes và stores data
        6. Return success stats
        """
        collection = self.get_or_create_collection()
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        print(f"\n💾 Storing {len(embeddings_data)} embeddings for document: {document_id}")
        
        for item in embeddings_data:
            # Create unique ID for each chunk
            # LEARNING: Format = "doc_id::chunk_0", "doc_id::chunk_1", etc.
            chunk_id = f"{document_id}::chunk_{item['chunk_index']}"
            ids.append(chunk_id)
            
            # Extract embedding vector
            embeddings.append(item['embedding'])
            
            # Extract text
            documents.append(item['text'])
            
            # Combine metadata
            chunk_metadata = {
                "document_id": document_id,
                "chunk_index": item['chunk_index'],
                "length": item['metadata']['length'],
                "words": item['metadata']['words'],
            }
            
            # Add document-level metadata if provided
            if metadata:
                chunk_metadata.update(metadata)
            
            metadatas.append(chunk_metadata)
        
        # Add to ChromaDB
        # LEARNING: add() is the main storage method
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"✅ Successfully stored {len(ids)} chunks in vector DB")
        
        return {
            "document_id": document_id,
            "chunks_stored": len(ids),
            "collection": self.collection_name
        }
    
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Tìm kiếm documents tương tự bằng vector similarity (Search for similar documents)
        
        =============================================================================
        LEARNING - SIMILARITY SEARCH (TÌM KIẾM THEO ĐỘ TƯƠNG ĐỒNG)
        =============================================================================
        
        Cách hoạt động chi tiết (Detailed workflow):
        --------------------------------------------
        
        Step 1: User hỏi câu hỏi
        - Question: "Cách học Python hiệu quả?"
        - Đây là natural language, máy tính chưa hiểu được
        
        Step 2: Embed câu hỏi thành vector
        - Call embedding_service.embed_text(question)
        - Result: [0.234, -0.567, 0.123, ..., 0.890] (768 floats)
        - Giờ máy tính có thể work với nó!
        
        Step 3: ChromaDB so sánh với ALL stored vectors
        - Database có 1000 chunks (1000 vectors)
        - ChromaDB compare query vector với 1000 vectors
        - Tính cosine similarity cho mỗi pair
        - Rank theo similarity scores
        
        Step 4: Trả về top-k most similar chunks
        - n_results = 5 → return 5 chunks giống nhất
        - Include: text + metadata + similarity score
        - Sort by score (highest first)
        
        Cosine Similarity - Công thức đo độ tương đồng:
        -----------------------------------------------
        
        Formula:
        ```
        similarity = (A · B) / (||A|| × ||B||)
        
        Where:
        - A · B = dot product (tích vô hướng)
        - ||A|| = magnitude of A (độ dài vector A)
        - ||B|| = magnitude of B
        ```
        
        Ý nghĩa:
        - Measures: Góc giữa 2 vectors trong không gian 768 chiều
        - Không quan tâm độ dài vector, chỉ quan tâm hướng
        - Vectors cùng hướng = meanings giống nhau
        
        Range và ý nghĩa:
        - 1.0 = Hoàn toàn giống nhau (identical meaning)
        - 0.9-0.99 = Rất rất giống (nearly identical)
        - 0.8-0.89 = Rất giống (very similar)
        - 0.7-0.79 = Giống (similar)
        - 0.5-0.69 = Có liên quan (related)
        - 0.3-0.49 = Hơi liên quan (loosely related)
        - 0.0-0.29 = Ít liên quan (barely related)
        - 0 = Không liên quan (unrelated)
        - -1 = Trái ngược (opposite meaning - rare for text)
        
        Example scores thực tế:
        ----------------------
        Query: "Cách học Python hiệu quả?"
        
        Results:
        1. "How to learn Python effectively" → 0.95 ✅ (Perfect match!)
        2. "Python learning tips for beginners" → 0.88 ✅ (Great match)
        3. "Best ways to study programming" → 0.72 ✅ (Good match)
        4. "Python tutorial for advanced users" → 0.65 ⚠️ (OK match)
        5. "Java programming basics" → 0.35 ❌ (Weak match)
        
        Tại sao không dùng exact text match?
        ------------------------------------
        
        Problem với keyword search:
        - Query: "học Python"
        - Keyword search chỉ match documents có chữ "học" VÀ "Python"
        - Bỏ lỡ:
          * "lập trình Python" (không có chữ "học")
          * "Python tutorial" (tiếng Anh, không có "học")
          * "Python course online" (từ đồng nghĩa)
          * "getting started with Python" (ý nghĩa giống nhưng khác từ)
        
        Solution với embeddings:
        - Query: "học Python" → embedding
        - Matches:
          * "lập trình Python" ✅ (similar meaning)
          * "Python tutorial" ✅ (same concept)
          * "Python course" ✅ (synonymous)
          * "learn programming" ✅ (related concept)
        - Embeddings capture SEMANTIC MEANING, not just keywords!
        
        Metadata Filtering:
        ------------------
        Optional: Filter results by metadata
        
        Example 1: Search trong 1 document specific
        ```python
        results = vector_db.search(
            query_embedding=embedding,
            n_results=5,
            filter_metadata={"document_id": "doc_123"}
        )
        # Chỉ search trong chunks của doc_123
        ```
        
        Example 2: Filter by filename
        ```python
        filter_metadata={"filename": "python_guide.pdf"}
        # Chỉ search trong chunks từ file này
        ```
        
        Example 3: Filter by chunk size
        ```python
        filter_metadata={"words": {"$gte": 400}}
        # Chỉ lấy chunks có >= 400 words
        ```
        
        Args:
            query_embedding: 768d vector của user's question
                           List of 768 floats
                           Ví dụ: [0.234, -0.567, ..., 0.890]
            
            n_results: Số lượng similar chunks muốn return
                      Default: 5 (top 5 matches)
                      Increase nếu cần more context
            
            filter_metadata: Optional dict để filter results
                           Ví dụ: {"document_id": "doc_123"}
                           None = search ALL chunks
            
        Returns:
            Dict với structure:
            {
                "results": [
                    {
                        "id": "doc_123::chunk_0",
                        "text": "Full chunk text...",
                        "metadata": {...},
                        "distance": 0.15  # Lower = more similar
                    },
                    ...
                ],
                "count": 5
            }
            
        Note: distance vs similarity
        - ChromaDB returns "distance" (khoảng cách)
        - Lower distance = more similar
        - Distance ≈ 0.0 = very similar
        - Distance > 1.0 = not similar
        - Similarity = 1 - distance (approximately)
        """
        collection = self.get_or_create_collection()
        
        print(f"\n🔍 Searching for {n_results} similar chunks...")
        
        # Search in ChromaDB
        # LEARNING: query() finds most similar vectors
        results = collection.query(
            query_embeddings=[query_embedding],  # Must be list of lists
            n_results=n_results,
            where=filter_metadata  # Optional filter
        )
        
        # Parse results
        # LEARNING: ChromaDB returns lists for batch queries
        # We only query 1 embedding, so take [0] index
        matched_docs = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                matched_docs.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        print(f"✅ Found {len(matched_docs)} matching chunks")
        
        # Log top result for debugging
        if matched_docs:
            top_match = matched_docs[0]
            print(f"   Top match (distance: {top_match['distance']:.4f}):")
            print(f"   {top_match['text'][:100]}...")
        
        return {
            "results": matched_docs,
            "count": len(matched_docs)
        }
    
    
    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Xóa tất cả chunks của một document (Delete all chunks of a document)
        
        =============================================================================
        LEARNING - DELETION (XÓA DỮ LIỆU)
        =============================================================================
        
        Use case - Khi nào cần xóa?
        ---------------------------
        1. User deletes uploaded PDF từ UI
        2. Document outdated, cần upload version mới
        3. Cleanup: Remove old/unused documents
        4. Privacy: User requests data deletion
        
        Problem: 1 document = nhiều chunks
        ----------------------------------
        - Document "report.pdf" → 50 chunks
        - Chunk IDs: "doc_123::chunk_0" đến "doc_123::chunk_49"
        - Cần xóa ALL 50 chunks, không phải chỉ 1!
        
        Solution: Metadata filtering
        ----------------------------
        Step 1: Find all chunks của document
        - Query ChromaDB với filter: {"document_id": "doc_123"}
        - ChromaDB returns list of matching chunk IDs
        
        Step 2: Delete by IDs
        - collection.delete(ids=[list_of_ids])
        - All chunks removed in one operation
        
        Step 3: Verify và return stats
        - Count số chunks deleted
        - Return success status
        
        Metadata Query Syntax:
        ---------------------
        ChromaDB supports MongoDB-style queries:
        
        Exact match:
        ```python
        where={"document_id": "doc_123"}
        # Find chunks where document_id == "doc_123"
        ```
        
        Multiple conditions:
        ```python
        where={
            "document_id": "doc_123",
            "chunk_index": {"$gte": 10}
        }
        # Find chunks where document_id == "doc_123" AND chunk_index >= 10
        ```
        
        OR conditions:
        ```python
        where={
            "$or": [
                {"document_id": "doc_123"},
                {"document_id": "doc_456"}
            ]
        }
        # Find chunks from either document
        ```
        
        Safety Considerations:
        ---------------------
        1. Deletion is PERMANENT!
           - Cannot undo after delete
           - Data gone from ChromaDB
           - Consider "soft delete" for production
        
        2. Cascading deletes:
           - Delete document from vector DB
           - Should also delete file from disk?
           - Currently: File kept, only embeddings deleted
           - Can re-embed if needed
        
        3. Error handling:
           - Document not found → return error
           - Partial delete failures → rollback?
           - Log deletion events for audit trail
        
        Alternative: Soft Delete
        -----------------------
        Instead of deleting, mark as "deleted":
        ```python
        # Update metadata
        collection.update(
            ids=chunk_ids,
            metadatas=[{"deleted": True, ...}]
        )
        
        # Search excludes deleted
        where={"deleted": {"$ne": True}}
        ```
        
        Benefits:
        - Can recover if mistake
        - Audit trail preserved
        - Gradual cleanup possible
        
        Args:
            document_id: ID của document cần xóa (string UUID)
                        Ví dụ: "550e8400-e29b-41d4-a716-446655440000"
            
        Returns:
            Dict với deletion status:
            
            Success case:
            {
                "success": True,
                "document_id": "doc_123",
                "chunks_deleted": 50
            }
            
            Not found case:
            {
                "success": False,
                "message": "Document not found"
            }
            
            Error case:
            {
                "success": False,
                "error": "Error message here"
            }
        
        Process Flow:
        ------------
        1. Get collection
        2. Query chunks với where={"document_id": ...}
        3. Check if any chunks found
        4. If yes:
           - Delete by IDs
           - Count deleted
           - Return success
        5. If no:
           - Return not found error
        6. If exception:
           - Catch error
           - Return error message
        """
        collection = self.get_or_create_collection()
        
        print(f"\n🗑️  Deleting document: {document_id}")
        
        try:
            # Find all chunks for this document
            # LEARNING: Use where filter to find by metadata
            results = collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                # Delete by IDs
                collection.delete(ids=results['ids'])
                print(f"✅ Deleted {len(results['ids'])} chunks")
                
                return {
                    "success": True,
                    "document_id": document_id,
                    "chunks_deleted": len(results['ids'])
                }
            else:
                print(f"⚠️  No chunks found for document: {document_id}")
                return {
                    "success": False,
                    "message": "Document not found"
                }
                
        except Exception as e:
            print(f"❌ Delete error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored documents
        
        Returns:
            Dict with collection stats
        """
        collection = self.get_or_create_collection()
        count = collection.count()
        
        return {
            "collection_name": self.collection_name,
            "total_chunks": count,
            "persist_directory": self.persist_directory
        }
    
    
    def list_all_documents(self) -> List[Dict[str, Any]]:
        """
        Lấy danh sách TẤT CẢ documents đã embedding (List all embedded documents)
        
        =============================================================================
        LEARNING - QUẢN LÝ DOCUMENTS TRONG VECTOR DB
        =============================================================================
        
        Cách lưu trữ (Storage structure):
        ---------------------------------
        Mỗi document được chia thành nhiều chunks:
        - doc_123::chunk_0
        - doc_123::chunk_1
        - doc_123::chunk_2
        
        Method này:
        1. Lấy ALL chunks từ ChromaDB
        2. Group theo document_id
        3. Aggregate metadata (filename, upload time, etc.)
        4. Count số chunks per document
        
        Use case: Hiển thị list documents trong UI
        
        Returns:
            List of dicts, mỗi dict = 1 document với:
            - document_id: Unique ID
            - filename: Tên file gốc
            - chunks_count: Số chunks
            - metadata: Thông tin khác (upload time, size, etc.)
        """
        collection = self.get_or_create_collection()
        
        try:
            # Get ALL data from collection
            # LEARNING: get() without filters returns everything
            all_data = collection.get(
                include=["metadatas", "documents"]  # Include metadata và text
            )
            
            if not all_data['ids'] or len(all_data['ids']) == 0:
                print("📚 No documents found in vector DB")
                return []
            
            # Group chunks by document_id
            # LEARNING: Dùng dict để group, key = document_id
            documents_map = {}
            
            for i, chunk_id in enumerate(all_data['ids']):
                metadata = all_data['metadatas'][i]
                document_id = metadata.get('document_id')
                
                if not document_id:
                    continue
                
                # Initialize document entry nếu chưa có
                if document_id not in documents_map:
                    documents_map[document_id] = {
                        "document_id": document_id,
                        "filename": metadata.get('filename', 'Unknown'),
                        "chunks_count": 0,
                        "total_words": 0,
                        "metadata": {}
                    }
                    
                    # Copy metadata (chỉ lưu 1 lần từ chunk đầu tiên)
                    for key, value in metadata.items():
                        if key not in ['document_id', 'chunk_index', 'length', 'words']:
                            documents_map[document_id]["metadata"][key] = value
                
                # Increment counts
                documents_map[document_id]["chunks_count"] += 1
                documents_map[document_id]["total_words"] += metadata.get('words', 0)
            
            # Convert map to list
            documents_list = list(documents_map.values())
            
            print(f"📚 Found {len(documents_list)} documents with {len(all_data['ids'])} total chunks")
            
            return documents_list
            
        except Exception as e:
            print(f"❌ Error listing documents: {str(e)}")
            return []
    
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy chi tiết 1 document cụ thể (Get details of a specific document)
        
        =============================================================================
        LEARNING - RETRIEVE DOCUMENT DETAILS
        =============================================================================
        
        Method này trả về:
        1. Document metadata (filename, upload time, etc.)
        2. List ALL chunks của document
        3. Chunk details (text preview, word count, etc.)
        
        Use case: 
        - User clicks vào 1 document trong UI
        - Hiển thị chi tiết + preview chunks
        - Debug: Xem chunks có đúng không
        
        Args:
            document_id: ID của document cần lấy
        
        Returns:
            Dict với document info + list of chunks, hoặc None nếu không tìm thấy
        """
        collection = self.get_or_create_collection()
        
        try:
            # Query chunks của document này
            # LEARNING: Use where filter để query by metadata
            results = collection.get(
                where={"document_id": document_id},
                include=["metadatas", "documents"]
            )
            
            if not results['ids'] or len(results['ids']) == 0:
                print(f"⚠️  Document not found: {document_id}")
                return None
            
            # Prepare document info
            first_metadata = results['metadatas'][0]
            
            document_info = {
                "document_id": document_id,
                "filename": first_metadata.get('filename', 'Unknown'),
                "chunks_count": len(results['ids']),
                "chunks": []
            }
            
            # Add metadata
            for key, value in first_metadata.items():
                if key not in ['document_id', 'chunk_index', 'length', 'words']:
                    document_info[key] = value
            
            # Add all chunks with details
            for i in range(len(results['ids'])):
                chunk_info = {
                    "chunk_id": results['ids'][i],
                    "chunk_index": results['metadatas'][i].get('chunk_index', i),
                    "text": results['documents'][i],
                    "text_preview": results['documents'][i][:200] + "..." if len(results['documents'][i]) > 200 else results['documents'][i],
                    "words": results['metadatas'][i].get('words', 0),
                    "length": results['metadatas'][i].get('length', 0)
                }
                document_info["chunks"].append(chunk_info)
            
            # Sort chunks by index
            document_info["chunks"].sort(key=lambda x: x['chunk_index'])
            
            print(f"📄 Retrieved document: {document_id} with {len(results['ids'])} chunks")
            
            return document_info
            
        except Exception as e:
            print(f"❌ Error getting document: {str(e)}")
            return None
    
    
    def get_document_chunks(self, document_id: str) -> List[str]:
        """
        Lấy ONLY text content của all chunks (Get only text of all chunks)
        
        =============================================================================
        LEARNING - LIGHTWEIGHT RETRIEVAL
        =============================================================================
        
        Khác với get_document_by_id():
        - Method này CHỈ trả về text, không có metadata
        - Lighter weight → faster
        - Use case: Khi cần full text để process/display
        
        Args:
            document_id: ID của document
        
        Returns:
            List of chunk texts (strings), sorted by chunk_index
        """
        collection = self.get_or_create_collection()
        
        try:
            results = collection.get(
                where={"document_id": document_id},
                include=["metadatas", "documents"]
            )
            
            if not results['ids'] or len(results['ids']) == 0:
                return []
            
            # Create list of (chunk_index, text) tuples
            chunks_with_index = []
            for i in range(len(results['ids'])):
                chunk_index = results['metadatas'][i].get('chunk_index', i)
                text = results['documents'][i]
                chunks_with_index.append((chunk_index, text))
            
            # Sort by chunk_index
            chunks_with_index.sort(key=lambda x: x[0])
            
            # Return only texts
            texts = [text for _, text in chunks_with_index]
            
            return texts
            
        except Exception as e:
            print(f"❌ Error getting chunks: {str(e)}")
            return []


# LEARNING - COMPLETE RAG FLOW:
# =============================
"""
End-to-end example:

# 1. Setup services
from embedding_service import EmbeddingService
from vector_db_service import VectorDBService

embedding_service = EmbeddingService()
vector_db = VectorDBService()

# 2. Process & store document
document_text = "Your PDF content here..."
document_id = "doc_123"

# Embed
embeddings = embedding_service.process_document(document_text)

# Store
vector_db.add_document(
    document_id=document_id,
    embeddings_data=embeddings,
    metadata={"filename": "report.pdf"}
)

# 3. Search (when user asks question)
question = "Summarize the main points"

# Embed question
question_embedding = embedding_service.embed_text(question)

# Find similar chunks
results = vector_db.search(
    query_embedding=question_embedding,
    n_results=3
)

# 4. Send to Gemini with context
context = "\n\n".join([r['text'] for r in results['results']])
prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"

# → Send to Gemini → Get response → Return to user!
"""
