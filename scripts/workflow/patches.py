"""
CrewAI Compatibility Patches.

Originally created for CrewAI 1.7.0 async memory issues.

[VERIFIED 2025-12-29] CrewAI 1.8.1 Test Results:
- RAGStorage.asearch: ✅ Native support (patch NOT needed)
- ChromaDBClient.asearch: ✅ Native support (patch NOT needed)
- Windows signal handling: ✅ Fixed in 1.7.1 (patch NOT needed on Linux)

These patches are kept for backward compatibility with older versions.
For CrewAI >= 1.8.1, you can safely skip calling apply_crewai_patches().

Version History:
- 1.7.0: Original patches created
- 1.8.1: All patches verified as unnecessary (native support added)
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
    
    Note: As of CrewAI 1.8.1, these patches are NO LONGER NEEDED.
    This function is kept for backward compatibility only.
    
    Args:
        verbose: Whether to print confirmation message
    """
    # Check CrewAI version - skip patches if >= 1.8.0
    try:
        import crewai
        version = getattr(crewai, '__version__', '0.0.0')
        major, minor = map(int, version.split('.')[:2])
        if major >= 1 and minor >= 8:
            if verbose:
                print(f"✅ CrewAI {version} detected - patches not needed (native async support)")
            return
    except Exception:
        pass  # Fall through to apply patches for safety
    
    apply_windows_patches()
    apply_chromadb_async_patch()
    apply_rag_storage_async_patch()
    
    if verbose:
        print("✅ CrewAI async memory compatibility patch applied")
