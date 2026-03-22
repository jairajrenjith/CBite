# CBite – Campus Bite

A full-stack college canteen management system built with Python (Flask) and MongoDB. Students can browse the menu, place orders, and track their order status in real time. Admin staff can manage the entire menu and handle all incoming orders through a secure panel.

---

## About

CBite digitizes the college canteen experience — no queues, no confusion. It replaces the traditional paper-based or verbal ordering system with a clean, professional web interface where students can place orders from any device and receive a token number instantly. The admin panel gives canteen management full control over the menu and all incoming orders, while the staff panel lets counter staff track and advance order statuses in real time.

Built as a college mini project, CBite demonstrates real-world backend design with full CRUD operations using MongoDB and Python Flask.

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | Python 3.x + Flask                              |
| Database   | MongoDB                                         |
| Driver     | PyMongo                                         |
| Frontend   | HTML5 + CSS3 + Vanilla JavaScript               |
| Fonts      | Google Fonts — Playfair Display + Outfit        |
| Images     | Unsplash CDN (no download needed, loads online) |

---

## User Roles

CBite has three roles — Student, Admin, and Staff.

### Student (default, no login required)
- Browse the full menu with food images, prices, and categories
- Filter menu by category: Meals, Snacks, Beverages, Desserts
- Add items to cart and adjust quantities
- Place an order — a unique token number is auto-assigned
- View live order status: Pending / Preparing / Ready for Pickup
- Cancel an order (only allowed if status is still Pending)

### Admin (login required — password protected)
- Secure login via the Staff / Admin Login button (top right of site)
- Add new menu items with name, price, category, image URL, and availability
- Edit existing items — update any field
- Delete menu items permanently
- View all orders in a full table
- Advance order status: Pending → Preparing → Ready
- Force delete any order regardless of its current status

### Staff / Counter Staff (login required — password protected)
- Separate secure login via the same Staff / Admin Login button (select Counter Staff)
- Dedicated Staff tab unlocks after login
- Live summary stats bar showing count of Pending, Preparing, Ready, and Total orders
- View all orders in a table with token number, items, total, and status
- Filter orders by status: All, Pending, Preparing, Ready
- Advance order status with one click: Pending → Preparing → Ready
- Refresh orders live without reloading the page

---

## File Structure

```
cbite/
├── app.py           ← Complete backend: all Flask routes + MongoDB logic + seeding
├── index.html       ← Complete frontend: UI, styles, and all JavaScript
└── requirements.txt ← Python dependencies (3 packages)
```

---

## Database Design (MongoDB — 3 Collections)

### `menu`
```json
{
  "_id": "ObjectId",
  "name": "Masala Dosa",
  "price": 45.0,
  "category": "Snacks",
  "available": true,
  "image": "https://..."
}
```

### `orders`
```json
{
  "_id": "ObjectId",
  "items": [
    {
      "item_id": "ObjectId",
      "name": "Masala Dosa",
      "quantity": 2,
      "price": 45.0,
      "subtotal": 90.0
    }
  ],
  "total_price": 90.0,
  "status": "pending",
  "created_at": "ISODate"
}
```

### `queue`
```json
{
  "_id": "ObjectId",
  "order_id": "ObjectId",
  "token_number": 1,
  "status": "pending"
}
```

---

## API Endpoints

### Menu

| Method   | Endpoint       | Description                                              |
|----------|----------------|----------------------------------------------------------|
| `GET`    | `/menu`        | List items (`?role=admin` shows hidden items too)        |
| `GET`    | `/menu/<id>`   | Get a single menu item by ID                             |
| `POST`   | `/menu`        | Add a new menu item                                      |
| `PUT`    | `/menu/<id>`   | Update item — name, price, category, image, availability |
| `DELETE` | `/menu/<id>`   | Permanently delete a menu item                           |

### Orders

| Method   | Endpoint                | Description                                         |
|----------|-------------------------|-----------------------------------------------------|
| `POST`   | `/order`                | Place a new order (auto-calculates total + token)   |
| `GET`    | `/orders`               | List all orders (filter with `?status=pending` etc) |
| `GET`    | `/order/<id>`           | Get a single order with its token number            |
| `PUT`    | `/order/<id>/status`    | Advance status: pending → preparing → ready         |
| `DELETE` | `/order/<id>`           | Cancel order (only if status is pending)            |
| `DELETE` | `/order/<id>?force=1`   | Force delete any order regardless of status         |
| `GET`    | `/queue`                | View full token queue sorted by token number        |

### Auth

| Method | Endpoint        | Description                           |
|--------|-----------------|---------------------------------------|
| `POST` | `/admin/login`  | Admin login — returns success/failure |
| `POST` | `/staff/login`  | Staff login — returns success/failure |
| `GET`  | `/health`       | Check server and DB connection status |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running locally

### Step 1 — Set up the project folder

Place all three files in one folder:
```
cbite/
├── app.py
├── index.html
└── requirements.txt
```

### Step 2 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Start MongoDB
```bash
mongod
```

### Step 4 — Run the app
```bash
python app.py
```

On the very first run, 14 sample menu items are automatically seeded into MongoDB. You will see this in the terminal:
```
[CBite] Seeded 14 menu items.
==================================================
  CBite – Campus Bite  |  http://localhost:5000
  Admin password: cadmin2026
  Staff password: cstaff2026
==================================================
```

### Step 5 — Open in browser
```
http://localhost:5000
```

---

## Credentials

| Role          | Password      | Access                                        |
|---------------|---------------|-----------------------------------------------|
| Admin         | `cadmin2026`  | Full menu CRUD + all order management         |
| Counter Staff | `cstaff2026`  | Staff panel — view and advance order statuses |

To log in, click **"Staff / Admin Login"** in the top-right corner, select your role from the dropdown, and enter the password.

---

## Seed Data (Auto-loaded on first run)

14 menu items across 4 categories are inserted automatically:

| Category  | Items                                            |
|-----------|--------------------------------------------------|
| Meals     | Veg Thali, Non-Veg Thali, Egg Rice, Chapati      |
| Snacks    | Masala Dosa, Idli, Samosa, Veg Puff              |
| Beverages | Masala Chai, Cold Coffee, Lassi, Fresh Lime Soda |
| Desserts  | Gulab Jamun, Ice Cream Cup                       |

---

## Business Rules

- Order total is **auto-calculated** at the time of placement
- Item **availability is checked** before adding to an order — unavailable items are rejected
- Token numbers are **auto-incremented** for every new order
- Order status moves **strictly one way**: `pending → preparing → ready`
- Students can only cancel orders that are still `pending`
- Admin can **force delete** any order at any status using `?force=1`
- Menu item names are **case-insensitively unique** — duplicate names are rejected

---

## PyMongo Operations Used

| Operation         | Used For                                        |
|-------------------|-------------------------------------------------|
| `insert_one`      | Add menu item, place order, create queue entry  |
| `insert_many`     | Seed initial 14 menu items on first run         |
| `find_one`        | Fetch item/order by ID, validate before acting  |
| `find`            | List all menu items, orders, queue entries      |
| `update_one`      | Edit menu item fields, advance order status     |
| `delete_one`      | Remove menu item, cancel or delete order        |
| `count_documents` | Check if seed data already exists               |
| `create_index`    | Indexes on status, created_at, token_number     |

---

## MongoDB Indexes

```python
db["orders"].create_index([("status",      ASCENDING)])
db["orders"].create_index([("created_at",  DESCENDING)])
db["menu"].create_index([("category",      ASCENDING)])
db["queue"].create_index([("token_number", ASCENDING)], unique=True)
```

---

## License

Built for educational purposes as a college miniproject.

By Jairaj R.
