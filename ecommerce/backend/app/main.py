import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database.db import init_db
from .services import auth as auth_service
from .services import products as products_service
from .services import cart as cart_service
from .services import orders as orders_service
from .schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from .schemas.product import Product
from .schemas.cart import AddToCartRequest, CartResponse
from .schemas.order import OrderResponse
from .schemas.order import OrderHistoryResponse, OrderSummary
from dotenv import load_dotenv

app = FastAPI(title="E-commerce API")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Serve static frontend at /app
FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend" / "public"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="app")


@app.on_event("startup")
async def startup_event():
    load_dotenv()
    init_db()


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "E-commerce API",
        "docs": "/docs",
        "endpoints": [
            "/register",
            "/login",
            "/products",
            "/products/{product_id}",
            "/cart",
            "/cart/add",
            "/order/place",
            "/orders",
        ],
    }


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserOut:
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return UserOut(user_id=user["user_id"], username=user["username"], email=user["email"]) 


# Auth endpoints
@app.post("/register", response_model=UserOut)
async def register(data: RegisterRequest):
    try:
        user_id = auth_service.create_user(data.username, data.email, data.password)
        user = auth_service.get_user_by_id(user_id)
        return UserOut(user_id=user["user_id"], username=user["username"], email=user["email"]) 
    except Exception as e:
        # Likely UNIQUE constraint
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    user = auth_service.authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_service.create_access_token({"sub": user["user_id"], "username": user["username"]})
    return TokenResponse(access_token=token)


# Product endpoints
@app.get("/products", response_model=list[Product])
async def get_products():
    products = products_service.list_products()
    return products


@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = products_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Cart endpoints
@app.post("/cart/add", response_model=CartResponse)
async def add_to_cart(data: AddToCartRequest, user: UserOut = Depends(get_current_user)):
    cart_service.add_to_cart(user.user_id, data.product_id, data.quantity)
    cart = cart_service.get_cart(user.user_id)
    return CartResponse(items=cart["items"], total=cart["total"]) 


@app.get("/cart", response_model=CartResponse)
async def get_cart(user: UserOut = Depends(get_current_user)):
    cart = cart_service.get_cart(user.user_id)
    return CartResponse(items=cart["items"], total=cart["total"]) 


# Order endpoint with transaction
@app.post("/order/place", response_model=OrderResponse)
async def place_order(user: UserOut = Depends(get_current_user)):
    order_id, err = orders_service.place_order(user.user_id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    # Fetch order to return
    from .database.db import get_connection  # quick fetch
    conn = get_connection()
    try:
        cur = conn.execute("SELECT total_amount, status FROM orders WHERE order_id = ?", (order_id,))
        row = cur.fetchone()
        return OrderResponse(order_id=order_id, total_amount=row["total_amount"], status=row["status"]) 
    finally:
        conn.close()


# Order history
@app.get("/orders", response_model=OrderHistoryResponse)
async def list_user_orders(user: UserOut = Depends(get_current_user)):
    orders = orders_service.list_orders(user.user_id)
    summaries = [OrderSummary(**o) for o in orders]
    return OrderHistoryResponse(orders=summaries)
