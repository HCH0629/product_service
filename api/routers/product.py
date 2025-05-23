from fastapi import APIRouter, Depends, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api import models
from api.database import get_db
from api.models import Product


router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)



@router.get("/{code}", response_model=models.ProductResponse)
def read_product(code: str, db: Session = Depends(get_db)):
    # 查找是否有 code 名稱產品
    db_product = db.query(models.Product).filter(models.Product.code == code).first()
    
    # 如果沒有返回 404，Product not found
    if db_product is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Product not found")

    return db_product


@router.post("/", response_model=models.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: models.ProductBase, db: Session = Depends(get_db)):
    db_product_by_code = db.query(models.Product).filter(models.Product.code == product_in.code).first()
    if db_product_by_code:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"success": False, "reason": f"Product with code {product_in.code} already exists"} )
    try:
        new_product = Product(
            name=product_in.name,
            code=product_in.code,
            category=product_in.category,
            unit_price=product_in.unit_price,
            inventory=product_in.inventory,
            size=product_in.size,
            color=product_in.color
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product # FastAPI can often serialize directly if orm_mode=True
    except Exception as e:
        db.rollback()
        # Log the error e
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            content= {"success": False, "reason": f"An error occurred: {str(e)}"})




@router.put("/{code}", response_model=models.ProductResponse)
def update_product(code: str, product_in: models.ProductUpdate, db: Session = Depends(get_db)):
    # 查找是否有 code 名稱產品
    db_product = db.query(models.Product).filter(models.Product.code == code).first()
    
    # 如果沒有返回 404，Product not found
    if db_product is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Product not found")

    update_data = product_in.dict(exclude_unset=True)


    try:
        if "code" in update_data and update_data["code"] != db_product.code:
            existing_product_with_code = db.query(models.Product).filter(models.Product.code == update_data["code"], models.Product.id != code).first()
            if existing_product_with_code:
                return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                    content= {"success": False, "reason": f"Product with code {update_data['code']} already exists"})

        
        for key, value in update_data.items():

            if hasattr(db_product, key):
                setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)
        return db_product
    
    except Exception as e:
        db.rollback()
        # Log the error e
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            content= {"success": False, "reason": f"An error occurred during update: {str(e)}"})
                            



@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(code: str, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.code == code).first()
    if db_product is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Product not found")
    try:
        db.delete(db_product)
        db.commit()
        return None # For 204 No Content, FastAPI expects no return body
    
    except Exception as e:
        db.rollback()
        # Log the error e
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            content= {"success": False, "reason": f"An error occurred during delete: {str(e)}"})
