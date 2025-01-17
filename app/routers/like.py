from fastapi import Depends, APIRouter
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..service import (LikeService, TokenService)
from ..dependencies import (RoleChecker,check_revoked_token, get_current_user)
from ..schemas import CourseResponseModel
from typing import List
import uuid

router = APIRouter(
    prefix="/like",
    tags=["Likes"],
)

like = LikeService()
revoked_token = TokenService()

role_checker = Depends(RoleChecker(['user','admin', 'editor']))
revoked_token_check = Depends(check_revoked_token)


@router.get('/{course_uid}', dependencies=[revoked_token_check, role_checker], status_code=200)
async def check_if_user_has_liked_course(course_uid: str, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_uid = current_user.uid
    response = await like.check_existing_like(user_uid, course_uid, session)
    return response

@router.post('/{course_uid}', dependencies=[revoked_token_check, role_checker], status_code=201)
async def like_a_course(course_uid: str, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_uid = current_user.uid
    response = await like.like_a_post(user_uid, course_uid, session)
    return response

@router.delete('/{course_uid}', dependencies=[revoked_token_check, role_checker], status_code=204)
async def unlike_a_course(course_uid: str, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_uid = current_user.uid
    response = await like.unlike_a_post(user_uid, course_uid, session)
    return response

