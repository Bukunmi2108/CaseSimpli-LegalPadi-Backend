from fastapi import status, Body, Depends, APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..schemas import (UserCreateModel, UserUpdateModel, UserResponseModel, UserLoginModel, AdminEditorResponseProfileModel)
from ..service import (UserService, TokenService)
from ..utils import (create_access_token, verify_passwd_hash, decode_safe_url)
from datetime import timedelta, datetime
from ..dependencies import (RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker,check_revoked_token)
from ..errors import (InvalidToken, InvalidCredentials, UserNotFound)


router = APIRouter(
    prefix="/user",
    tags=["Users"],
)

user = UserService()
revoked_token = TokenService()

role_checker = Depends(RoleChecker(['user', 'editor', 'admin']))
role_checker_admin = Depends(RoleChecker(['editor', 'admin']))
revoked_token_check = Depends(check_revoked_token)


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponseModel)
async def create_user_account(background_tasks: BackgroundTasks, user_data: UserCreateModel = Body(...), session: AsyncSession = Depends(get_session)):
    new_user = await user.create_a_user(user_data, background_tasks, session)
    return new_user

@router.post("/login")
async def login_user(login_data: UserLoginModel = Body(...), session: AsyncSession = Depends(get_session)):
    user_email = login_data.email

    existing_user = await user.get_all_user_by_email(user_email, session)

    if existing_user is not None:
        passwd_valid = verify_passwd_hash(password=login_data.password, hashed_password=existing_user.password)

        if passwd_valid:
            access_token = create_access_token(user_data={
                'email': existing_user.email,
                'user_uid': str(existing_user.uid),
                'role': existing_user.role
            })
        
            refresh_token = create_access_token(user_data={
                'email': existing_user.email,
                'user_uid': str(existing_user.uid)
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
                        "email": existing_user.email,
                        'uid': str(existing_user.uid)
                    }
                }
            )
        
    raise InvalidCredentials

@router.get('/profile', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def get_user_profile(user = Depends(get_current_user)):
    return user

@router.get('/admin/profile', dependencies=[role_checker_admin, revoked_token_check], response_model=AdminEditorResponseProfileModel)
async def get_user_profile(user = Depends(get_current_user)):
    return user

@router.get('/editor/profile', dependencies=[role_checker_admin, revoked_token_check], response_model=AdminEditorResponseProfileModel)
async def get_user_profile(user = Depends(get_current_user)):
    return user

@router.get('/role', dependencies=[role_checker, revoked_token_check])
async def get_user_role(current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    role = await user.get_user_role(current_user.uid, session)
    return role

@router.put('/update_user', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def update_user_profile(user_data: UserUpdateModel = Body(...), current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await user.update_a_user(current_user.uid, user_data, session)
    return result

@router.put('/make_premium', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def update_user_profile( current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    result = await user.update_user_data(current_user.uid, {"is_premium": True}, session)
    return result

@router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):

    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data=token_details['user']
        )

        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )
    
    raise InvalidToken()

@router.get("/logout")
async def logout_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)):

    await revoked_token.add_token_to_blacklist(session=session, token_jti= token_details['jti'])

    return JSONResponse(
        content={
            "message": "Logout successfully"
        },
        status_code=status.HTTP_200_OK
    )

@router.get("/verify_safe_url/{url}")
async def verify_safe_url(url:str, session: AsyncSession = Depends(get_session)):
    signage = decode_safe_url(url)
    
    email = signage.get('email', None)
    user_uid = signage.get('user_uid', None)

    if signage is None:
        return {"message": "Invalid URL"}
    
    update_status = await user.update_user_data(user_uid, {"is_verified": True}, session)
    if update_status is None:
        raise UserNotFound
    
    return {"message": "Email verified successfully"}

@router.delete('/delete_account', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await user.delete_a_user(current_user.uid, session)
    return JSONResponse(
        content={
            "message": "Account deleted successfully"
        }
    )