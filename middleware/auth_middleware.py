from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from service.auth_service import AuthService
from dao.user_dao import UserDAO
from db.session import Database

# Paths that don't require authentication
EXCLUDED_PATHS = ["/auth/login", "/docs", "/openapi.json", "/redoc", "/favicon.ico"]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Check excluded paths
        if any(request.url.path.startswith(path) for path in EXCLUDED_PATHS):
            return await call_next(request)

        # Get token from cookie
        token = request.cookies.get("access_token")
        if not token:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "msg": "Not authenticated", "data": None}
            )

        # Verify token
        # Note: We need to instantiate services manually here because middleware 
        # is initialized before FastAPI dependency injection system.
        # However, for simple JWT verification we can reuse AuthService logic 
        # or duplicate it slightly. To keep it clean, let's instantiate.
        # But instantiating AuthService requires UserDAO which requires DB connection.
        # Creating DB connection on every request in middleware is fine but we must close it.
        
        try:
            # Simple manual JWT decode without full service instantiation to avoid overhead
            # We import SECRET_KEY and ALGORITHM from auth_service to keep DRY
            from service.auth_service import SECRET_KEY, ALGORITHM
            import jwt
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if username is None:
                raise Exception("Invalid token")
                
            # Store user info in request state
            request.state.user = {"id": user_id, "username": username}
            
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"code": 401, "msg": "Invalid or expired token", "data": None}
            )

        response = await call_next(request)
        return response
