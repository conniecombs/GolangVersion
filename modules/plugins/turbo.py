# modules/plugins/turbo.py
"""
TurboImageHost plugin - Schema-based implementation.

Python-based upload plugin with optional login and endpoint configuration.
"""

import os
from typing import Dict, Any, List
from .base import ImageHostPlugin
from . import helpers
from .. import api
from loguru import logger


class TurboPlugin(ImageHostPlugin):
    """TurboImageHost image hosting plugin using schema-based UI."""

    @property
    def id(self) -> str:
        return "turboimagehost"

    @property
    def name(self) -> str:
        return "TurboImageHost"

    @property
    def metadata(self) -> Dict[str, Any]:
        """Plugin metadata for TurboImageHost"""
        return {
            "version": "2.0.0",
            "author": "Connie's Uploader Team",
            "description": "Upload images to TurboImageHost with optional authentication, dynamic endpoint configuration, and cover image support",
            "website": "https://www.turboimagehost.com",
            "implementation": "python",
            "features": {
                "galleries": True,
                "covers": True,
                "authentication": "optional",
                "direct_links": True,
                "custom_thumbnails": True,
                "dynamic_endpoint": True,  # Fetches upload endpoint dynamically
            },
            "credentials": [
                {
                    "key": "turbo_user",
                    "label": "Username",
                    "required": False,
                    "description": "Optional login for enhanced features",
                },
                {
                    "key": "turbo_pass",
                    "label": "Password",
                    "required": False,
                    "secret": True,
                    "description": "Password for enhanced features",
                },
            ],
            "limits": {
                "max_file_size": 50 * 1024 * 1024,  # 50MB
                "allowed_formats": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
                "rate_limit": "Moderate (respectful use)",
                "max_resolution": (15000, 15000),
                "min_resolution": (1, 1),
            },
        }

    @property
    def settings_schema(self) -> List[Dict[str, Any]]:
        """Declarative UI schema for Turbo settings."""
        return [
            {
                "type": "label",
                "text": "ℹ️ Login Optional",
                "color": "orange",
            },
            {
                "type": "dropdown",
                "key": "thumbnail_size",
                "label": "Thumbnail Size",
                "values": ["150", "200", "250", "300", "350", "400", "500", "600"],
                "default": "180",
                "required": True,
            },
            {
                "type": "inline_group",
                "fields": [
                    {"type": "label", "text": "Cover Images:", "width": 100},
                    {
                        "type": "dropdown",
                        "key": "cover_count",
                        "values": [str(i) for i in range(11)],
                        "default": "0",
                        "width": 80,
                    },
                ],
            },
            {
                "type": "checkbox",
                "key": "save_links",
                "label": "Save Links.txt",
                "default": False,
            },
            {
                "type": "separator",
            },
            {
                "type": "text",
                "key": "gallery_id",
                "label": "Gallery ID (Optional)",
                "default": "",
                "placeholder": "Leave blank for auto-gallery",
            },
        ]

    def validate_configuration(self, config: Dict[str, Any]) -> List[str]:
        """Custom validation for Turbo configuration."""
        errors = []

        # Convert cover_count to int (using helper)
        helpers.validate_cover_count(config, errors)

        # Content type - turbo uses "adult" or "all"
        # For now, default to "all" (safe)
        config["content_type"] = "all"

        return errors

    # --- Upload Implementation (Unchanged from original) ---

    def initialize_session(
        self, config: Dict[str, Any], creds: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Initialize upload session for TurboImageHost.

        Gets endpoint configuration and handles optional login.
        """
        # Create context with client (using helper)
        context = helpers.create_upload_context(
            api,
            cookies=None,
            endpoint="https://www.turboimagehost.com/upload_html5.tu"
        )

        # Get client from context
        client = helpers.get_client_from_context(context)

        # 1. Get Config/Endpoint
        ep = api.get_turbo_config(client=client)
        if ep:
            context["endpoint"] = ep

        # 2. Login (optional)
        user = creds.get("turbo_user")
        pwd = creds.get("turbo_pass")
        if user and pwd:
            cookies = api.turbo_login(user, pwd, client=client)
            if cookies:
                context["cookies"] = cookies
                logger.info("TurboImageHost login successful")

        return context

    def upload_file(
        self, file_path: str, group, config: Dict[str, Any], context: Dict[str, Any], progress_callback
    ):
        """
        Upload a single file to TurboImageHost.

        Args:
            file_path: Path to image file
            group: Group object containing files
            config: Plugin configuration from UI
            context: Session context from initialize_session
            progress_callback: Function to report upload progress

        Returns:
            Tuple of (viewer_url, thumb_url)
        """
        # Get client from context (using helper)
        client = helpers.get_client_from_context(context)

        # Apply cookies if present
        if context.get("cookies"):
            client.cookies.update(context["cookies"])

        # Determine if this is a cover image (using helper)
        is_cover = helpers.is_cover_image(file_path, group, config)

        # Use max thumbnail size for covers
        thumb = "600" if is_cover else config["thumbnail_size"]

        # Create uploader (using helper for progress callback)
        uploader = api.TurboUploader(
            file_path,
            os.path.basename(file_path),
            helpers.create_progress_callback(progress_callback),
            context["endpoint"],
            api.generate_turbo_upload_id(),
            config["content_type"],
            thumb,
            config.get("gallery_id"),
            client=client,
        )

        try:
            # Perform upload (using helpers)
            url, data, headers = uploader.get_request_params()
            headers = helpers.prepare_upload_headers(headers, data)
            r = client.post(url, headers=headers, data=data, timeout=300)

            try:
                resp = r.json()
            except (ValueError, TypeError) as e:
                logger.debug(f"Response was not JSON, using text: {e}")
                resp = r.text

            return uploader.parse_response(resp)
        finally:
            uploader.close()
