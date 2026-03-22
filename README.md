# CBite – Campus Bite

A full-stack college canteen management system built with Python (Flask) and MongoDB. Students can browse the menu, place orders, and track order status live. Admin staff can manage the menu and update order statuses through a dedicated panel.

---

## About

CBite digitizes the college canteen experience — no queues, no confusion. It replaces the traditional paper-based or verbal ordering system with a clean web interface where students can place orders from any device and get a token number instantly. The admin panel gives canteen staff full control over the menu and all incoming orders.

This project demonstrates real-world backend design with full CRUD operations using MongoDB and Python, making it suitable as a college mini project.

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.x + Flask                |
| Database  | MongoDB                           |
| Driver    | PyMongo                           |
| Frontend  | HTML + CSS + Vanilla JavaScript   |
| Fonts     | Google Fonts (Playfair Display, Outfit) |
| Images    | Unsplash (CDN, no download needed) |

---

## Features

### Student
- Browse full menu with food images, prices, and categories
- Filter menu by category (Meals, Snacks, Beverages, Desserts)
- Add items to cart, adjust quantities
- Place order — auto token number assigned
- Track live order status (Pending / Preparing / Ready)
- Cancel order (only if still Pending)

### Admin (password protected)
- Secure login with password
- Add new menu items with image, price, category
- Edit existing items (name, price, availability, image)
- Delete menu items
- View all orders in a table
- Advance order status: Pending → Preparing → Ready
- Force delete any order regardless of status

---

## File Structure

```
cbite/
├── app.py          ← Full backend (Flask routes + MongoDB logic)
├── index.html      ← Complete frontend UI
└── requirements.txt
```

---

## Database Design (MongoDB)

### `menu` collection
```json
{
  "_id": ObjectId,
  "name": "Masala Dosa",
  "price": 45.0,
  "category": "Snacks",
  "available": true,
  "image": "https://..."
}
```

### `orders` collection
```json
{
  "_id": ObjectId,
  "items": [
    {
      "item_id": ObjectId,
      "name": "Masala Dosa",
      "quantity": 2,
      "price": 45.0,
      "subtotal": 90.0
    }
  ],
  "total_price": 90.0,
  "status": "pending",
  "created_at": ISODate
}
```

### `queue` collection
```json
{
  "_id": ObjectId,
  "order_id": ObjectId,
  "token_number": 1,
  "status": "pending"
}
```

---

## API Endpoints

### Menu

| Method   | Endpoint        | Description                          |
|----------|----------------|--------------------------------------|
| `GET`    | `/menu`         | List items (student: available only; admin: all) |
| `GET`    | `/menu/<id>`    | Get single item                      |
| `POST`   | `/menu`         | Add new item                         |
| `PUT`    | `/menu/<id>`    | Update item (price, name, availability, image) |
| `DELETE` | `/menu/<id>`    | Delete item                          |

### Orders

| Method   | Endpoint                  | Description                          |
|----------|--------------------------|--------------------------------------|
| `POST`   | `/order`                  | Place a new order                    |
| `GET`    | `/orders`                 | List all orders (filter by `?status=`) |
| `GET`    | `/order/<id>`             | Get single order with token info     |
| `PUT`    | `/order/<id>/status`      | Advance status (pending→preparing→ready) |
| `DELETE` | `/order/<id>`             | Cancel order (pending only)          |
| `DELETE` | `/order/<id>?force=1`     | Force delete any order (admin)       |
| `GET`    | `/queue`                  | View full token queue                |

### Auth

| Method | Endpoint        | Description        |
|--------|-----------------|--------------------|
| `POST` | `/admin/login`  | Admin login        |
| `GET`  | `/health`       | Server health check |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running locally

### Step 1 — Clone or download the project
Place all three files in one folder:
```
cbite/
├── app.py
├── index.html
└── requirements.txt
```

### Step 2 — Install dependencies
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
On first run, 14 sample menu items are seeded automatically into MongoDB.

### Step 5 — Open in browser
```
http://localhost:5000
```

---

## Credentials

| Role  | Password      |
|-------|---------------|
| Admin | `cadmin2026`  |

Click **"Admin Login"** in the top-right corner of the site to access the admin panel.

---

## Business Rules

- Total price is **auto-calculated** during order creation
- Item **availability is validated** before adding to order
- Token numbers are **auto-incremented** per order
- Order status flow is **strictly one-way**: `pending → preparing → ready`
- Students can only cancel orders that are still `pending`
- Admin can force-delete any order regardless of status
- Duplicate menu item names are rejected

## PyMongo Operations Used

| Operation      | Usage                                      |
|----------------|--------------------------------------------|
| `insert_one`   | Add menu item, place order, create token   |
| `insert_many`  | Seed initial menu data                     |
| `find_one`     | Fetch item/order by ID, validate existence |
| `find`         | List menu, orders, queue                   |
| `update_one`   | Edit menu item, advance order status       |
| `delete_one`   | Remove menu item, cancel/delete order      |
| `create_index` | Indexes on status, created_at, token_number |

---

## Screenshots

> Home page with live stats, featured items with food images, hero section.
> Menu page with category filters and Add to Cart controls.
> Cart modal with quantity controls and total.
> Order confirmed modal showing token number.
> Admin panel with full menu table (edit/delete) and orders table (advance/delete).

---

## License

This project is built for educational purposes as a college mini project.
