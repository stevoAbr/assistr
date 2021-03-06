from typing import List, Optional
from fastapi import APIRouter, Body, Path, Depends, HTTPException, status

from app.models.post import PostCreate, PostInDB, PostPublic, PostUpdate

from app.db.repositories.posts import PostsRepository


# dependencies
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_org_user, get_current_user
from app.api.dependencies.posts import (
    get_post_id_from_path,
    validate_post_modification_permissons,
)
from app.models.user import UserInDB


router = APIRouter()


@router.get(
    "/",
    response_model=List[PostPublic],
    name="posts:list-posts",
    status_code=status.HTTP_200_OK,
)
async def list_all_posts(
    offset: Optional[int] = 0,
    limit: Optional[int] = 3,
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> List[PostPublic]:
    """
    # untested

    Lists all posts made. Takes an ***optional*** offset and limit query parameter.

    # /api/posts/?offset=0&limit=3

    """
    return await posts_repo.list_posts_by_created_at(offset=offset, limit=limit)


@router.post(
    "/",
    response_model=PostPublic,
    name="posts:create-post",
    status_code=status.HTTP_201_CREATED,
)
async def create_new_post(
    new_post: PostCreate = Body(..., embed=True),  # passed in body as 'new_post'
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
    current_user: UserInDB = Depends(get_current_org_user),  # require org user
) -> PostPublic:
    """
    Creates a new post.

    Only an organisation can create a post.

    """
    created_post = await posts_repo.create_post(
        new_post=new_post, requesting_user=current_user
    )

    return created_post

@router.get(
    "/{post_id}/",
    response_model=PostPublic,
    name="posts:get-post-by-id"
)
async def get_post_by_id(
    post: PostInDB = Depends(get_post_id_from_path)
) -> PostPublic:
    return post


@router.put(
    "/{post_id}/",
    response_model=PostPublic,
    name="posts:update-post-by-id",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(validate_post_modification_permissons)], 
)
async def update_post_by_id(
    post: PostInDB = Depends(get_post_id_from_path),  
    post_update: PostUpdate = Body(..., embed=True),  
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> PostPublic:
    """
    Protected route for updating a post. Requires that the current user has valid modify permissions (e.g. is the *owner* of this post)
    """

    post = await posts_repo.update_post_by_id(post=post, post_update=post_update)

    return post


@router.delete(
    "/{post_id}/",
    response_model=int,
    name="posts:delete-post-by-id",
    dependencies=[Depends(validate_post_modification_permissons)],
)
async def delete_post_by_id(
    post: PostInDB = Depends(get_post_id_from_path),
    posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> int:
    """
    Protected route for deleting a post. Only the org that owns it may delete it.

    user auth handled by posts dependency
    """

    deleted_post = await posts_repo.delete_post(post=post)

    return deleted_post