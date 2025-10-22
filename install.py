# Add to the installation process
def track_installation():
    """Track installation for usage analytics"""
    try:
        # Call the uninstall script to track installation
        import subprocess
        subprocess.run(['./uninstall.sh', '--track-install'], check=True)
        logger.info("✅ Installation tracking initialized")
    except Exception as e:
        logger.warning(f"⚠️ Installation tracking failed: {e}")

# Call this after successful installation
track_installation()
