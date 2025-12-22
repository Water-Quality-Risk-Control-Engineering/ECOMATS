import logging
import os

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def get_language():
    """Get current language setting."""
    try:
        from src.config.config import Config
        return Config.LANGUAGE
    except Exception:
        return os.getenv("LANGUAGE", "zh")


def load_prompt(file_path):
    """Load Prompt file content with multilingual support."""
    try:
        # Get current language
        lang = get_language()
        
        # Get the directory where the current file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try to load multilingual version first
        locale_prompt_path = os.path.join(current_dir, "..", "locales", lang, "prompts", file_path)
        
        if os.path.exists(locale_prompt_path):
            with open(locale_prompt_path, 'r', encoding='utf-8') as file:
                logger.debug(f"Loaded {lang} prompt: {file_path}")
                return file.read()
        
        # Fallback to default prompts directory
        default_prompt_path = os.path.join(current_dir, "..", "prompts", file_path)
        
        if os.path.exists(default_prompt_path):
            with open(default_prompt_path, 'r', encoding='utf-8') as file:
                logger.debug(f"Loaded default prompt: {file_path}")
                return file.read()
        
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
        
    except FileNotFoundError:
        # Prompt file not found, using default backstory
        logger.warning(f"Prompt file {file_path} not found, using default backstory")
        return get_default_backstory()
    except Exception as e:
        # Unknown error occurred while loading Prompt file
        logger.error(f"Error occurred while loading Prompt file {file_path}: {str(e)}")
        return get_default_backstory()


def get_default_backstory():
    """Get default backstory."""
    lang = get_language()
    if lang == "en":
        return """You are a professional project coordination expert, familiar with all aspects of material design and evaluation.
You can intelligently select and coordinate relevant experts to participate in the work according to task requirements."""
    else:
        return """You are a professional project coordination expert, familiar with all aspects of material design and evaluation.
You can intelligently select and coordinate relevant experts to participate in the work according to task requirements."""