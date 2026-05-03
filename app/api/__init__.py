from .health.routes import router as health_router
from .trading.routes import router as trading_router

routers = [
    health_router,
    trading_router,
]
