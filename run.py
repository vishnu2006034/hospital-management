"""Application entry point.

Configures and runs the Flask application server.
"""

import os
import sys
# from typing import NoReturn

from app import create_app
from app.logging_config import setup_logging, get_logger

# Setup Logging
log_level: str = os.getenv('LOG_LEVEL', 'INFO')
setup_logging(log_level)
logger = get_logger(__name__)

app = create_app()

logger.info('Starting application')


def main() -> None:
    """Run the application server."""
    debug: bool = os.getenv('FLASK_DEBUG', '0') == '1'
    host: str = os.getenv('FLASK_HOST', '0.0.0.0')
    port: int = int(os.getenv('FLASK_PORT', '5000'))

    logger.info(f'Server running on {host}:{port}')
    app.run(debug=debug, host=host, port=port)


if __name__ == '__main__':
    main()
