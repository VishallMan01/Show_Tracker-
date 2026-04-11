from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schema import ShowCreate, ShowResponse, ShowUpdate

from auth import CurrentUser

router = APIRouter()


@router.get("", response_model=list[ShowResponse])
async def get_shows(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Show)
        .options(selectinload(models.Show.author))
        .order_by(models.Show.date_posted.desc()),
        )
    shows = result.scalars().all()
    return shows


@router.post("", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
async def create_show(show: ShowCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    new_show = models.Show(
        name=show.name,
        watch_status=show.watch_status,
        completeness=show.completeness,
        review=show.review,
        user_id=current_user.id,
    )
    db.add(new_show)
    await db.commit()
    await db.refresh(new_show, attribute_names=["author"])
    return new_show


@router.get("/{show_id}", response_model=ShowResponse)
async def get_show(show_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Show).where(models.Show.id == show_id))
    show = result.scalars().first()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return show


@router.put("/{show_id}", response_model=ShowResponse)
async def update_show_full(show_id: int, show_data:ShowCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Show).where(models.Show.id == show_id))
    show = result.scalars().first()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    

    if show.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this show")
    
    show.name = show_data.name
    show.watch_status = show_data.watch_status
    show.completeness = show_data.completeness
    show.review = show_data.review

    await db.commit()
    await db.refresh(show, attribute_names=["author"])
    return show
        

@router.patch("/{show_id}", response_model=ShowResponse)
async def update_show_partial(show_id: int, show_data:ShowUpdate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Show).where(models.Show.id == show_id))
    show = result.scalars().first()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")

    if show.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this show")

    update_data = show_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(show, field, value)
    
    await db.commit()
    await db.refresh(show, attribute_names=["author"])
    return show


@router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(show_id: int, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Show).where(models.Show.id == show_id))
    show = result.scalars().first()
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")

    if show.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this show")

    await db.delete(show)
    await db.commit()