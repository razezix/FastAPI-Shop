from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.categories.create_category import CreateCategoryInput, CreateCategoryUseCase
from src.application.categories.delete_category import DeleteCategoryUseCase
from src.application.categories.list_category import ListCategoriesUseCase
from src.application.categories.update_category import UpdateCategoryInput, UpdateCategoryUseCase
from src.core.exceptions import EntityNotFound
from src.presentation.api.deps import ManagerOrAbove, get_category_repo
from src.presentation.schemas.category import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
)

router = APIRouter(prefix="/categories", tags=["categories"])


def _to_response(c) -> CategoryResponse:
    return CategoryResponse(
        id=c.id,
        name=c.name,
        slug=c.slug,
        description=c.description,
        parent_id=c.parent_id,
        is_active=c.is_active,
        created_at=c.created_at,
    )


@router.get("", response_model=list[CategoryResponse])
async def list_categories(category_repo=Depends(get_category_repo)):
    use_case = ListCategoriesUseCase(category_repo)
    categories = await use_case.execute()
    return [_to_response(c) for c in categories]


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    body: CategoryCreateRequest,
    _: ManagerOrAbove,
    category_repo=Depends(get_category_repo),
):
    try:
        use_case = CreateCategoryUseCase(category_repo)
        category = await use_case.execute(
            CreateCategoryInput(
                name=body.name,
                slug=body.slug,
                description=body.description,
                parent_id=body.parent_id,
            )
        )
        return _to_response(category)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    body: CategoryUpdateRequest,
    _: ManagerOrAbove,
    category_repo=Depends(get_category_repo),
):
    try:
        use_case = UpdateCategoryUseCase(category_repo)
        category = await use_case.execute(
            UpdateCategoryInput(
                category_id=category_id,
                name=body.name,
                slug=body.slug,
                description=body.description,
                parent_id=body.parent_id,
                is_active=body.is_active,
            )
        )
        return _to_response(category)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    _: ManagerOrAbove,
    category_repo=Depends(get_category_repo),
):
    try:
        use_case = DeleteCategoryUseCase(category_repo)
        await use_case.execute(category_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
