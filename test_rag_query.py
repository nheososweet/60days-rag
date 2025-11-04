"""
Test RAG Query System - Kiểm tra hệ thống hỏi đáp trên documents

=============================================================================
HƯỚNG DẪN SỬ DỤNG:
=============================================================================

1. Đảm bảo server đang chạy: python main.py
2. Đảm bảo đã upload documents và embedding: python test_document_api.py
3. Run script này: python test_rag_query.py

Script này sẽ:
- Check RAG stats (có documents chưa?)
- Test RAG query với câu hỏi mẫu
- Show answer + sources + metadata
"""

import requests
import json
import time
from typing import Dict, Any


# API Configuration
BASE_URL = "http://localhost:3201"
RAG_STATS_URL = f"{BASE_URL}/api/rag/stats"
RAG_QUERY_URL = f"{BASE_URL}/api/rag/query"


def print_section(title: str, width: int = 80):
    """Print section header"""
    print(f"\n{'='*width}")
    print(f"  {title}")
    print(f"{'='*width}\n")


def check_rag_stats():
    """
    STEP 1: Check RAG System Stats
    Kiểm tra xem hệ thống có ready chưa (có documents chưa)
    """
    print_section("📊 STEP 1: Checking RAG System Stats")
    
    try:
        response = requests.get(RAG_STATS_URL)
        response.raise_for_status()
        
        stats = response.json()
        
        print("✅ RAG Stats retrieved successfully!\n")
        print(f"Ready:            {stats.get('ready')}")
        print(f"Total Documents:  {stats.get('total_documents')}")
        print(f"Total Chunks:     {stats.get('total_chunks')}")
        print(f"Status:           {stats.get('status')}")
        print(f"Message:          {stats.get('message')}")
        print(f"\nCollection:       {stats.get('collection_name')}")
        print(f"Embedding Model:  {stats.get('embedding_model')}")
        print(f"Chat Model:       {stats.get('chat_model')}")
        
        return stats
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server!")
        print("   Make sure server is running: python main.py")
        return None
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None


def test_rag_query(question: str, n_results: int = 5, include_context: bool = False):
    """
    STEP 2: Test RAG Query
    Hỏi câu hỏi và xem AI trả lời như thế nào dựa trên documents
    
    Args:
        question: Câu hỏi (Vietnamese or English)
        n_results: Số chunks muốn lấy (1-20, default=5)
        include_context: True nếu muốn xem context đã dùng
    """
    print_section(f"🤖 STEP 2: Testing RAG Query")
    
    print(f"Question: {question}")
    print(f"N_results: {n_results}")
    print(f"Include context: {include_context}\n")
    
    # Prepare request
    request_data = {
        "question": question,
        "n_results": n_results,
        "include_context": include_context
    }
    
    print("📤 Sending request to RAG API...")
    print(f"   URL: {RAG_QUERY_URL}")
    print(f"   Payload: {json.dumps(request_data, indent=2, ensure_ascii=False)}\n")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            RAG_QUERY_URL,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        request_time = end_time - start_time
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Response received in {request_time:.2f}s\n")
        
        # Display results
        print_section("📝 ANSWER FROM AI")
        print(result.get('answer', 'No answer'))
        
        # Display sources
        sources = result.get('sources', [])
        if sources:
            print_section(f"📚 SOURCES ({len(sources)} chunks used)")
            for i, source in enumerate(sources, 1):
                print(f"\n[Source {i}]")
                print(f"  Similarity: {source.get('similarity', 0):.3f}")
                print(f"  Distance:   {source.get('distance', 0):.3f}")
                
                metadata = source.get('metadata', {})
                if metadata.get('filename'):
                    print(f"  File:       {metadata['filename']}")
                if metadata.get('chunk_index') is not None:
                    print(f"  Chunk:      {metadata['chunk_index']}")
                
                print(f"\n  Text Preview:")
                print(f"  {source.get('text_preview', '')}")
                print(f"  {'-'*76}")
        
        # Display context if requested
        if include_context and result.get('context_used'):
            print_section("📄 CONTEXT USED (Full)")
            print(result['context_used'])
        
        # Display metadata
        metadata = result.get('metadata', {})
        if metadata:
            print_section("🔍 METADATA")
            print(f"Chunks used:            {metadata.get('chunks_used')}")
            print(f"Total chunks available: {metadata.get('total_chunks_available')}")
            print(f"Context length:         {metadata.get('context_length')} chars")
            print(f"Answer length:          {metadata.get('answer_length')} chars")
            print(f"Processing time:        {metadata.get('processing_time_seconds')}s")
            print(f"Embedding model:        {metadata.get('embedding_model')}")
            print(f"Chat model:             {metadata.get('model')}")
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP ERROR: {e}")
        try:
            error_detail = response.json()
            print(f"   Detail: {error_detail}")
        except:
            print(f"   Response: {response.text}")
        return None
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def run_test_suite():
    """
    Run complete test suite
    Chạy tất cả các test cases
    """
    print_section("🚀 RAG QUERY TEST SUITE", width=80)
    print("Testing RAG (Retrieval-Augmented Generation) system")
    print("This will test if AI can answer questions based on your documents\n")
    
    # Step 1: Check stats
    stats = check_rag_stats()
    
    if not stats:
        print("\n⚠️  Cannot proceed: Server not running")
        return
    
    if not stats.get('ready'):
        print(f"\n⚠️  Cannot proceed: {stats.get('message')}")
        print("   Please run: python test_document_api.py first")
        return
    
    print(f"\n✅ System ready! {stats.get('total_documents')} documents with {stats.get('total_chunks')} chunks\n")
    
    # Wait a bit
    print("⏳ Starting tests in 2 seconds...\n")
    time.sleep(2)
    
    # Test cases - Điều chỉnh câu hỏi theo documents của bạn
    test_cases = [
        {
            "question": "Giyu Tomioka là ai?",
            "n_results": 5,
            "include_context": False
        },
        {
            "question": "Shinobu Kocho có tính cách như thế nào?",
            "n_results": 3,
            "include_context": False
        },
        # Uncomment để test thêm:
        # {
        #     "question": "Who are the main characters?",
        #     "n_results": 10,
        #     "include_context": True
        # },
    ]
    
    # Run each test
    for i, test_case in enumerate(test_cases, 1):
        if i > 1:
            print("\n" + "="*80)
            print(f"⏳ Next test in 3 seconds...")
            print("="*80)
            time.sleep(3)
        
        print(f"\n{'#'*80}")
        print(f"# TEST CASE {i}/{len(test_cases)}")
        print(f"{'#'*80}")
        
        test_rag_query(**test_case)
    
    # Summary
    print_section("✅ TEST SUITE COMPLETED")
    print(f"Ran {len(test_cases)} test cases")
    print("\nNotes:")
    print("- Điều chỉnh câu hỏi trong test_cases[] theo documents của bạn")
    print("- Tăng n_results để lấy nhiều chunks hơn (1-20)")
    print("- Set include_context=True để xem context đầy đủ")
    print("- Check console log của server để xem detailed workflow")


if __name__ == "__main__":
    run_test_suite()
