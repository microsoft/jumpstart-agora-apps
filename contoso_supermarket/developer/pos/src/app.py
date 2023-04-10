#!/usr/bin/env python
from importlib import import_module
import os
import cv2
from flask import Flask, render_template, Response, request, session, redirect, url_for
from flask_session import Session
import secrets
from sqlConnector import SqlConnector
import psycopg2
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)
#storeid = 1
storeid = os.environ.get('STORE_ID')
dbconfig = {
    "host": os.environ.get('SQL_HOST'),
    "user": os.environ.get('SQL_USERNAME'),
    "password": os.environ.get('SQL_PASSWORD'),
    "database": os.environ.get('SQL_DATABASE')
    #"host": "localhost",
    #"user": "postgres",
    #"password": "admin123",
    #"database": "contoso"
}

conn = psycopg2.connect(**dbconfig)
cursor = conn.cursor()

@app.route('/')
def index():
    """Contoso Supermarket home page."""
    cameras_enabled = True
    if os.environ.get('CAMERAS_ENABLED'):
        cameras_enabled = os.environ.get('CAMERAS_ENABLED') == 'True'
    
    head_title = "Contoso Supermarket"
    if os.environ.get('HEAD_TITLE'):
        head_title = os.environ.get('HEAD_TITLE')

    new_category = False
    if os.environ.get('NEW_CATEGORY'):
        new_category = os.environ.get('NEW_CATEGORY') == 'True'

    query = "SELECT * FROM contoso.products ORDER BY productId"
    productlist = []
    cursor.execute(query)
    for item in cursor.fetchall():
        productlist.append({
        'produtctid': item[0],
        'name': item[1],
        'price': item[2],
        'currentInventory': item[3],
        'photolocation': item[4]
    })
    #cursor.close()

    #return render_template('index2.html' if new_category else 'index.html', head_title = head_title, cameras_enabled = cameras_enabled, productlist=productlist)
    return render_template('index.html', head_title = head_title, cameras_enabled = cameras_enabled, productlist=productlist)

@app.route('/inventory')
def inventory():
    try:
        cur = conn.cursor()
        inventorylist = []
        query = "SELECT * from contoso.products"
        cur.execute(query)
        for item in cur.fetchall():
            inventorylist.append({
                'id': item[0],
                'name': item[1],
                'price': item[2],
                'currentInventory': item[3]
            })
        cur.close()
        #conn.close()
        return render_template('inventory.html', inventorylist=inventorylist)
    except Exception as e:
        return "Error querying items: " + str(e)


@app.route('/update_item', methods=['POST'])
def update_item():

    cur = conn.cursor()
    try:
        # Get item information from request data
        item_id = int(request.form['id'])
        name = request.form['name']
        price = float(request.form['price'])

        # Update item in database  
        cur.execute("UPDATE contoso.products SET Name=%s, price=%s WHERE productId=%s", (name, price, item_id))
        conn.commit()
        #cur.close()

        # Return success message
        return "Item updated successfully."
    except Exception as e:
        # Handle errors
        return "Error updating item: " + str(e)

@app.route('/delete_item', methods=['POST'])
def delete_item():
    try:
        # Get item ID from request data
        item_id = int(request.form['id'])

        # Delete item from database
        cur = conn.cursor()
        cur.execute("DELETE FROM contoso.products WHERE productid=%s", (item_id,))
        conn.commit()
        #cur.close()

        # Return success message
        return "Item deleted successfully."
    except Exception as e:
        # Handle errors
        return "Error deleting item: " + str(e)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Get the product ID and quantity from the form data
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    product_price = request.form['product_price']
    quantity = 1

    # Create a new cart item with the product data and quantity
    item = {
        'id': product_id,
        'quantity': quantity,
        'name': product_name,
        'price': product_price
    }

    # Add the item to the shopping cart session
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(item)

    # Redirect back to the homepage
    return redirect('/')

@app.route('/cart')
def cart():
    # Get the cart data from the session
    summary = {}
    cart = session.get('cart', [])
    for item in cart:
        id = item['id']
        quantity = item['quantity']
        if id in summary:
            summary[id] += quantity
        else:
            summary[id] = quantity
    # print (summary)
    # Render the shopping cart template with the cart data
    return render_template('cart.html', cart=cart)

@app.route('/checkout')
def checkout():

    cur = conn.cursor()
    cart = session.get('cart', [])
    #orderDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    orderDate = datetime.now()
    jsoncart = json.dumps(cart)
    query = "INSERT INTO contoso.Orders (orderDate, orderdetails, storeId) VALUES ('{}', '{}', {}) returning orderId".format(orderDate, jsoncart, storeid)
    cur.execute(query)
    ordernumber = cur.fetchone()[0]
    conn.commit()
    cur.close()
    #cnx.close()
    session.clear()
    return render_template('checkout.html', ordernumber=ordernumber)

@app.route('/addPurchase',methods = ['POST'])
def addPurchase():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json; charset=UTF-8'):
        json = request.get_json()
        sqlDb = SqlConnector()
        successful = sqlDb.addPurchase(json['ProductId'])
        if(successful):
            return "Ok"
        else:
            return "Error processing request"
    else:
        return 'Content-Type not supported!'

@app.route('/video_feed/<feed>')
def video_feed(feed):
    return Response(gen_frames(feed),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames(source):
    """Video streaming frame capture function."""
    baseUrl = "rtsp://localhost:554/media/" 
    if os.environ.get('CAMERAS_BASEURL'):
        baseUrl = str(os.environ['CAMERAS_BASEURL'])

    cap = cv2.VideoCapture(baseUrl + source)  # capture the video from the live feed

    while True:
        # # Capture frame-by-frame. Return boolean(True=frame read correctly. )
        success, frame = cap.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
