"""
CrewAI Compatibility Patches.
Fixes for CrewAI 1.7.0 async memory issues.
"""

import sys
import signal


def apply_windows_patches():
    """Apply Windows-specific compatibility patches."""
    if sys.platform == 'win32':
        # Windows doesn't support SIGHUP
        if not hasattr(signal, 'SIGHUP'):
            signal.SIGHUP = None
        # Set console encoding to UTF-8
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass  # Python < 3.7 doesn't support reconfigure


def apply_chromadb_async_patch():
    """
    Patch ChromaDBClient.asearch() to use sync implementation.
    CrewAI 1.7.0's memory calls asearch() in async mode, but ChromaDB client is synchronous.
    """
    import crewai.rag.chromadb.client as chromadb_client_module
    original_ChromaDBClient = chromadb_client_module.ChromaDBClient

    class PatchedChromaDBClient(original_ChromaDBClient):
        """Patched ChromaDBClient - calls sync implementation in async method."""
        async def asearch(self, **kwargs):
            return self.search(**kwargs)

    chromadb_client_module.ChromaDBClient = PatchedChromaDBClient


def apply_rag_storage_async_patch():
    """
    Patch RAGStorage.asearch() to use sync implementation.
    """
    import crewai.memory.storage.rag_storage as rag_storage_module
    original_RAGStorage = rag_storage_module.RAGStorage

    class PatchedRAGStorage(original_RAGStorage):
        """Patched RAGStorage - directly uses sync method."""
        async def asearch(self, query: str, limit: int = 5, filter=None, score_threshold: float = 0.6):
            return self.search(query, limit, filter, score_threshold)

    rag_storage_module.RAGStorage = PatchedRAGStorage


def apply_crewai_patches(verbose: bool = True):
    """
    Apply all CrewAI compatibility patches.
    
    Args:
        verbose: Whether to print confirmation message
    """
    apply_windows_patches()
    apply_chromadb_async_patch()
    apply_rag_storage_async_patch()
    
    if verbose:
        print("✅ CrewAI async memory compatibility patch applied")
