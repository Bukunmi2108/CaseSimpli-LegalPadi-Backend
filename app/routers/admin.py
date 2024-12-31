from fastapi import Body, Depends, status, APIRouter,  BackgroundTasks
from fastapi.responses import JSONResponse
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..schemas import AdminLoginModel, AdminCreateModel, AdminUpdateModel, AdminProfileModel
from ..service import TokenService, AdminService
from ..utils import create_access_token, verify_passwd_hash
from datetime import timedelta
from ..dependencies import AccessTokenBearer, RoleChecker, check_revoked_token, get_current_user
from ..errors import InvalidCredentials
from ..models import UserRole


router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)

admin = AdminService()
revoked_token = TokenService()
role_checker = Depends(RoleChecker(["admin"]))
revoked_token_check = Depends(check_revoked_token)



################################
@router.post('/create_super_admin')
async def create_super_admin(background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    result = await admin.create_super_admin( background_tasks, session=session)
    
    return result
################################

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_new_admin(admin_data: AdminCreateModel = Body(...), session: AsyncSession = Depends(get_session)):
    new_admin = await admin.create_an_admin(admin_data, session)
    return new_admin

@router.post("/login")
async def login_admin(login_data: AdminLoginModel = Body(...), session: AsyncSession = Depends(get_session)):
    admin_email = login_data.email

    existing_admin = await admin.get_admin_by_email(admin_email, session=session)
    if existing_admin is not None:
        passwd_valid = verify_passwd_hash(password=login_data.password, hashed_password=existing_admin.password)

        if passwd_valid:
            access_token = create_access_token(user_data={
                'email': existing_admin.email,
                'user_uid': str(existing_admin.uid),
                'role': existing_admin.role
            })
        
            refresh_token = create_access_token(user_data={
                'email': existing_admin.email,
                'user_uid': str(existing_admin.uid)
            },
            refresh=True,
            expiry=timedelta(days=2)
            )


            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": existing_admin.email,
                        'uid': str(existing_admin.uid)
                    }
                }
            )
        
    raise InvalidCredentials

@router.get('/profile', dependencies=[role_checker, revoked_token_check], response_model=AdminProfileModel)
async def get_user_profile(user = Depends(get_current_user)):
    return user


@router.get("/logout")
async def logout_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):

    await revoked_token.add_token_to_blacklist(session=session, token_jti= token_details['jti'])

    return JSONResponse(
        content={
            "message": "Logout successfully"
        },
        status_code=status.HTTP_200_OK
    )