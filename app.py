import os

import uvicorn
from api_app.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("FASTAPI_RELOAD", "0") == "1",
    )
