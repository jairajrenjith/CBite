from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import os

MONGO_URI      = "mongodb://localhost:27017/"
DB_NAME        = "cbite_db"
ADMIN_PASSWORD = "cadmin2026"
STAFF_PASSWORD = "cstaff2026"

app = Flask(__name__, template_folder=".")
CORS(app)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db     = client[DB_NAME]

db["orders"].create_index([("status",      ASCENDING)])
db["orders"].create_index([("created_at",  DESCENDING)])
db["menu"].create_index([("category",      ASCENDING)])
db["queue"].create_index([("token_number", ASCENDING)], unique=True)

STATUS_FLOW = {"pending": "preparing", "preparing": "ready", "ready": None}

def oid(raw):
    try:    return ObjectId(raw)
    except: return None

def ser(doc):
    doc["_id"] = str(doc["_id"])
    if "order_id" in doc:
        doc["order_id"] = str(doc["order_id"])
    for it in doc.get("items", []):
        if isinstance(it.get("item_id"), ObjectId):
            it["item_id"] = str(it["item_id"])
    return doc

def next_token():
    last = db["queue"].find_one(sort=[("token_number", -1)])
    return (last["token_number"] + 1) if last else 1

def ok(data=None, msg="", code=200, **kw):
    r = {"success": True}
    if msg:   r["message"] = msg
    if data is not None: r["data"] = data
    r.update(kw)
    return jsonify(r), code

def err(msg, code=400):
    return jsonify({"success": False, "error": msg}), code

SEED_MENU = [
    {"name": "Veg Thali",          "price": 60.0,  "category": "Meals",     "available": True,
     "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80"},
    {"name": "Non-Veg Thali",      "price": 80.0,  "category": "Meals",     "available": True,
     "image": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80"},
    {"name": "Egg Rice",           "price": 50.0,  "category": "Meals",     "available": True,
     "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=400&q=80"},
    {"name": "Chapati (3 pcs)",    "price": 30.0,  "category": "Meals",     "available": True,
     "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80"},
    {"name": "Masala Dosa",        "price": 45.0,  "category": "Snacks",    "available": True,
     "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=400&q=80"},
    {"name": "Idli (3 pcs)",       "price": 25.0,  "category": "Snacks",    "available": True,
     "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=400&q=80"},
    {"name": "Samosa (2 pcs)",     "price": 20.0,  "category": "Snacks",    "available": True,
     "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80"},
    {"name": "Veg Puff",           "price": 15.0,  "category": "Snacks",    "available": True,
     "image": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&q=80"},
    {"name": "Masala Chai",        "price": 10.0,  "category": "Beverages", "available": True,
     "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80"},
    {"name": "Cold Coffee",        "price": 30.0,  "category": "Beverages", "available": True,
     "image": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&q=80"},
    {"name": "Lassi",              "price": 25.0,  "category": "Beverages", "available": True,
     "image": "https://images.unsplash.com/photo-1571091718767-18b5b1457add?w=400&q=80"},
    {"name": "Fresh Lime Soda",    "price": 20.0,  "category": "Beverages", "available": False,
     "image": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400&q=80"},
    {"name": "Gulab Jamun (2 pcs)","price": 20.0,  "category": "Desserts",  "available": True,
     "image": "https://images.unsplash.com/photo-1666406420061-65d803a3c8f8?w=400&q=80"},
    {"name": "Ice Cream Cup",      "price": 30.0,  "category": "Desserts",  "available": True,
     "image": "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400&q=80"},
]

def seed():
    if db["menu"].count_documents({}) == 0:
        db["menu"].insert_many(SEED_MENU)
        print("[CBite] Seeded 14 menu items.")

@app.route("/menu", methods=["GET"])
def get_menu():
    role     = request.args.get("role", "student")
    category = request.args.get("category")
    query    = {} if role == "admin" else {"available": True}
    if category:
        query["category"] = category
    items = [ser(d) for d in db["menu"].find(query)]
    return ok(items, count=len(items))

@app.route("/menu/<item_id>", methods=["GET"])
def get_menu_item(item_id):
    o = oid(item_id)
    if not o: return err("Invalid ID")
    doc = db["menu"].find_one({"_id": o})
    if not doc: return err("Item not found", 404)
    return ok(ser(doc))

@app.route("/menu", methods=["POST"])
def add_menu_item():
    b        = request.get_json(silent=True) or {}
    name     = (b.get("name") or "").strip()
    category = (b.get("category") or "General").strip()
    image    = b.get("image", "")
    available = bool(b.get("available", True))
    if not name: return err("name is required")
    try:
        price = float(b["price"])
        assert price >= 0
    except:
        return err("price must be a non-negative number")
    if db["menu"].find_one({"name": {"$regex": f"^{name}$", "$options": "i"}}):
        return err(f"'{name}' already exists", 409)
    doc = {"name": name, "price": price, "category": category,
           "available": available, "image": image}
    res = db["menu"].insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return ok(doc, "Item added", 201)

@app.route("/menu/<item_id>", methods=["PUT"])
def update_menu_item(item_id):
    o = oid(item_id)
    if not o: return err("Invalid ID")
    b = request.get_json(silent=True) or {}
    upd = {}
    if "name"      in b: upd["name"]      = b["name"].strip()
    if "category"  in b: upd["category"]  = b["category"].strip()
    if "available" in b: upd["available"] = bool(b["available"])
    if "image"     in b: upd["image"]     = b["image"]
    if "price"     in b:
        try:
            p = float(b["price"]); assert p >= 0; upd["price"] = p
        except:
            return err("price must be a non-negative number")
    if not upd: return err("No valid fields to update")
    res = db["menu"].update_one({"_id": o}, {"$set": upd})
    if res.matched_count == 0: return err("Item not found", 404)
    return ok(ser(db["menu"].find_one({"_id": o})), "Item updated")

@app.route("/menu/<item_id>", methods=["DELETE"])
def delete_menu_item(item_id):
    o = oid(item_id)
    if not o: return err("Invalid ID")
    res = db["menu"].delete_one({"_id": o})
    if res.deleted_count == 0: return err("Item not found", 404)
    return ok(msg="Item deleted")

@app.route("/order", methods=["POST"])
def place_order():
    b         = request.get_json(silent=True) or {}
    raw_items = b.get("items", [])
    if not raw_items: return err("items list required")

    order_items, total, errors = [], 0.0, []
    for entry in raw_items:
        o = oid(entry.get("item_id"))
        if not o: errors.append(f"Invalid item_id: {entry.get('item_id')}"); continue
        try:
            qty = int(entry.get("quantity", 1)); assert qty >= 1
        except:
            errors.append(f"quantity must be >= 1"); continue
        mi = db["menu"].find_one({"_id": o})
        if not mi:             errors.append(f"Item {entry['item_id']} not found"); continue
        if not mi.get("available"): errors.append(f"'{mi['name']}' unavailable"); continue
        sub = mi["price"] * qty
        total += sub
        order_items.append({"item_id": o, "name": mi["name"],
                             "quantity": qty, "price": mi["price"],
                             "subtotal": round(sub, 2)})
    if errors: return jsonify({"success": False, "errors": errors}), 400
    if not order_items: return err("No valid items")

    doc = {"items": order_items, "total_price": round(total, 2),
           "status": "pending", "created_at": datetime.now(timezone.utc)}
    ores  = db["orders"].insert_one(doc)
    token = next_token()
    db["queue"].insert_one({"order_id": ores.inserted_id,
                             "token_number": token, "status": "pending"})
    resp = ser(doc)
    resp["token_number"] = token
    return ok(resp, "Order placed!", 201)

@app.route("/orders", methods=["GET"])
def get_orders():
    status = request.args.get("status")
    query  = {}
    if status:
        if status not in STATUS_FLOW: return err(f"Invalid status. Use: {list(STATUS_FLOW)}")
        query["status"] = status
    orders    = list(db["orders"].find(query, sort=[("created_at", -1)]))
    order_ids = [o["_id"] for o in orders]
    tokens    = {q["order_id"]: q["token_number"]
                 for q in db["queue"].find({"order_id": {"$in": order_ids}})}
    result = []
    for o in orders:
        s = ser(o)
        s["token_number"] = tokens.get(ObjectId(s["_id"]))
        result.append(s)
    return ok(result, count=len(result))

@app.route("/order/<order_id>", methods=["GET"])
def get_order(order_id):
    o = oid(order_id)
    if not o: return err("Invalid ID")
    doc = db["orders"].find_one({"_id": o})
    if not doc: return err("Order not found", 404)
    qe  = db["queue"].find_one({"order_id": o})
    s   = ser(doc)
    s["token_number"] = qe["token_number"] if qe else None
    return ok(s)

@app.route("/order/<order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    o = oid(order_id)
    if not o: return err("Invalid ID")
    doc = db["orders"].find_one({"_id": o})
    if not doc: return err("Order not found", 404)
    cur  = doc["status"]
    nxt  = STATUS_FLOW.get(cur)
    if nxt is None: return err(f"Order is already '{cur}' (terminal)")
    db["orders"].update_one({"_id": o}, {"$set": {"status": nxt}})
    db["queue"].update_one({"order_id": o}, {"$set": {"status": nxt}})
    return ok({"status": nxt}, f"{cur} -> {nxt}")

@app.route("/order/<order_id>", methods=["DELETE"])
def cancel_order(order_id):
    o = oid(order_id)
    if not o: return err("Invalid ID")
    doc = db["orders"].find_one({"_id": o})
    if not doc: return err("Order not found", 404)
    force = request.args.get("force") == "1"
    if not force and doc["status"] != "pending":
        return err(f"Cannot cancel '{doc['status']}' order. Only 'pending' orders can be cancelled.", 400)
    db["orders"].delete_one({"_id": o})
    db["queue"].delete_one({"order_id": o})
    return ok(msg="Order cancelled")

@app.route("/queue", methods=["GET"])
def get_queue():
    entries = [ser(e) for e in db["queue"].find(sort=[("token_number", 1)])]
    return ok(entries, count=len(entries))

@app.route("/admin/login", methods=["POST"])
def admin_login():
    b = request.get_json(silent=True) or {}
    if b.get("password") == ADMIN_PASSWORD:
        return ok({"role": "admin"}, "Login successful")
    return err("Incorrect password", 401)

@app.route("/staff/login", methods=["POST"])
def staff_login():
    b = request.get_json(silent=True) or {}
    if b.get("password") == STAFF_PASSWORD:
        return ok({"role": "staff"}, "Staff login successful")
    return err("Incorrect staff password", 401)

@app.route("/health")
def health():
    try:
        client.admin.command("ping")
        return ok({"db": "connected"})
    except Exception as e:
        return err(str(e), 500)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    seed()
    print("=" * 52)
    print("  CBite – Campus Bite  |  http://localhost:5000")
    print("  Admin password: cadmin2026")
    print("  Staff password: cstaff2026")
    print("=" * 52)
    app.run(debug=True, port=5000)
