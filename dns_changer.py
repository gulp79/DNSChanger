"""
DNSChanger - A modern DNS management tool for Windows.

Features:
- Change DNS servers on network adapters
- Support for DNS over HTTPS (DoH)
- DNS verification with automatic rollback
- YAML-based DNS provider configuration
- Migration from legacy dns_list.txt format
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dnschanger.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_admin_privileges() -> bool:
    """Check if running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()  # type: ignore
    except:
        return False


def request_admin_elevation():
    """Request administrator elevation."""
    try:
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(  # type: ignore
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )
    except Exception as e:
        logger.error(f"Failed to request admin elevation: {e}")


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("DNSChanger starting...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("=" * 60)
    
    # Check for admin privileges
    if not check_admin_privileges():
        logger.warning("Not running as administrator. Requesting elevation...")
        request_admin_elevation()
        sys.exit(0)
    
    logger.info("Running with administrator privileges ✓")
    
    # Import GUI after admin check
    try:
        from ui.main_window import DNSChangerApp  # type: ignore
        
        logger.info("Initializing GUI...")
        app = DNSChangerApp()
        
        logger.info("Starting main loop...")
        app.mainloop()
        
        logger.info("Application closed normally")
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Make sure all dependencies are installed (customtkinter, pydantic, pyyaml)")
        try:
            import tkinter.messagebox as _mb
            _mb.showerror("DNSChanger", f"Failed to import modules:\n\n{e}\n\nCheck dnschanger.log for details.")
        except Exception:
            pass
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        try:
            import tkinter.messagebox as _mb
            _mb.showerror("DNSChanger", f"Unexpected error:\n\n{e}\n\nCheck dnschanger.log for details.")
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
