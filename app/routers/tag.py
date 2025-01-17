from fastapi import Depends, APIRouter, status
from ..db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from ..schemas import (TagModel)
from ..service import (TagService, TokenService)
from ..dependencies import (RoleChecker,check_revoked_token)


router = APIRouter(
    prefix="/tag",
    tags=["Tags"],
)

tag = TagService()
revoked_token = TokenService()

role_checker = Depends(RoleChecker(['admin']))
revoked_token_check = Depends(check_revoked_token)



@router.get('/get/all', dependencies=[revoked_token_check])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tag_q = await tag.get_all_tags(session)

    return tag_q

@router.get('/name/{query}', dependencies=[ revoked_token_check])
async def get_all_tags(query:str = None, session: AsyncSession = Depends(get_session)):
    tag_q = await tag.get_all_tag_name(query=query, session=session)

    return tag_q

@router.get('/get/{tag_id}', dependencies=[role_checker, revoked_token_check])
async def get_tag_by_uid(tag_id: int, session: AsyncSession = Depends(get_session)):
    tag_q = await tag.get_tag_by_id(tag_id, session)

    return tag_q

@router.get('/name/{tag_name}', dependencies=[role_checker, revoked_token_check])
async def get_tag_by_uid(tag_name: str, session: AsyncSession = Depends(get_session)):
    tag_q = await tag.get_tag_by_name(tag_name, session)

    return tag_q

@router.post('/create', dependencies=[role_checker, revoked_token_check])
async def create_tag(tag_name: TagModel, session: AsyncSession = Depends(get_session)):
    tag_q = await tag.create_tag(tag_name, session)

    return tag_q

@router.put('/update/{tag_id}', dependencies=[role_checker, revoked_token_check])
async def update_a_tag( tag_id: int, tag_name: TagModel, session: AsyncSession = Depends(get_session)):
    tag_q = await tag.update_tag(tag_id, tag_name, session)

    return tag_q

@router.delete('/delete/{tag_id}', dependencies=[role_checker, revoked_token_check], status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_tag(tag_id: int, session: AsyncSession = Depends(get_session)):
    tag_q = await tag.delete_tag(tag_id, session)

    return tag_q

