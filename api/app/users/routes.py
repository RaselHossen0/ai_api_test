# app/users/routes.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import User, UserCreate, UserUpdate
from app.dependencies import get_password_hash
from app.database import users_collection
from app.auth.utils import get_current_user, get_user ,get_current_active_user
from bson import ObjectId

router = APIRouter()

@router.post("/create", response_model=User)
async def create_user(user: UserCreate):
    if get_user(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]  # Remove plain password before saving

    # Insert the user and capture the MongoDB _id
    insert_result = users_collection.insert_one(user_dict)
    user_id = str(insert_result.inserted_id)

    # Return user data with id
    return User(**user_dict, id=user_id)



@router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user_data = users_collection.find_one({"_id": user_object_id})
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Map MongoDB _id to id in the User model
    user_data["id"] = str(user_data["_id"])  # Convert _id to string and set it as id
    del user_data["_id"]  # Remove _id to avoid duplication

    return User(**user_data)
# app/users/routes.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas import User, UserCreate
from app.dependencies import get_password_hash
from app.database import users_collection
from app.auth.utils import get_current_user, get_user ,get_current_active_user
from bson import ObjectId

router = APIRouter()

@router.post("/create", response_model=User)
async def create_user(user: UserCreate):
    if get_user(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]  # Remove plain password before saving

    # Insert the user and capture the MongoDB _id
    insert_result = users_collection.insert_one(user_dict)
    user_id = str(insert_result.inserted_id)

    # Return user data with id
    return User(**user_dict, id=user_id)



@router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user_data = users_collection.find_one({"_id": user_object_id})
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Map MongoDB _id to id in the User model
    user_data["id"] = str(user_data["_id"])  # Convert _id to string and set it as id
    del user_data["_id"]  # Remove _id to avoid duplication

    return User(**user_data)
@router.put("/edit/{user_id}", response_model=User)
async def edit_user(user_id: str, user_update: UserUpdate):
    print(user_update)
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Find the user in the database
    user_data = users_collection.find_one({"_id": user_object_id})
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # If the password is provided, hash it before updating
    if user_update.password:
        user_update.password = get_password_hash(user_update.password)

    # Prepare the update data (exclude unset fields from the update)
    update_data = user_update.dict(exclude_unset=True)
    
    # Only remove password if it's not in the update data (this avoids KeyError)
    if 'password' in update_data:
        del update_data['password']

    # Update user details in the database
    result = users_collection.update_one(
        {"_id": user_object_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found for update")

    # Return updated user data
    updated_user = users_collection.find_one({"_id": user_object_id})
    updated_user["id"] = str(updated_user["_id"])  # Convert _id to string
    del updated_user["_id"]  # Remove _id to avoid duplication
    return User(**updated_user)