from fastapi import Depends, APIRouter
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..schemas import (CourseCreateModel, CourseUpdateModel, CourseResponseModel)
from ..service import (CourseService, TokenService)
from datetime import timedelta, datetime
from ..dependencies import (get_current_user, RoleChecker,check_revoked_token)
from typing import List

router = APIRouter(
    prefix="/course",
    tags=["Courses"],
)

course = CourseService()
revoked_token = TokenService()

role_checker = Depends(RoleChecker(['editor', 'admin']))
revoked_token_check = Depends(check_revoked_token)


@router.get('/get/all', dependencies=[revoked_token_check], response_model=List[CourseResponseModel])
async def get_all_courses(session: AsyncSession = Depends(get_session)):
    course_q = await course.get_all_courses(session)

    return course_q



@router.get('/get/{course_uid}', dependencies=[ revoked_token_check], response_model=CourseResponseModel)
async def get_course_by_uid(course_uid: str, session: AsyncSession = Depends(get_session)):
    course_q = await course.get_course_by_uid(course_uid, session)

    return course_q


@router.post('/create', dependencies=[role_checker, revoked_token_check])
async def create_course(course_data: CourseCreateModel, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    user_uid = current_user.uid
    course_q = await course.create_course(user_uid, course_data, session)

    return course_q

@router.put('/update/{course_uid}', dependencies=[role_checker, revoked_token_check], response_model=CourseResponseModel)
async def update_a_course( course_uid: str, course_data: CourseUpdateModel, session: AsyncSession = Depends(get_session)):
    course_q = await course.update_a_course(course_uid, course_data, session)

    return course_q

@router.delete('/delete/{course_uid}', dependencies=[role_checker, revoked_token_check])
async def delete_a_course(course_uid: str, session: AsyncSession = Depends(get_session)):
    course_q = await course.delete_a_course(course_uid, session)

    return course_q