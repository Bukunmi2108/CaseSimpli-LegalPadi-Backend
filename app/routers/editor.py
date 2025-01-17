from fastapi import Depends, APIRouter, BackgroundTasks, status
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..schemas import (UserCreateModel, UserUpdateModel, UserResponseModel, AdminCreateUserModel, EditorResponseModel)
from ..service import (EditorService, UserService, TokenService)
from ..dependencies import (RoleChecker,check_revoked_token)
from typing import List


router = APIRouter(
    prefix="/editor",
    tags=["Editor"],
)

editor = EditorService()
user = UserService()
revoked_token = TokenService()

role_checker = Depends(RoleChecker(['editor', 'admin']))
role_checker_admin = Depends(RoleChecker(['admin']))
revoked_token_check = Depends(check_revoked_token)



@router.get('/get/all', dependencies=[role_checker, revoked_token_check], response_model=List[EditorResponseModel])
async def get_all_editors(session: AsyncSession = Depends(get_session)):
    editor_q = await editor.get_all_editors(session)

    return editor_q

@router.get('/get/{editor_uid}', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def get_editor_by_uid(editor_uid: str, session: AsyncSession = Depends(get_session)):
    editor_q = await editor.get_editor_by_uid(editor_uid, session)

    return editor_q

@router.post('/create', dependencies=[role_checker_admin, revoked_token_check], response_model=EditorResponseModel)
async def create_editor(editor_data: AdminCreateUserModel,background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    
    editor_q = await editor.create_an_editor(editor_data, background_tasks, session)

    return editor_q

@router.put('/update/{editor_uid}', dependencies=[role_checker, revoked_token_check], response_model=UserResponseModel)
async def update_a_editor( editor_uid: str, editor_data: UserUpdateModel, session: AsyncSession = Depends(get_session)):
    editor_q = await editor.update_a_editor(editor_uid, editor_data, session)

    return editor_q

@router.delete('/delete/{editor_uid}', dependencies=[role_checker, revoked_token_check], status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_editor(editor_uid: str, session: AsyncSession = Depends(get_session)):
    editor_q = await editor.delete_a_editor(editor_uid, session)

    return editor_q