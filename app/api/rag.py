"""
RAG (Retrieval-Augmented Generation) API
API để hỏi đáp dựa trên documents đã upload

=============================================================================
                    LEARNING NOTES - HỌC VỀ RAG
=============================================================================

1. RAG LÀ GÌ? (What is RAG?)
   ==========================
   
   RAG = Retrieval-Augmented Generation
   - Retrieval: Tìm kiếm thông tin liên quan từ documents
   - Augmented: Tăng cường, bổ sung
   - Generation: AI sinh ra câu trả lời
   
   Workflow:
   User question → Search docs → AI reads context → Generate answer
   
   Tại sao cần RAG?
   - AI thuần: Chỉ biết data được train (outdated, không có info riêng bạn)
   - AI + RAG: Có thể answer dựa trên YOUR documents (up-to-date, specific)
   - No hallucination: AI không bịa, vì có context từ docs

2. SO SÁNH: CHAT THUẦN vs RAG
   ===========================
   
   A. Chat Thuần (chat.py, qwen.py):
      - User: "Giyu Tomioka là ai?"
      - AI: "Tôi không có thông tin cụ thể..." (general knowledge only)
      - Không access documents
   
   B. RAG (rag.py - file này):
      - User: "Giyu Tomioka là ai?"
      - System: Search trong docs → Find chunks về Giyu
      - AI: "Theo tài liệu, Giyu Tomioka là..." (based on YOUR docs)
      - Accurate + có source citations

3. RAG WORKFLOW CHI TIẾT
   ======================
   
   Step 1: Embed Question
   - Input: "Cách cài đặt Python?"
   - Process: embedding_service.embed_text(question)
   - Output: [0.234, -0.567, ..., 0.890] (768d vector)
   
   Step 2: Search Similar Chunks
   - Input: question_embedding
   - Process: vector_db.search(embedding, n_results=5)
   - Output: Top 5 most similar chunks
   
   Step 3: Build Context
   - Input: List of chunks
   - Process: Combine chunks với separators
   - Output: Long text với all relevant info
   
   Step 4: Create Prompt
   - Template: "Context: {chunks}\n\nQuestion: {q}\n\nAnswer:"
   - AI sẽ đọc context trước khi trả lời
   
   Step 5: Generate Answer
   - Input: Prompt với context
   - Process: gemini.chat(prompt)
   - Output: Answer based on context
   
   Step 6: Return Response
   - Answer + Sources + Context used
   - User có thể verify từ sources

4. PROMPT ENGINEERING
   ===================
   
   Good prompt structure:
   ```
   Based on the following context from documents, answer the question.
   
   Context:
   [Document chunks here]
   
   Question: [User's question]
   
   Instructions:
   - Answer based ONLY on the context provided
   - If context doesn't have info, say "I don't have information about this"
   - Be specific and cite information
   - Use clear, concise language
   ```
   
   Tại sao structure này tốt?
   - Clear instructions: AI biết phải làm gì
   - Context first: AI đọc context trước
   - Grounding: "based ONLY on context" → no hallucination
   - Fallback: Nếu không biết, thừa nhận thay vì bịa

5. N_RESULTS - SỐ CHUNKS CẦN LẤY
   ==============================
   
   Trade-offs:
   
   Low n_results (1-3):
   - Pros: Fast, focused, less tokens cost
   - Cons: Có thể miss important info
   - Use: Simple questions, specific topics
   
   Medium n_results (5-10):
   - Pros: Balanced, good coverage
   - Cons: More tokens, slightly slower
   - Use: General questions (recommended default)
   
   High n_results (15-20):
   - Pros: Maximum context, comprehensive
   - Cons: Expensive tokens, slower, may confuse AI
   - Use: Complex questions, need full picture
   
   Gemini limits:
   - Max context: 30,720 tokens (~100,000 characters)
   - Each chunk: ~500 words (~3,000 chars)
   - Safe: 10-15 chunks max

=============================================================================
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, AsyncIterator
import time
import json

from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDBService
from app.services.gemini_service import GeminiService

# Create router với prefix và tags
# LEARNING: prefix="/api/rag" → all endpoints start với /api/rag
# tags=["rag"] → group trong API docs (Swagger UI)
router = APIRouter(prefix="/api/rag", tags=["rag"])

# Initialize services
# LEARNING: Reuse services đã có, không tạo mới
# Singleton pattern: One instance shared across requests
embedding_service = EmbeddingService()
vector_db = VectorDBService()
gemini_service = GeminiService()



class RAGQueryRequest(BaseModel):
    """
    Request body cho RAG query endpoint
    
    LEARNING - PYDANTIC MODELS:
    ==========================
    - Automatic validation: FastAPI tự kiểm tra types
    - Documentation: Swagger UI show schema
    - Type hints: IDE autocomplete
    """
    question: str  # Required: User's question (câu hỏi của user)
    n_results: int = 5  # Optional: Số chunks muốn lấy (default: 5)
    document_id: Optional[str] = None  # Optional: Search trong doc cụ thể
    include_context: bool = False  # Optional: Return context used hay không


class RAGQueryResponse(BaseModel):
    """
    Response structure cho RAG query
    
    LEARNING: Clear response structure giúp frontend dễ handle
    """
    success: bool
    question: str
    answer: str
    sources: List[Dict[str, Any]]  # List of chunks used
    context_used: Optional[str]  # Full context (if requested)
    metadata: Dict[str, Any]  # Stats: chunks_count, processing_time, etc.


@router.post("/query")
async def rag_query(request: RAGQueryRequest) -> RAGQueryResponse:
    """
    RAG Query Endpoint - Hỏi đáp dựa trên documents đã upload
    
    =============================================================================
    LEARNING - RAG QUERY IMPLEMENTATION
    =============================================================================
    
    Workflow hoàn chỉnh:
    1. Validate input (FastAPI tự động)
    2. Embed question → vector
    3. Search similar chunks trong vector DB
    4. Build context từ chunks
    5. Create prompt với context
    6. Call Gemini để generate answer
    7. Format và return response
    
    Error handling:
    - No documents: "Please upload documents first"
    - No matches: "No relevant information found"
    - Gemini error: "AI service error"
    
    Args:
        request: RAGQueryRequest object với question, n_results, document_id
    
    Returns:
        RAGQueryResponse với answer, sources, metadata
    
    Example:
        POST /api/rag/query
        {
            "question": "Giyu Tomioka là ai?",
            "n_results": 5,
            "include_context": true
        }
        
        Response:
        {
            "success": true,
            "answer": "Giyu Tomioka là...",
            "sources": [...],
            "metadata": {"chunks_used": 5, "time": 2.5}
        }
    """
    try:
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"🔍 RAG QUERY STARTED")
        print(f"{'='*80}")
        print(f"Question: {request.question}")
        print(f"N_results: {request.n_results}")
        if request.document_id:
            print(f"Filtering by document: {request.document_id}")
        
        # =====================================================================
        # STEP 1: VALIDATE - Kiểm tra có documents trong DB không
        # =====================================================================
        # LEARNING: Check trước khi process để avoid wasted computation
        print(f"\n📊 Step 1: Checking vector database...")
        
        stats = vector_db.get_collection_stats()
        total_chunks = stats.get('total_chunks', 0)
        
        if total_chunks == 0:
            print("⚠️  No documents found in database!")
            raise HTTPException(
                status_code=404,
                detail="No documents found. Please upload and embed documents first."
            )
        
        print(f"✅ Found {total_chunks} chunks in database")
        
        # =====================================================================
        # STEP 2: EMBED QUESTION - Chuyển câu hỏi thành vector
        # =====================================================================
        # LEARNING: Question phải cùng format với document embeddings
        # Cùng model (text-embedding-004), cùng dimensions (768)
        print(f"\n🎯 Step 2: Embedding question...")
        
        question_embedding = embedding_service.embed_text(request.question)
        
        print(f"✅ Question embedded to {len(question_embedding)}d vector")
        print(f"   Sample values: [{question_embedding[0]:.4f}, {question_embedding[1]:.4f}, ...]")
        
        # =====================================================================
        # STEP 3: SEARCH - Tìm chunks tương tự trong vector DB
        # =====================================================================
        # LEARNING: Similarity search là core của RAG
        # ChromaDB compare question_embedding với all stored embeddings
        # Return top-k most similar (lowest distance = highest similarity)
        print(f"\n🔍 Step 3: Searching for similar chunks...")
        
        # Prepare metadata filter nếu có
        filter_metadata = None
        if request.document_id:
            filter_metadata = {"document_id": request.document_id}
            print(f"   Filtering by: {filter_metadata}")
        
        # Search trong vector DB
        search_results = vector_db.search(
            query_embedding=question_embedding,
            n_results=request.n_results,
            filter_metadata=filter_metadata
        )
        
        # Check if any results found
        if search_results['count'] == 0:
            print("⚠️  No relevant chunks found!")
            raise HTTPException(
                status_code=404,
                detail="No relevant information found for your question."
            )
        
        print(f"✅ Found {search_results['count']} relevant chunks")
        
        # Log top matches với similarity scores
        print(f"\n   Top matches:")
        for i, result in enumerate(search_results['results'][:3], 1):
            distance = result.get('distance', 0)
            similarity = 1 - distance  # Convert distance to similarity
            text_preview = result['text'][:100] + "..."
            print(f"   {i}. Similarity: {similarity:.3f} | {text_preview}")
        
        # =====================================================================
        # STEP 4: BUILD CONTEXT - Kết hợp chunks thành context text
        # =====================================================================
        # LEARNING: Context structure affects AI's answer quality
        # Good structure: Clear separators, numbered chunks, source info
        print(f"\n📝 Step 4: Building context from chunks...")
        
        context_parts = []
        sources = []
        
        for i, result in enumerate(search_results['results'], 1):
            # Format: [Source 1] text...
            # LEARNING: Numbering helps AI reference specific sources
            chunk_text = result['text']
            metadata = result.get('metadata', {})
            
            # Add source info
            source_info = f"[Source {i}]"
            if metadata.get('filename'):
                source_info += f" From: {metadata['filename']}"
            if metadata.get('chunk_index') is not None:
                source_info += f" (Chunk {metadata['chunk_index']})"
            
            # Combine: [Source 1] From: file.pdf (Chunk 5)
            # Text content here...
            context_parts.append(f"{source_info}\n{chunk_text}")
            
            # Prepare sources for response
            sources.append({
                "chunk_id": result['id'],
                "text": chunk_text,
                "text_preview": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                "distance": result.get('distance', 0),
                "similarity": 1 - result.get('distance', 0),
                "metadata": metadata
            })
        
        # Join với separator
        # LEARNING: "\n\n---\n\n" creates clear visual separation
        context = "\n\n---\n\n".join(context_parts)
        
        context_length = len(context)
        print(f"✅ Context built: {context_length} characters from {len(context_parts)} chunks")
        
        # =====================================================================
        # STEP 5: CREATE PROMPT - Tạo prompt cho Gemini
        # =====================================================================
        # LEARNING: Prompt engineering is critical for good answers
        # Structure: Instructions → Context → Question → Output format
        print(f"\n💭 Step 5: Creating prompt for Gemini...")
        
        prompt = f"""You are a helpful AI assistant. Answer the question based ONLY on the context provided below.

CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {request.question}

INSTRUCTIONS:
- Answer in the same language as the question (Vietnamese or English)
- Base your answer ONLY on the information in the context above
- If the context doesn't contain relevant information, say "I don't have enough information to answer this question based on the provided documents."
- Use clear and concise language
- If multiple sources say the same thing, mention that for credibility

ANSWER:"""
        
        prompt_length = len(prompt)
        print(f"✅ Prompt created: {prompt_length} characters")
        print(f"   Context: {context_length} chars | Question: {len(request.question)} chars")
        
        # =====================================================================
        # STEP 6: GENERATE ANSWER - Call Gemini API
        # =====================================================================
        # LEARNING: This is where AI magic happens
        # Gemini reads context + question → generates grounded answer
        print(f"\n🤖 Step 6: Calling Gemini to generate answer...")
        
        try:
            # Call Gemini service
            # LEARNING: gemini_service.generate_response() handles API call, retries, errors
            result = await gemini_service.generate_response(
                message=prompt,
                temperature=0.7  # Lower temperature for factual answers
            )
            
            answer = result['response']
            answer_length = len(answer)
            print(f"✅ Answer generated: {answer_length} characters")
            print(f"   Preview: {answer[:150]}...")
            
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"AI service error: {str(e)}"
            )
        
        # =====================================================================
        # STEP 7: FORMAT RESPONSE - Chuẩn bị response cho client
        # =====================================================================
        print(f"\n📦 Step 7: Formatting response...")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Metadata với stats
        metadata = {
            "chunks_used": len(sources),
            "total_chunks_available": total_chunks,
            "context_length": context_length,
            "answer_length": answer_length,
            "processing_time_seconds": round(processing_time, 2),
            "model": "gemini-2.0-flash-exp",
            "embedding_model": "text-embedding-004"
        }
        
        response = RAGQueryResponse(
            success=True,
            question=request.question,
            answer=answer,
            sources=sources,
            context_used=context if request.include_context else None,
            metadata=metadata
        )
        
        print(f"\n{'='*80}")
        print(f"✅ RAG QUERY COMPLETED")
        print(f"{'='*80}")
        print(f"Processing time: {processing_time:.2f}s")
        print(f"Chunks used: {len(sources)}")
        print(f"Answer length: {answer_length} characters")
        print(f"\n")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (already formatted)
        raise
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/query/stream")
async def rag_query_stream(request: RAGQueryRequest):
    """
    RAG Query Streaming Endpoint - Stream answer với sources (like chat UI)
    
    =============================================================================
    LEARNING - STREAMING RAG FOR UI
    =============================================================================
    
    Why streaming?
    - Better UX: User sees progress immediately (sources → answer streaming)
    - Like chat UI: Show sources as "thinking", then stream answer
    - Engagement: User không phải đợi 2-3s cho full response
    
    Stream format (Server-Sent Events):
    1. Event "sources": Show retrieved documents (like thinking phase)
       data: {"type":"sources","chunks":[...],"count":5}
    
    2. Event "answer": Stream answer chunks (like chat streaming)
       data: {"type":"answer","chunk":"Giyu Tomioka..."}
       data: {"type":"answer","chunk":" là Thủy Trụ..."}
    
    3. Event "done": Final metadata
       data: {"type":"done","metadata":{...},"done":true}
    
    UI Integration:
    - Phase 1: Show sources (document cards, như thinking)
    - Phase 2: Stream answer text (như chat streaming)
    - Phase 3: Show metadata (time, chunks used)
    
    Example usage:
        const eventSource = new EventSource('/api/rag/query/stream?question=...');
        eventSource.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'sources') {
                // Show document cards
            } else if (data.type === 'answer') {
                // Append chunk to answer
            } else if (data.type === 'done') {
                // Show metadata, close stream
            }
        };
    """
    
    async def generate_stream() -> AsyncIterator[str]:
        """
        Generator function for SSE streaming
        
        LEARNING: AsyncIterator[str] = async generator
        Yield SSE format: "data: {json}\n\n"
        """
        try:
            start_time = time.time()
            
            print(f"\n{'='*80}")
            print(f"🔍 RAG STREAMING QUERY STARTED")
            print(f"{'='*80}")
            print(f"Question: {request.question}")
            
            # ================================================================
            # PHASE 1: RETRIEVE & SEND SOURCES (like "thinking")
            # ================================================================
            print(f"\n📊 Phase 1: Retrieving sources...")
            
            # Step 1: Check DB
            stats = vector_db.get_collection_stats()
            total_chunks = stats.get('total_chunks', 0)
            
            if total_chunks == 0:
                error_data = {
                    "type": "error",
                    "error": "No documents found. Please upload documents first.",
                    "done": True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            # Step 2: Embed question
            question_embedding = embedding_service.embed_text(request.question)
            print(f"✅ Question embedded")
            
            # Step 3: Search chunks
            filter_metadata = None
            if request.document_id:
                filter_metadata = {"document_id": request.document_id}
            
            search_results = vector_db.search(
                query_embedding=question_embedding,
                n_results=request.n_results,
                filter_metadata=filter_metadata
            )
            
            if search_results['count'] == 0:
                error_data = {
                    "type": "error",
                    "error": "No relevant information found.",
                    "done": True
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            print(f"✅ Found {search_results['count']} chunks")
            
            # Step 4: Prepare sources
            sources = []
            context_parts = []
            
            for i, result in enumerate(search_results['results'], 1):
                chunk_text = result['text']
                metadata = result.get('metadata', {})
                
                # Source info
                source_info = f"[Source {i}]"
                if metadata.get('filename'):
                    source_info += f" From: {metadata['filename']}"
                if metadata.get('chunk_index') is not None:
                    source_info += f" (Chunk {metadata['chunk_index']})"
                
                context_parts.append(f"{source_info}\n{chunk_text}")
                
                # Prepare source for UI
                sources.append({
                    "chunk_id": result['id'],
                    "text": chunk_text,
                    "text_preview": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                    "distance": result.get('distance', 0),
                    "similarity": 1 - result.get('distance', 0),
                    "metadata": metadata,
                    "source_number": i
                })
            
            context = "\n\n---\n\n".join(context_parts)
            context_length = len(context)
            
            # Send sources event (like "thinking" phase)
            # LEARNING: UI shows này như document cards, giống thinking mode
            sources_event = {
                "type": "sources",
                "chunks": sources,
                "count": len(sources),
                "total_chunks_available": total_chunks
            }
            yield f"data: {json.dumps(sources_event, ensure_ascii=False)}\n\n"
            print(f"📤 Sent sources to UI")
            
            # ================================================================
            # PHASE 2: GENERATE & STREAM ANSWER (like chat streaming)
            # ================================================================
            print(f"\n💭 Phase 2: Generating answer...")
            
            # Create prompt
            prompt = f"""You are a helpful AI assistant. Answer the question based ONLY on the context provided below.

CONTEXT FROM DOCUMENTS:
{context}

QUESTION: {request.question}

INSTRUCTIONS:
- Answer in the same language as the question (Vietnamese or English)
- Base your answer ONLY on the information in the context above
- If the context doesn't contain relevant information, say "I don't have enough information to answer this question based on the provided documents."
- Be specific and cite which source ([Source 1], [Source 2], etc.) supports your answer
- Use clear and concise language
- If multiple sources say the same thing, mention that for credibility

ANSWER:"""
            
            print(f"🤖 Calling Gemini to stream answer...")
            
            # Stream answer from Gemini
            # LEARNING: generate_stream_response() streams chunks
            answer_text = ""
            
            async for chunk_data in gemini_service.generate_stream_response(
                message=prompt,
                temperature=0.7,
                thinking_budget=0  # No thinking for RAG
            ):
                chunk_type = chunk_data.get('type')
                chunk_text = chunk_data.get('chunk', '')
                
                # Only stream answer chunks (not thoughts, not done)
                if chunk_type == 'answer' and chunk_text:
                    answer_text += chunk_text
                    
                    # Send answer chunk to UI
                    answer_event = {
                        "type": "answer",
                        "chunk": chunk_text,
                        "done": False
                    }
                    yield f"data: {json.dumps(answer_event, ensure_ascii=False)}\n\n"
                
                # Handle errors
                elif chunk_type == 'error':
                    error_event = {
                        "type": "error",
                        "error": chunk_data.get('error', 'Unknown error'),
                        "done": True
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"
                    return
            
            # ================================================================
            # PHASE 3: SEND FINAL METADATA
            # ================================================================
            end_time = time.time()
            processing_time = end_time - start_time
            
            print(f"✅ Answer streamed: {len(answer_text)} characters")
            print(f"⏱️  Total time: {processing_time:.2f}s")
            
            # Send done event với metadata
            done_event = {
                "type": "done",
                "done": True,
                "metadata": {
                    "chunks_used": len(sources),
                    "total_chunks_available": total_chunks,
                    "context_length": context_length,
                    "answer_length": len(answer_text),
                    "processing_time_seconds": round(processing_time, 2),
                    "model": "gemini-2.0-flash-exp",
                    "embedding_model": "text-embedding-004"
                }
            }
            yield f"data: {json.dumps(done_event)}\n\n"
            
            print(f"\n{'='*80}")
            print(f"✅ RAG STREAMING COMPLETED")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"\n❌ Streaming error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_event = {
                "type": "error",
                "error": str(e),
                "done": True
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    # Return SSE response
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/stats")
async def get_rag_stats():
    """
    Get RAG System Statistics - Xem trạng thái hệ thống
    
    =============================================================================
    LEARNING - STATS ENDPOINT
    =============================================================================
    
    Why stats endpoint?
    - Monitor system health: Có documents chưa? DB hoạt động?
    - Debug: Nếu RAG query fail, check stats first
    - UI: Show "Ready" badge nếu có data, "Upload documents" nếu empty
    
    Returns:
    - ready: boolean - System ready for queries?
    - total_documents: int - Number of uploaded documents
    - total_chunks: int - Number of embedded chunks
    - status: str - "ready" | "no_data" | "error"
    - message: str - Human-readable status
    
    Example response:
    {
        "ready": true,
        "total_documents": 3,
        "total_chunks": 150,
        "status": "ready",
        "message": "RAG system ready with 3 documents and 150 chunks"
    }
    """
    try:
        print(f"\n📊 Checking RAG system stats...")
        
        # Get collection stats từ vector DB
        # LEARNING: ChromaDB stores stats về documents và chunks
        stats = vector_db.get_collection_stats()
        total_chunks = stats.get('total_chunks', 0)
        
        # Get list of documents
        # LEARNING: Each document có thể có nhiều chunks
        documents = vector_db.list_all_documents()
        total_documents = len(documents)
        
        # Determine system status
        if total_chunks > 0:
            ready = True
            status = "ready"
            message = f"RAG system ready with {total_documents} documents and {total_chunks} chunks"
        else:
            ready = False
            status = "no_data"
            message = "No documents found. Please upload and embed documents first."
        
        print(f"✅ Stats: {total_documents} docs, {total_chunks} chunks, status={status}")
        
        return {
            "ready": ready,
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "status": status,
            "message": message,
            "collection_name": "documents",  # Current collection name
            "embedding_model": "text-embedding-004",
            "chat_model": "gemini-2.0-flash-exp"
        }
        
    except Exception as e:
        print(f"❌ Error getting stats: {str(e)}")
        
        return {
            "ready": False,
            "total_documents": 0,
            "total_chunks": 0,
            "status": "error",
            "message": f"Error: {str(e)}"
        }
