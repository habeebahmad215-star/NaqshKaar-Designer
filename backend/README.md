# NaqshKaar AI Gateway

Server-side gateway for NaqshKaar Designer.

Required environment variable:
- OPENAI_API_KEY

Optional:
- PORT
- OPENAI_TEXT_MODEL
- OPENAI_IMAGE_MODEL

Endpoints:
- GET /health
- POST /write
- POST /image
- POST /remove-background
- POST /magic-remove
- POST /enhance

The OpenAI key must remain server-side and must never be embedded in the Flutter APK.
