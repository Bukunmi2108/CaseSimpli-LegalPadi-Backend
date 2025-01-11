from fastapi import Depends, APIRouter
from typing import List
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..service import (CourseTagService, TokenService)
from ..dependencies import (RoleChecker,check_revoked_token)
from ..schemas import CourseResponseModel
from typing import List
import uuid

router = APIRouter(
    prefix="/coursetag",
    tags=["Course Tags"],
)

course_tag = CourseTagService()
revoked_token = TokenService()

role_checker = Depends(RoleChecker(['admin', 'editor']))
revoked_token_check = Depends(check_revoked_token)




@router.get("/courses/{tag_id}/all", dependencies=[revoked_token_check], response_model=List[CourseResponseModel])
async def get_all_tag_courses(tag_id: int, session: AsyncSession = Depends(get_session)):
    courses = await course_tag.get_all_tag_courses(tag_id, session)

    return courses

@router.get("/tags/{course_uid}/all", dependencies=[revoked_token_check])
async def get_all_course_tags(course_uid: uuid.UUID, session: AsyncSession = Depends(get_session)):
    tags = await course_tag.get_all_course_tags(course_uid, session)

    return tags

# @router.post("/{course_uid}/add", dependencies=[revoked_token_check, role_checker])
# async def add_tags_to_course(course_uid: uuid.UUID, tags: List[str], session: AsyncSession = Depends(get_session)):
#     result = await course_tag.add_tags_to_course(course_uid, tags, session)

#     return result