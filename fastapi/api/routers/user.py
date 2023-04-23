from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    File,
    UploadFile,
    BackgroundTasks,
    Body,
)
from fastapi_pagination import Page, Params, add_pagination, paginate

from sqlalchemy.orm import Session

# load database
from ..database.setup import get_db
from ..database import models, schemas

# load authentication
from ..authentication import oauth2

# load business logic
from ..controller import ctr_user

import os

# build routes
router = APIRouter(
    prefix=os.environ.get("FASTAPI_URL", "/fastapi/v1") + "/user", tags=["User"]
)


##
## User
##
@router.get(
    "s/",
    response_model=Page[schemas.ShowUser],
    dependencies=[Depends(oauth2.check_superuser)],
)
async def get_all_user(
    params: Params = Depends(),
    db: Session = Depends(get_db),
    current_user: schemas.ShowUser = Depends(oauth2.get_current_user),
):
    return paginate(ctr_user.show_all_user(db), params)


@router.get(
    "/", response_model=schemas.ShowUser, dependencies=[Depends(oauth2.check_active)]
)
async def get_user(
    db: Session = Depends(get_db),
    current_user: schemas.ShowUser = Depends(oauth2.get_current_user),
):
    return ctr_user.show_specific_user(current_user.username, db)


@router.post("/", response_model=schemas.CreateUser, status_code=201)
async def singup_user(request: schemas.CreateUser, db: Session = Depends(get_db)):
    return ctr_user.create_user(request, db)


@router.put(
    "/",
    response_model=schemas.EditUserOut,
    status_code=202,
    dependencies=[Depends(oauth2.check_active)],
)
async def edit_user(
    request: schemas.EditUser = Body(exclude_unset=True),
    db: Session = Depends(get_db),
    current_user: schemas.ShowUser = Depends(oauth2.get_current_user),
):
    return ctr_user.edit_user(current_user.username, request, db)


# permission handling superuser!
@router.delete(
    "/", status_code=204, dependencies=[Depends(oauth2.check_superuser)]
)  # , response_model=schemas.SimplyUser)
async def delete_user(
    db: Session = Depends(get_db),
    current_user: schemas.ShowUser = Depends(oauth2.get_current_user),
):
    # as long as response is set to 204
    # we do net get a JSON as return :-( !
    return ctr_user.delete_user(current_user.username, db)
