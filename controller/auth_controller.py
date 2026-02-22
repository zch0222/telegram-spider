from fastapi import APIRouter, Depends, Request, Response, HTTPException
from service.auth_service import AuthService
from model.res_data import ResData
from pydantic import BaseModel

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginDTO(BaseModel):
    username: str
    password: str

class ChangePasswordDTO(BaseModel):
    old_password: str
    new_password: str

@auth_router.post("/login")
def login(dto: LoginDTO, response: Response, service: AuthService = Depends()):
    token = service.login(dto.username, dto.password)
    if not token:
        return ResData.error("Invalid username or password")
    
    # Set secure cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        # secure=True, # Enable in production with HTTPS
        # samesite="Lax",
        max_age=60 * 60 * 24 * 7 # 7 days
    )
    return ResData.success("Login successful")

@auth_router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return ResData.success("Logout successful")

@auth_router.post("/change_password")
def change_password(dto: ChangePasswordDTO, request: Request, service: AuthService = Depends()):
    # Get user from token manually or via middleware (but middleware is not applied here yet if we don't use Depends)
    # Ideally we should have a get_current_user dependency.
    # But since we are implementing middleware globally later, we can get user from request.state.user
    
    user = getattr(request.state, "user", None)
    if not user:
         raise HTTPException(status_code=401, detail="Not authenticated")

    service.change_password(user["id"], dto.old_password, dto.new_password)
    return ResData.success("Password changed successfully")
