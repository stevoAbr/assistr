from typing import Optional
from app.models.profile import ProfileCreate
from databases import Database

# app
from pydantic import EmailStr
from fastapi import HTTPException, status

# repositories
from app.db.repositories.base import BaseRepository
from app.db.repositories.profiles import ProfilesRepository

# auth
from app.services import auth_service

# from app.db.repositoris.profiles import ProfilesRepository

# models
from app.models.user import UserCreate, UserInDB, UserPasswordUpdate, UserPublic

CREATE_USER_QUERY = """
    INSERT INTO users (email,salt, password)
    VALUES (:email,:salt,:password)
    RETURNING id, profile_id, email, is_org, salt, password, created_at, updated_at;
"""

# enables creation of an organisation (functionally setting is_org flag to true and creating a org_profile)
CREATE_ORG_QUERY = """
    INSERT INTO users (email,salt, password, is_org)
    VALUES (:email, :salt, :password,:is_org)
    RETURNING id, profile_id, email, is_org, salt, password, created_at,
    updated_at;
"""

# don't use select *. bad.
GET_USER_BY_EMAIL_QUERY = """
    SELECT id, email, is_org, salt, password, created_at, updated_at
    FROM users
    WHERE email = :email;
"""


class UsersRepository(BaseRepository):
    """
    All database actions associated with Users
    """

    # when we init we want to ensure that the auth service is available to the repository --> we're going to be doing auth things
    def __init__(self, db: Database) -> None:
        """
        Standard repository intialise + auth_service + profiles_repo available
        """
        super().__init__(db)
        self.auth_service = auth_service
        self.profiles_repo = ProfilesRepository(db)  # see BaseRepositoy

    async def get_user_by_email(self, *, email: EmailStr) -> UserInDB:
        """
        Queries the database for the first matching user with this email.
        """

        # pass values to query
        user = await self.db.fetch_one(
            query=GET_USER_BY_EMAIL_QUERY, values={"email": email}
        )

        # if user, return UserInDB else None
        if user:
            user = UserInDB(**user)

            # perform any other modifications on returning inDB model here TODO
            # e.g. masking password/hash/private details
        return user

    async def create_user(self, *, new_user: UserCreate) -> UserInDB:
        """
        Creates a user.
        """

        # unique constraints exist on email -> confirm is not taken
        existing_user = await self.get_user_by_email(email=new_user.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That email is alredy taken. Login or try another.",
            )

        # UserPasswordUpdate model with password and salt using auth service
        hashed_pw = self.auth_service.salt_and_hash_pw(
            plaintext_password=new_user.password
        )

        # copy and replace in the UserCreate model
        new_user_hashed_pw = new_user.copy(update=hashed_pw.dict())

        # create user in database
        query_vals = new_user_hashed_pw.dict()
        created_user = await self.db.fetch_one(
            query=CREATE_USER_QUERY, values=query_vals
        )

        # create profile for the user (user_id + empty row)
        await self.profiles_repo.create_profile_for_user(
            profile_create=ProfileCreate(user_id=created_user["id"])
        )

        # attach profile to public user by pulling out from db
        populated_user = await self.populate_user(user=UserInDB(**created_user))

        return populated_user

    async def authenticate_user(
        self, *, email: EmailStr, password: str
    ) -> Optional[UserInDB]:
        """
        Authenticate supplied email + pass matches a user in database. Return None if not valid/DNE.
        """

        # check for existence using email
        user_in_db = await self.get_user_by_email(email=email)

        if not user_in_db:
            return None

        # user exists verify pass
        if not self.auth_service.verify_password(
            password=password, salt=user_in_db.salt, hashed_pw=user_in_db.password
        ):
            return None

        return user_in_db

    async def populate_user(self, *, user: UserInDB) -> UserInDB:
        """
        Takes a user and then appends profile details and returns the model.
        """

        pub_user = UserPublic(
            **user.dict(),
            # fetch and attach profile as well
            profile=await self.profiles_repo.get_profile_by_user_id(user_id=user.id),
        )

        return pub_user

    async def create_org(self, *, new_user: UserCreate) -> UserInDB:
        """
        This function exists to create an organisation --> functionally the same as create_user but overrides is_org as true.
        """
        # unique constraints exist on email -> confirm is not taken
        existing_user = await self.get_user_by_email(email=new_user.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="That email is already taken. Login or try another.",
            )

        # UserPasswordUpdate model with password and salt using auth service
        hashed_pw = self.auth_service.salt_and_hash_pw(
            plaintext_password=new_user.password
        )

        # copy and replace in the UserCreate model
        new_user_hashed_pw = new_user.copy(update=hashed_pw.dict())

        # create ORG in database
        query_vals = new_user_hashed_pw.copy(update={"is_org": True})
        created_user = await self.db.fetch_one(
            query=CREATE_ORG_QUERY, values=query_vals.dict()
        )

        # create profile for the user (user_id + empty row)
        await self.profiles_repo.create_profile_for_user(
            profile_create=ProfileCreate(user_id=created_user["id"])
        )

        # attach profile to public user by pulling out from db
        populated_user = await self.populate_user(user=UserInDB(**created_user))

        return populated_user
