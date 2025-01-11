from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Body, HTTPException, status, BackgroundTasks
from .schemas import (RevokedTokenModel, UserCreateModel, UserUpdateModel, AdminCreateModel, AdminUpdateModel, CourseCreateModel, CourseUpdateModel, TagModel, AdminCreateUserModel)
from .models import (RevokedToken, User, UserRole, Course, Tag, CourseTag)
from sqlmodel import select, desc
from .utils import generate_passwd_hash, create_safe_url, generate_password
from .errors import (UserAlreadyExists, AdminAlreadyExists, EditorAlreadyExists, CourseAlreadyExists, CourseNotFound, UserNotFound, EditorNotFound, AdminNotFound, TagNotFound, TagAlreadyExists)
from .config import settings
from .mail import create_message, mail
from typing import List


class TokenService:
    async def add_token_to_blacklist(self, session:AsyncSession, token_jti: RevokedTokenModel):
        try:
            new_revoked_token = RevokedToken(
                token_jti= token_jti
            )

            session.add(new_revoked_token)
            await session.commit()

            return new_revoked_token
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

    async def get_token_from_blacklist(self, session:AsyncSession, token_jti: RevokedTokenModel) -> bool:
        try:
            statement = select(RevokedToken).where(RevokedToken.token_jti == token_jti)

            result = await session.exec(statement)
            return True if result.first() else None
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error is {e}")

class UserService:
    async def get_user_by_uid(self, uid: str, session: AsyncSession):
        user = select(User).where((User.uid == uid) & (User.role == UserRole.USER.value))

        result = await session.exec(user)

        if result is None:
            raise UserNotFound()
        return result.first()

    async def get_user_role(self, uid: str, session: AsyncSession):
        user = select(User).where(User.uid == uid)
        result = await session.exec(user)

        if result is None:
            raise UserNotFound()
        return result.first().role

    async def get_user_by_email(self, email: str, session: AsyncSession):
        user = select(User).where((User.email == email) & (User.role == UserRole.USER.value))

        result = await session.exec(user)

        if result is None:
            raise UserNotFound()
        return result.first() 

    async def get_all_user_by_email(self, email: str, session: AsyncSession):
        user = select(User).where(User.email == email)

        result = await session.exec(user)

        if result is None:
            raise UserNotFound()
        return result.first() 
    
    async def get_all_users(self, session: AsyncSession):
        statement = select(User).where(User.role == UserRole.USER.value).order_by(desc(User.created_at))
        
        result = await session.exec(statement)
        
        if result is None:
            raise UserNotFound()
        return result.first()
    
    async def create_a_user(self, user_data: UserCreateModel, background_tasks: BackgroundTasks, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        email = user_data_dict["email"]

        if await self.get_user_by_email(email, session):
            raise UserAlreadyExists()
        
        new_user = User(
            **user_data_dict
        )
        new_user.password = generate_passwd_hash(new_user.password)

        #######################
        safe_url = create_safe_url( str(new_user.uid), new_user.email)

        html = f"""<>
                    <h1>Welcome to the App</h1></br>
                    <p>Congratulations, you have successfully signed up</p></br>
                    <p>Click <a href="{settings.DOMAIN_URL}/api/v1/user/verify_safe_url/{safe_url}">here</a> to verify your account</p>
                    </>
                """
        message = create_message(
            recipients=[new_user.email],
            subject='Activation Link',
            body=html
        )
        # background_tasks.add_task(mail.send_message, message)
        ############################

        session.add(new_user)
        await session.commit()
        return new_user

    async def update_user_data(self, user_uid: str, user_data: dict, session: AsyncSession):
        user_to_update = await self.get_user_by_uid(user_uid, session)
    

        if user_to_update is not None:
            for k, v in user_data.items():
                setattr(user_to_update, k, v)
            
            await session.commit()

            return user_to_update
        else:
            raise UserNotFound()

    async def update_a_user(self, user_uid: str, user_data: UserUpdateModel, session: AsyncSession):
        user_to_update = await self.get_user_by_uid(user_uid, session)
    
        user_data_dict = user_data.model_dump()
        updated_dict = {k: v for k, v in user_data_dict.items() if v is not None}

        if user_to_update is not None:
            for k, v in updated_dict.items():
                setattr(user_to_update, k, v)
            
            await session.commit()

            return user_to_update
        else:
            raise UserNotFound()

    async def delete_a_user(self, user_uid: str, session: AsyncSession):
        user_to_delete = await self.get_user_by_uid(user_uid, session)

        if user_to_delete is not None:
            await session.delete(user_to_delete)
            await session.commit()
        else:
            raise UserNotFound()
        
class EditorService:
    async def get_editor_by_uid(self, uid: str, session: AsyncSession):
        user = select(User).where((User.uid == uid) & (User.role == UserRole.EDITOR.value))

        result = await session.exec(user)

        if result is None:
            raise EditorNotFound()
        return result.first()

    async def get_editor_by_email(self, email: str, session: AsyncSession):
        user = select(User).where((User.email == email) & (User.role == UserRole.EDITOR.value))

        result = await session.exec(user)

        if result is None:
            raise EditorNotFound()
        return result.first() 
    
    async def get_all_editors(self, session: AsyncSession):
        statement = select(User).where(User.role == UserRole.EDITOR.value).order_by(desc(User.created_at))
        
        result = await session.exec(statement)
        
        if result is None:
            raise EditorNotFound()
        return result.all()
    
    async def create_an_editor(self, user_data: AdminCreateUserModel, background_tasks: BackgroundTasks, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        user_data_dict["password"] = generate_password()
        print(user_data_dict["password"])

        email = user_data_dict["email"]

        if await self.get_editor_by_email(email, session):
            raise EditorAlreadyExists()
        
        new_user = User(
            **user_data_dict
        )
        new_user.password = generate_passwd_hash(new_user.password)
        new_user.role = UserRole.EDITOR.value

        #######################
        safe_url = create_safe_url( str(new_user.uid), new_user.email)

        html = f"""<>
                    <h1>Welcome to the App</h1></br>
                    <p>Congratulations, you have successfully signed up</p></br>
                    <p>Click <a href="{settings.DOMAIN_URL}/api/v1/user/verify_safe_url/{safe_url}">here</a> to verify your account</p>
                    </>
                """
        message = create_message(
            recipients=[new_user.email],
            subject='Activation Link',
            body=html
        )
        # background_tasks.add_task(mail.send_message, message)
        ############################

        session.add(new_user)
        await session.commit()
        return new_user

    async def update_a_editor(self, user_uid: str, user_data: UserUpdateModel, session: AsyncSession):
        user_to_update = await self.get_editor_by_uid(user_uid, session)
    
        user_data_dict = user_data.model_dump()
        updated_dict = {k: v for k, v in user_data_dict.items() if v is not None}

        if user_to_update is not None:
            for k, v in updated_dict.items():
                setattr(user_to_update, k, v)
            
            await session.commit()

            return user_to_update
        else:
            raise UserNotFound()

    async def delete_a_editor(self, user_uid: str, session: AsyncSession):
        user_to_delete = await self.get_editor_by_uid(user_uid, session)

        if user_to_delete is not None:
            await session.delete(user_to_delete)
            await session.commit()

            return {"message": "Editor deleted"}
        else:
            raise EditorNotFound()
        
class AdminService:
    async def get_admin_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where((User.email == email) & (User.role == UserRole.ADMIN.value))
        result = await session.exec(statement)

        if result is None:
            raise AdminNotFound()
        return result.first()

    async def get_super_user_by_email(self, session: AsyncSession):
        statement = select(User).where((User.email == settings.SUPER_ADMIN_EMAIL) & (User.role == UserRole.ADMIN.value))
        result = await session.exec(statement)

        if result is None:
            raise AdminNotFound()
        return result.first()
    
    async def get_admin_by_uid(self, uid: str, session: AsyncSession):
        statement = select(User).where((User.uid == uid) & (User.role == UserRole.ADMIN.value))
        result = await session.exec(statement)

        if result is None:
            raise AdminNotFound()
        return result.first()
        
    async def get_all_admins(self, session: AsyncSession):
        statement = select(User).where(User.role == UserRole.ADMIN.value).order_by(desc(User.created_at))
        result = await session.exec(statement)

        if result is None:
            raise AdminNotFound()
        return result.all()

    async def create_super_admin(self, background_tasks: BackgroundTasks, session: AsyncSession):
        admin_data = {
            "email": settings.SUPER_ADMIN_EMAIL,
            "password": generate_passwd_hash(settings.SUPER_ADMIN_PASSWORD),
            "first_name": settings.SUPER_ADMIN_FIRSTNAME,
            "last_name": settings.SUPER_ADMIN_LASTNAME,
            "phone_number": settings.SUPER_ADMIN_PHONE_NUMBER,
        }

        html = f"""<body>
                    <h1>Welcome to Resultify</h1></br>
                    <p>First Name: {settings.SUPER_ADMIN_FIRSTNAME}</p>
                    <p>Last Name: {settings.SUPER_ADMIN_LASTNAME}</p>
                    <p>Email: {settings.SUPER_ADMIN_EMAIL}</p>
                    <p>Password: {settings.SUPER_ADMIN_PASSWORD}</p>
                </body>"""

        message = create_message(
            recipients=[settings.SUPER_ADMIN_EMAIL],
            subject='Resultify Super Admin Details',
            body=html
        )

        email_check = await self.get_super_user_by_email(session)

        if email_check is None:
            new_admin = User(**admin_data)
            new_admin.role = UserRole.ADMIN.value

            background_tasks.add_task(mail.send_message, message)
            
            session.add(new_admin)
            await session.commit()

            return {"message": "Super Admin Created"}
        raise AdminAlreadyExists()

    async def create_an_admin(self, admin_data: AdminCreateModel, session: AsyncSession):
        admin_data_dict = admin_data.model_dump()
        email = admin_data_dict["email"]

        if await self.get_admin_by_email(email, session):
            raise AdminAlreadyExists()
        
        new_admin = User(**admin_data_dict)
        new_admin.password = generate_passwd_hash(new_admin.password)
        new_admin.role = UserRole.ADMIN.value

        session.add(new_admin)
        await session.commit()

        return new_admin
        
    async def update_an_admin(self, admin_uid: str, admin_data: AdminUpdateModel, session: AsyncSession):
        admin_to_update = await self.get_admin_by_uid(admin_uid, session)

        admin_data_dict = admin_data.model_dump()
        updated_dict = {k: v for k, v in admin_data_dict.items() if v is not None}

        if admin_to_update:
            for k, v in updated_dict.items():
                setattr(admin_to_update, k, v)
            await session.commit()
            return admin_to_update
        raise AdminNotFound()

    async def delete_an_admin(self, admin_uid: str, session: AsyncSession):
        admin_to_delete = await self.get_admin_by_uid(admin_uid, session)
        if admin_to_delete:
            await session.delete(admin_to_delete)
            await session.commit()
        else:
            raise AdminNotFound()
        
class CourseService:
    async def get_course_by_uid(self, course_uid: str, session: AsyncSession):
        statement = select(Course).where(Course.uid == course_uid)

        result = await session.exec(statement)

        if result is None:
            raise CourseNotFound()
        return result.first()

    async def get_all_courses(self, session: AsyncSession):
        statement = select(Course).order_by(Course.created_at)

        result = await session.exec(statement)

        if result is None:
            raise CourseNotFound()
        return result.all()

    async def get_all_user_courses(self, user_uid:str, session: AsyncSession):
        statement = select(Course).where(Course.user_uid == user_uid).order_by(Course.created_at)

        result = await session.exec(statement)

        if result is None:
            raise CourseNotFound()
        return result.all()

    async def create_course(self, user_uid: str, course_data: CourseCreateModel, session: AsyncSession):
        course_data_dict = course_data.model_dump()

        tags = course_data_dict.get('tags')

        course_data_dict.pop('tags', None)

        new_course = Course(
            **course_data_dict,
            user_uid=user_uid
        )
        session.add(new_course)

        await CourseTagService().add_tags_to_course(new_course.uid, tags, session)

        await session.commit()

        return new_course

    async def update_a_course(self, course_uid: str, course_data: CourseUpdateModel, session: AsyncSession):
        course_to_update = await self.get_course_by_uid(course_uid, session)

        course_data_dict = course_data.model_dump()
        updated_dict = {k: v for k, v in course_data_dict.items() if v is not None}
        
        if course_to_update:
            for k, v in updated_dict.items():
                setattr(course_to_update, k, v)
            await session.commit()
            return course_to_update
        raise CourseNotFound()

    async def delete_a_course(self, course_uid: str, session: AsyncSession):
        course_to_delete = await self.get_course_by_uid(course_uid, session)
        if course_to_delete:
            await session.delete(course_to_delete)
            await session.commit()

            return {"message": "Course Deleted"}
        else:
            raise CourseNotFound()

class TagService:
    async def get_tag_by_name(self, tag_name: TagModel, session: AsyncSession):
        statement = select(Tag).where(Tag.name == tag_name)

        result = await session.exec(statement)

        if result is None:
            raise TagNotFound()
        return result.first()

    async def get_tag_by_id(self, tag_id: int, session: AsyncSession):
        statement = select(Tag).where(Tag.id == tag_id)

        result = await session.exec(statement)

        if result is None:
            raise TagNotFound()
        else:
            return result.first()

    async def get_all_tags(self, session: AsyncSession):
        statement = select(Tag)

        result = await session.exec(statement)

        if result is None:
            raise TagNotFound()
        return result.all()
    
    async def create_tag(self, tag_name: TagModel, session: AsyncSession):
        tag_check = await self.get_tag_by_name(tag_name, session)

        if tag_check:
            raise TagAlreadyExists()
        
        new_tag = Tag(
            name=tag_name
        )

        session.add(new_tag)
        await session.commit()

        return new_tag
    
    async def update_tag(self, tag_id: int, tag_name: TagModel, session: AsyncSession):
        tag_to_update = await self.get_tag_by_id(tag_id, session)

        if tag_to_update is None:
            raise TagNotFound()
        
        setattr(tag_to_update, "name", tag_name)
        await session.commit()

        return tag_to_update
    
    async def delete_tag(self, tag_id: int, session: AsyncSession):
        tag_check = await self.get_tag_by_id(tag_id, session)

        if tag_check is None:
            raise TagNotFound()
        
        await session.delete(tag_check)
        await session.commit()

class CourseTagService:
    async def get_all_course_tags(self, course_uid: str, session: AsyncSession):
        """This gets all the tags of a course"""
        statement = select(CourseTag).where(CourseTag.course_uid == course_uid)

        result = await session.exec(statement)
        tags = []

        for x in result:
            x_dict = x.model_dump()

            tag = await TagService().get_tag_by_id(x_dict["tag_id"], session)
            tags.append(tag)

        if tags is None:
            raise TagNotFound()
        return tags

    async def get_all_tag_courses(self, tag_id: int, session: AsyncSession):
        """This gets all the courses that has a particular tag"""
        statement = select(CourseTag).where(CourseTag.tag_id == tag_id)

        result = await session.exec(statement)

        courses = []

        for x in result:
            x_dict = x.model_dump()

            course = await CourseService().get_course_by_uid(x_dict["course_uid"], session)
            courses.append(course)
        
        if courses is None:
            raise CourseNotFound()
        return courses

    async def create_course_tag(self, tag_id: int, course_uid: str, session: AsyncSession):
        tag_check = await TagService().get_tag_by_id(tag_id, session)

        if tag_check:
            raise TagAlreadyExists()
        
        new_course_tag = CourseTag(
            course_uid=course_uid,
            tag_id=tag_id
        )

        session.add(new_course_tag)
        await session.commit()

        return new_course_tag

    async def add_tags_to_course(self, course_uid: str, tags: List[str], session: AsyncSession):
        """This adds tags to a course"""
        for tag in tags:
            tag_check = await TagService().get_tag_by_name(tag, session)

            if tag_check is None:
                create_tag = await TagService().create_tag(tag, session)
                tag_check = await TagService().get_tag_by_name(create_tag.name, session)

            tag_id = tag_check.id

            new_course_tag = CourseTag(
                course_uid=course_uid,
                tag_id=tag_id
            )

            session.add(new_course_tag)
            await session.commit()

        return "Course Tags Added"
    
