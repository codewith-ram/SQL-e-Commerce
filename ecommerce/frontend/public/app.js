const API_BASE = ""; // same origin

const state = {
  token: localStorage.getItem("token") || null,
  username: localStorage.getItem("username") || null,
  cartCount: 0,
};

function setAuth(token, username) {
  state.token = token;
  state.username = username;
  if (token) {
    localStorage.setItem("token", token);
    localStorage.setItem("username", username || "");
    document.getElementById("auth-links").style.display = "none";
    document.getElementById("logout-btn").style.display = "inline-block";
    document.getElementById("nav-orders").style.display = "inline-block";
  } else {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    document.getElementById("auth-links").style.display = "inline-block";
    document.getElementById("logout-btn").style.display = "none";
  }
}

function authHeaders() {
  return state.token ? { Authorization: `Bearer ${state.token}` } : {};
}

async function api(path, options = {}) {
  const opts = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...authHeaders(),
    },
  };
  const res = await fetch(`${API_BASE}${path}`, opts);
  if (!res.ok) {
    let detail = "API error";
    try { const data = await res.json(); detail = data.detail || JSON.stringify(data); } catch (e) {}
    throw new Error(detail);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res.text();
}

function render(html) {
  document.getElementById("app-root").innerHTML = html;
}

function updateCartCount(n) {
  state.cartCount = n;
  document.getElementById("cart-count").textContent = n;
}

async function refreshCartCount() {
  if (!state.token) { updateCartCount(0); return; }
  try {
    const data = await api("/cart");
    updateCartCount(data.items.reduce((s, i) => s + i.quantity, 0));
  } catch (e) {
    updateCartCount(0);
  }
}

// Views
async function ProductsView() {
  const products = await api("/products");
  const cards = products.map(p => `
    <div class="card">
      <img src="${p.image_url || "https://picsum.photos/seed/placeholder/400/300"}" alt="${p.name}" />
      <div class="p-3">
        <div style="font-weight:600">${p.name}</div>
        <div class="price">$${p.price.toFixed(2)}</div>
        <div class="row" style="margin-top:10px">
          <button class="btn" onclick="location.hash='#/product/${p.product_id}'">Details</button>
          <button class="btn btn-outline" onclick="addToCart(${p.product_id})">Add to Cart</button>
        </div>
      </div>
    </div>
  `).join("");

  render(`
    <h2>Products</h2>
    <div class="grid">${cards}</div>
  `);
}

async function ProductDetailsView(id) {
  try {
    const p = await api(`/products/${id}`);
    render(`
      <div class="row">
        <div>
          <img src="${p.image_url || "https://picsum.photos/seed/placeholder/800/600"}" alt="${p.name}" style="width:100%;max-width:520px;border-radius:12px;border:1px solid #1f2937" />
        </div>
        <div>
          <h2>${p.name}</h2>
          <div class="price" style="font-size:24px">$${p.price.toFixed(2)}</div>
          <p style="white-space:pre-wrap;line-height:1.6">${p.description || "No description."}</p>
          <div class="row">
            <button class="btn" onclick="addToCart(${p.product_id})">Add to Cart</button>
            <button class="btn btn-outline" onclick="location.hash='#/products'">Back to Products</button>
          </div>
        </div>
      </div>
    `);
  } catch (e) {
    render(`<div class="alert">${e.message}</div>`);
  }
}

async function CartView() {
  if (!state.token) { location.hash = "#/login"; return; }
  try {
    const data = await api("/cart");
    const rows = data.items.map(i => `
      <tr>
        <td>${i.name}</td>
        <td>$${i.price.toFixed(2)}</td>
        <td>${i.quantity}</td>
        <td>$${i.subtotal.toFixed(2)}</td>
      </tr>
    `).join("");
    render(`
      <h2>Your Cart</h2>
      ${data.items.length === 0 ? '<div class="alert">Your cart is empty.</div>' : ''}
      <table class="table">
        <thead><tr><th>Product</th><th>Price</th><th>Qty</th><th>Subtotal</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div class="total">Total: $${data.total.toFixed(2)}</div>
      <div style="margin-top:12px">
        <button class="btn" onclick="placeOrder()" ${data.items.length === 0 ? 'disabled' : ''}>Checkout</button>
      </div>
    `);
  } catch (e) {
    render(`<div class="alert">${e.message}</div>`);
  }
}

async function OrdersView() {
  if (!state.token) { location.hash = "#/login"; return; }
  try {
    const data = await api("/orders");
    const rows = data.orders.map(o => `
      <tr>
        <td>#${o.order_id}</td>
        <td>${o.order_date}</td>
        <td>$${o.total_amount.toFixed(2)}</td>
        <td>${o.status}</td>
      </tr>
    `).join("");
    render(`
      <h2>Your Orders</h2>
      ${data.orders.length === 0 ? '<div class="alert">No past orders yet.</div>' : ''}
      <table class="table">
        <thead><tr><th>Order</th><th>Date</th><th>Total</th><th>Status</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    `);
  } catch (e) {
    render(`<div class="alert">${e.message}</div>`);
  }
}

function LoginView() {
  render(`
    <h2>Login</h2>
    <form id="login-form">
      <label>Username</label>
      <input name="username" required />
      <label>Password</label>
      <input name="password" type="password" required />
      <div style="margin-top:12px"><button class="btn">Login</button></div>
    </form>
    <div style="margin-top:10px">No account? <span class="link" onclick="location.hash='#/register'">Register</span></div>
  `);
  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const data = await api("/login", { method: "POST", body: JSON.stringify({
        username: fd.get("username"), password: fd.get("password")
      })});
      setAuth(data.access_token, fd.get("username"));
      await refreshCartCount();
      location.hash = "#/products";
    } catch (err) { alert(err.message); }
  });
}

function RegisterView() {
  render(`
    <h2>Register</h2>
    <form id="register-form">
      <label>Username</label>
      <input name="username" required />
      <label>Email</label>
      <input name="email" type="email" required />
      <label>Password</label>
      <input name="password" type="password" required />
      <div style="margin-top:12px"><button class="btn">Create Account</button></div>
    </form>
  `);
  document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      await api("/register", { method: "POST", body: JSON.stringify({
        username: fd.get("username"), email: fd.get("email"), password: fd.get("password")
      })});
      alert("Registration successful. Please login.");
      location.hash = "#/login";
    } catch (err) { alert(err.message); }
  });
}

// Actions
async function addToCart(productId) {
  if (!state.token) { location.hash = "#/login"; return; }
  try {
    await api("/cart/add", { method: "POST", body: JSON.stringify({ product_id: productId, quantity: 1 }) });
    await refreshCartCount();
    alert("Added to cart.");
  } catch (e) { alert(e.message); }
}

async function placeOrder() {
  try {
    const res = await api("/order/place", { method: "POST" });
    alert(`Order #${res.order_id} placed!`);
    await refreshCartCount();
    location.hash = "#/orders";
  } catch (e) { alert(e.message); }
}

// Router
async function router() {
  const hash = location.hash || "#/products";
  const parts = hash.slice(2).split("/");
  const route = parts[0];
  const param = parts[1];

  // Toggle auth UI
  if (state.token) {
    document.getElementById("auth-links").style.display = "none";
    document.getElementById("logout-btn").style.display = "inline-block";
  } else {
    document.getElementById("auth-links").style.display = "inline-block";
    document.getElementById("logout-btn").style.display = "none";
    document.getElementById("nav-orders").style.display = "inline-block";
  }

  try {
    if (route === "products" || route === "") return await ProductsView();
    if (route === "product") return await ProductDetailsView(param);
    if (route === "cart") return await CartView();
    if (route === "orders") return await OrdersView();
    if (route === "login") return LoginView();
    if (route === "register") return RegisterView();
    render('<div class="alert">Page not found</div>');
  } catch (e) {
    render(`<div class=\"alert\">${e.message}</div>`);
  }
}

window.addEventListener("hashchange", router);

document.getElementById("logout-btn").addEventListener("click", () => {
  setAuth(null, null);
  updateCartCount(0);
  location.hash = "#/products";
});

// Init
(async function init() {
  setAuth(state.token, state.username);
  await refreshCartCount();
  router();
})();
