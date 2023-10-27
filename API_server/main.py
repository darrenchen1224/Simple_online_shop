from flask import Flask, request, jsonify
from flasgger import Swagger
import mysql.connector


# 建立資料庫連線
con = mysql.connector.connect(
    user = "root",
    password = "P@ssw0rd1234",
    host = "localhost",
    database = "shopping_mall_db"
)
print("連線成功")

# 建立 cursor 物件，用來對資料庫下 SQL 指令
cursor = con.cursor()


app = Flask(__name__)
swagger = Swagger(app)  # http://localhost:3000/apidocs

# 新增帳號
@app.route('/user', methods=['POST'])
def create_user():
    """
    新增會員帳號
    ---
    tags:
        - User Management
    parameters:
        - name: data
          in: body
          schema:
            type: object
            properties:
                account:
                    type: string
                password:
                    type: string
                name:
                    type: string
                email:
                    type: string
          required: true
          description: 使用 json 格式，帶入 user 創建帳號需要的資料
    responses:
        201:
            description: User created successfully
        400:
            description: Informations are not complete
        409:
            description: Account has been used

    """
    data = request.get_json()

    # 確認 data 中的欄位是否齊全
    try :
        account = data['account']
        password = data['password']
        name = data['name']
        email = data['email']
    except :
        return jsonify({'message': 'Informations are not complete'}), 400

    # 搜尋資料庫是否已存在此帳號
    cursor.execute("SELECT * FROM users WHERE account=%s", (account,))
    find_user = cursor.fetchone()
     
    # 新增會員至資料庫
    if find_user is None :
        cursor.execute("INSERT INTO users(name,email,account,password) VALUES(%s, %s, %s, %s)", (name ,email ,account ,password))
        con.commit()    # 確定執行，用於新增、更新、刪除資料
        return jsonify({'message': 'User created successfully'}), 201
    
    # 帳號重複
    else :
        return jsonify({'message': 'Account has been used'}), 409


# 刪除帳號
@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id) :
    """
    刪除帳號
    ---
    tags:
        - User Management
    parameters :
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲刪除的會員id
    responses :
        200:
            description: Delete account successfully
        404:
            description: User is not exist

    """
    # 從資料庫中找到對應 account 的資料
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()
    
    # 找不到帳號
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404

    # 刪除帳號
    else :
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        con.commit()
        return jsonify({"message": 'Delete account successfully'}), 200


# 取得會員資料
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """
    取得會員資料
    ---
    tags:
        - User Management
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲取得資料的會員id
    responses:
        200:
            description: Successfully get user profile and return
            schema:
                type: object
                properties:
                    email:
                        type: string
                    name:
                        type: string
        404:
            description: User is not exist
    """
    # 從資料庫中找到對應 account 的資料
    cursor.execute("SELECT name, email FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 找不到帳號
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404
    
    # 從資料庫取得該會員資料
    else :
        profile = {
            "name" : find_user[0],
            "email" : find_user[1]
        }
        return jsonify({'profile': profile}), 200


# 修改會員資料
@app.route('/user/<int:user_id>', methods=['PUT'])
def modify_profile(user_id) :
    """
    修改會員資料
    ---
    tags:
        - User Management
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲修改資料的會員id
        - name: data
          in: body
          required: true
          description: 使用 json 格式，帶入欲修改的資料內容
          schema:
            type: object
            properties:
                name:
                    type: string
                email:
                    type: string
    responses:
        200:
            description: Update profile successfully
        400:
            description: Informations are not complete
        404:
            description: User is not exist
    """
    data = request.get_json()

    # 確認 data 中的欄位是否齊全
    try :
        name = data['name']
        email = data['email']
    except :
        return jsonify({'message': 'Informations are not complete'}), 400

    # 從資料庫中找到對應 user 的資料
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 找不到帳號
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404
    
    # 更新會員資料置資料庫
    else :
        cursor.execute("UPDATE users SET name=%s, email=%s WHERE id = %s", (name, email, user_id))
        con.commit()
        return jsonify({'message': 'Update profile successfully'}), 200


# 帳號登入
@app.route('/user/login', methods=['POST'])
def login() :
    """
    帳號登入
    ---
    tags:
        - User Management
    parameters:
        - name: data
          in: body
          required: true
          description: 使用 json 格式，帶入 User 登入資訊
          schema:
            type: object
            properties:
                account:
                    type: string
                password:
                    type: string
    responses :
        200:
            description: successful logged in and return
            schema:
                type: object
                properties:
                    user_id:
                        type: integer
        400:
            description: Informations are not complete
        401:
            description: Wrong password
        404:
            description: User is not exist
    """
    data = request.get_json()

    # 確認 data 中的欄位是否齊全
    try :
        account = data['account']
        password = data['password']
    except :
        return jsonify({'message': 'Informations are not complete'}), 400

    # 搜尋資料庫是否有此 user
    cursor.execute("SELECT * FROM users WHERE binary account=%s", (account,))
    find_user = cursor.fetchone()

    # 找不到該 user
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404
    
    # 確認密碼是否正確
    else :
        cursor.execute("SELECT id FROM users WHERE binary account=%s and password=%s", (account, password))
        user_validation = cursor.fetchone()
        if user_validation is None :
            return jsonify({'message': 'Wrong password'}), 401
        else :
            user = {
                "user_id" : int(find_user[0])
            }
            return jsonify({'user': user}), 200


# 更改密碼
@app.route('/user/change_password', methods=['POST'])
def change_password():
    """
    更改密碼
    ---
    tags:
        - User Management
    parameters:
        - name: data
          in: body
          required: true
          description: 使用 json 格式，帶入 User 帳號以及欲修改的密碼
          schema:
            type: object
            properties:
                account:
                    type: string
                newpassword:
                    type: string
    responses:
        200:
            description: Update password successfully
        400:
            description: Informations are not complete
        404:
            description: User is not exist
    """
    data = request.get_json()

    # 確認 data 中的欄位是否齊全
    try :
        account = data['account']
        newpassword = data['newpassword']
    except :
        return jsonify({'message': 'Informations are not complete'}), 400

    # 從資料庫中找到對應 account 的資料
    cursor.execute("SELECT * FROM users WHERE account=%s", (account,))
    result = cursor.fetchone()
    
    # 找不到帳號
    if result is None :
        return jsonify({'message': 'User is not exist'}), 404

    # 更該密碼至資料庫
    else :
        cursor.execute("UPDATE users SET password=%s WHERE account=%s", (newpassword ,account))
        con.commit()
        return jsonify({'message': 'Update password successfully'}), 200


# 新增商品
@app.route('/product', methods=['POST'])
def new_product():
    """
    新增商品
    ---
    tags:
        - Product Management
    parameters:
        - name: data
          in: body
          required: true
          description: 使用 json 格式，帶入新增商品所需要的資料
          schema:
            type: object
            properties:
                product_name:
                    type: string
                product_info:
                    type: string
                price:
                    type: integer
    responses:
        201:
            description: Product created successfully
        400:
            description: Informations are not complete
    """
    data = request.get_json()

    # 確認 data 中的欄位是否齊全
    try :
        product_name = data['product_name']
        product_info = data['product_info']
        price = data['price']
    except :
        return jsonify({'message': 'Informations are not complete'}), 400
    
    # 新增商品至資料庫
    cursor.execute("INSERT INTO commodities(product_name,product_info,price) VALUES(%s, %s, %s)", (product_name ,product_info ,price))
    con.commit()    # 確定執行，用於新增、更新、刪除資料
    return jsonify({'message': 'Product created successfully'}), 201
    

# 修改商品資料
@app.route('/product/<int:product_id>', methods=['PUT'])
def modify_product(product_id):
    """
    修改商品資料
    ---
    tags:
        - Product Management
    parameters:
        - name: product_id
          in: path
          type: integer
          required: true
          description: 欲修改資料的商品id
        - name: data
          in: body
          required: true
          description: 使用 json 格式，帶入欲修改的商品資料內容
          schema:
            type: object
            properties:
                product_name:
                    type: string
                product_info:
                    type: string
                price:
                    type: integer
    responses:
        200:
            description: Updated product successfully
        400:
            description: Informations are not complete
        404:
            description: Product is not exist
    """
    data = request.get_json()

    # 確認 data 中的欄位是否齊全
    try :
        product_name = data['product_name']
        product_info = data['product_info']
        price = data['price']
    except :
        return jsonify({'message': 'Informations are not complete'}), 400

     # 搜尋資料庫是否存在此商品
    cursor.execute("SELECT * FROM commodities WHERE id=%s", (product_id,))
    find_product = cursor.fetchone()

    # 找不到該商品
    if find_product is None :
        return jsonify({"message" : "Product is not exist"}), 404
    
    # 更新商品資訊至資料庫
    else :
        cursor.execute("UPDATE commodities SET product_name=%s, product_info=%s, price=%s WHERE id=%s", (product_name, product_info, price, product_id))
        return jsonify({"message" : "Updated product successfully"}), 200


# 取得所有商品資訊
@app.route('/product', methods=['GET'])
def get_products():
    """
    取得所有商品資訊
    ---
    tags:
        - Product Management
    responses :
        200:
            description: Successfully get all products and return
            schema:
                type: object
                properties:
                    id:
                        type: integer
                    product_name:
                        type: string
                    product_info:
                        type: string
                    price:
                        type: integer
    """
    cursor.execute("SELECT id, product_name, product_info, price FROM commodities")
    result = cursor.fetchall()

    # 將內容存成陣列並返回
    products = []
    for i in range(0,len(result)):
        product = {}
        product["id"] = result[i][0]
        product['product_name'] = result[i][1]
        product['product_info'] = result[i][2]
        product['price'] = result[i][3]
        products.append(product)
    return jsonify({"products": products}), 200


# 刪除商品
@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """
    刪除商品
    ---
    tags:
        - Product Management
    parameters:
        - name: product_id
          in: path
          type: integer
          required: true
          description: 欲刪除的商品id
    responses:
        200:
            description: Delete product successfully
        400:
            description: Informations are not complete
        404:
            description: Product is not exist
    """
     # 搜尋資料庫是否存在此商品
    cursor.execute("SELECT * FROM commodities WHERE id=%s", (product_id,))
    find_product = cursor.fetchone()

    # 找不到商品
    if find_product is None :
        return jsonify({'message': 'Product is not exist'}), 404

    # 刪除商品 (購物車內的商品也需要被刪除)
    else :
        cursor.execute("DELETE FROM commodities WHERE id=%s", (product_id,))
        cursor.execute("DELETE FROM shopping_cart WHERE product_id=%s", (product_id,))
        con.commit()
        return jsonify({"message" : "Delete product successfully"}), 200
    

# 將商品加入會員購物車
@app.route("/chart/<int:user_id>/<int:product_id>", methods=["POST"])
def add_to_chart(user_id, product_id) :
    """
    將商品加入會員購物車
    ---
    tags:
        - Shopping Chart
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲加入購物車的會員id
        - name: product_id
          in: path
          type: integer
          required: true
          description: 欲加入購物車的商品id
    responses:
        201:
            description: Add product to chart successfully
        404:
            description: User or product are not exist
        409:
            description: Product is already exist in chart
    """

    # 搜尋資料庫中是否有此 user
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 搜尋資料庫中是否有此 product
    cursor.execute("SELECT id FROM commodities WHERE id=%s", (product_id,))
    find_product = cursor.fetchone()

    # 找不到 user
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404

    # 找不到 product
    elif find_product is None :
        return jsonify({'message': 'Product is not exist'}), 404

    else :
        # 確認購物車是否已存在此商品
        cursor.execute("SELECT user_id, product_id FROM shopping_cart WHERE user_id=%s and product_id=%s", (user_id, product_id))
        result = cursor.fetchone()

        if result is not None :
            return jsonify({'message': 'Product is already exist in chart'}), 409

        else :
            # 將 user_id 及 product_id 加入資料庫
            cursor.execute("INSERT INTO shopping_cart(user_id,product_id) VALUES(%s, %s)", (user_id, product_id))
            con.commit()
            return jsonify({"message" : "Add product to chart successfully"}), 201


# 取得會員的購物車資訊
@app.route("/chart/<int:user_id>", methods=["GET"])
def get_product_form_chart(user_id) :
    """
    取得會員的購物車資訊
    ---
    tags:
        - Shopping Chart
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲取得購物車內容的會員id
    responses:
        200:
            description: get shopping chart successfully
            schema:
                type: object
                properties:
                    id:
                        type: integer
                    product_name:
                        type: string
                    product_info:
                        type: string
                    price:
                        type: integer
        404:
            description: User is not exist
    """
    # 搜尋資料庫中是否有此 user
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 找不到 user
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404

    else :
        # 找到購物車資料表中 user 對應的 product_id 的資料表內容
        cursor.execute("SELECT commodities.id, commodities.product_name, commodities.product_info, commodities.price FROM shopping_cart INNER JOIN commodities ON shopping_cart.product_id=commodities.id WHERE shopping_cart.user_id=%s", (user_id,))
        result = cursor.fetchall()

        # 將內容存成陣列並返回
        products = []
        for i in range(0, len(result)) :
            product = {}
            product["id"] = result[i][0]
            product["product_name"] = result[i][1]
            product["product_info"] = result[i][2]
            product["price"] = result[i][3]
            products.append(product)

        return jsonify({"products": products}), 200


# 刪除會員的某筆購物車商品
@app.route("/chart/<int:user_id>/<int:product_id>", methods=["DELETE"])
def delete_from_chart(user_id, product_id) :
    """
    刪除會員的某筆購物車商品
    ---
    tags:
        - Shopping Chart
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲刪除購物車的會員id
        - name: product_id
          in: path
          type: integer
          required: true
          description: 欲刪除購物車的商品id
    responses:
        200:
            description: Delete product from chart successfully
        404:
            description: User or product are not exist
    """
    # 搜尋資料庫中是否有此 user
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 搜尋資料庫中是否有此 product
    cursor.execute("SELECT id FROM commodities WHERE id=%s", (product_id,))
    find_product = cursor.fetchone()

    # 找不到 user
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404

    # 找不到 product
    elif find_product is None :
        return jsonify({'message': 'Product is not exist'}), 404
    
    # 刪除資料
    else :
        cursor.execute("DELETE FROM shopping_cart WHERE user_id=%s and product_id=%s", (user_id, product_id))
        con.commit()
        return jsonify({"message" : "Delete product from chart successfully"}), 200


# 建立訂單
@app.route("/order_management/<int:user_id>", methods=["POST"])
def buy_product(user_id) :
    """
    建立訂單
    ---
    tags:
        - Order Management
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲新增訂單的會員id
        - name: data
          in: body
          required: true
          description: 使用 json 格式，帶入新增訂單所需要的資料
          schema:
            type: object
            properties:
                product_ids:
                    type: array
                    items:
                        type: integer
                recipient:
                    type: string
                recipient_phone:
                    type: string
                recipient_address:
                    type: string
    responses:
        201:
            description: Create order success
        400:
            description: Informations are not complete or product id is invalid
        404:
            description: User is not exist or product is null
    """
    data = request.get_json()
    
    # 確認 data 中的欄位是否齊全
    try :
        product_ids = []
        product_ids = data["product_ids"]
        recipient = data["recipient"]
        recipient_phone = data["recipient_phone"]
        recipient_address = data["recipient_address"]
    except :
        return jsonify({'message': 'Informations are not complete'}), 400

    # 搜尋資料庫中是否有此 user
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 找不到 user
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404

    # 若 product id 為空
    elif len(product_ids) == 0 :
        return jsonify({'message': "Product is null"}), 404

    else :
        # 搜尋資料庫中是否有這些 product_id
        invalid_product_id = []
        for i in range(0, len(product_ids)) :
            cursor.execute("SELECT id FROM commodities WHERE id=%s", (product_ids[i],))
            find_product = cursor.fetchone()
            if find_product is None :
                invalid_product_id.append(product_ids[i])

        # 將無效的商品 id 返回給前端
        if len(invalid_product_id) != 0 :
            return jsonify({'invalid_product_id': invalid_product_id}), 400

        # 訂單成立
        else :
            # 將 product_id 存成 str
            product_ids = ','.join(str(x) for x in product_ids)
            cursor.execute("INSERT INTO order_management(user_id,product_ids,recipient,recipient_phone,recipient_address) VALUES(%s, %s, %s, %s, %s)", (user_id, product_ids, recipient, recipient_phone, recipient_address))
            con.commit()
            return jsonify({'message' : 'Create order success'}), 201


# 取得會員所有訂單資訊
@app.route('/order_management/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    """
    取得會員所有訂單資訊
    ---
    tags:
        - Order Management
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲取的訂單資訊的會員id
    responses:
        200:
            description: Successfully get orders and return
            schema:
                type: object
                properties:
                    order_number:
                        type: integer
                    product_ids:
                        type: array
                        items:
                            type: object
                            properties:
                                id:
                                    type: integer
                                product_name:
                                    type: string
                                product_info:
                                    type: string
                                price:
                                    type: integer
                    recipient:
                        type: string
                    recipient_phone:
                        type: string
                    recipient_address:
                        type: string
                    transportation_status:
                        type: string
                    order_status:
                        type: string
        404:
            description: User is not exist
    """

    # 搜尋資料庫中是否有此 user
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 找不到 user
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404
    
    # 回傳 order 資訊
    else :
        cursor.execute("SELECT order_number, product_ids, recipient, recipient_phone, recipient_address, transportation_status, order_status FROM order_management WHERE user_id=%s", (user_id,))
        result = cursor.fetchall()

        # 將內容存成陣列並返回
        orders_info = []
        for i in range(0, len(result)):
            order_info = {}
            order_info['order_number'] = result[i][0]
            product_ids = result[i][1]

            # 將 product_ids 分割成 list，並從資料庫找到對應的商品資訊
            product_ids = product_ids.split(',')
            product_ids_info = []
            for i in range(0, len(product_ids)) :
                cursor.execute('SELECT * FROM commodities WHERE id=%s', (product_ids[i],))
                product = cursor.fetchone()
                product_id_info = {}
                product_id_info['id'] = product[0]
                product_id_info['product_name'] = product[1]
                product_id_info['product_info'] = product[2]
                product_id_info['price'] = product[3]
                product_ids_info.append(product_id_info)
            order_info['product_ids'] = product_ids_info

            order_info['recipient'] = result[i][2]
            order_info['recipient_phone'] = result[i][3]
            order_info['recipient_address'] = result[i][4]
            order_info['transportation_status'] = result[i][5]
            order_info['order_status'] = result[i][6]
            orders_info.append(order_info)
        return jsonify({'orders_info' : orders_info }), 200


# 修改訂單物流狀態
@app.route('/order_management/<int:order_number>', methods=['PUT'])
def modify_transportation_status(order_number) :
    """
    修改訂單物流狀態
    ---
    tags:
        - Order Management
    parameters:
        - name: order_number
          in: path
          type: integer
          required: true
          description: 欲修改物流狀態的訂單編號
        - name: data
          in: body
          required: true
          description: 使用 json 格式，帶入欲修改的物流狀態 (運送中/已抵達/取貨完成)
          schema:
            type: object
            properties:
                order_status:
                    type: string
                    enum: ['運送中','已抵達','取貨完成']
    responses:
        200:
            description: Change status successfully
        400:
            description: Informations are not complete
        404:
            description: Order is not exist or request wrong status
    """
    data = request.get_json()
    
    # 確認 data 中的欄位是否齊全
    try :
        order_status = data['order_status']
    except :
        return jsonify({'message': 'Informations are not complete'}), 400

    # 搜尋資料庫中是否有此 order number
    cursor.execute("SELECT * FROM order_management WHERE order_number=%s", (order_number,))
    find_order = cursor.fetchone()

    # 找不到 order number
    if find_order is None :
        return jsonify({'message': 'Order is not exist'}), 404

    # 修改物流進度
    else :
        if order_status == '運送中' :
            cursor.execute("UPDATE order_management SET transportation_status=%s WHERE order_number=%s", (order_status, order_number))
            con.commit()
            return jsonify({'message': 'Change transportation_status status to 運送中'}), 200
        
        elif order_status == '已抵達' :
            cursor.execute("UPDATE order_management SET transportation_status=%s WHERE order_number=%s", (order_status, order_number))
            con.commit()
            return jsonify({'message': 'Change transportation_status status to 已抵達'}), 200
        
        elif order_status == '取貨完成' :
            cursor.execute("UPDATE order_management SET transportation_status=%s, order_status='已完成' WHERE order_number=%s", (order_status, order_number))
            con.commit()
            return jsonify({'message': 'Change transportation_status status to 取貨完成'}), 200
        
        else :
            return jsonify({'message': 'Wrong status'}), 404


# 取得會員所有訂單
@app.route('/order_management/<int:user_id>', methods=['GET'])
def get_shopping_sheet(user_id) :
    """
    取得會員所有訂單
    ---
    tags:
        - Order Management
    parameters:
        - name: user_id
          in: path
          type: integer
          required: true
          description: 欲取得購買紀錄的會員id
    responses:
        200:
            description: Successfully get shopping sheet and return
            schema:
                type: object
                properties:
                    order_number:
                        type: integer
                    user_id:
                        type: integer
                    product_id:
                        type: integer
                    recipient:
                        type: string
                    recipient_phone:
                        type: string
                    recipient_address:
                        type: string
                    transportation_status:
                        type: string
                    order_status:
                        type: string
        404:
            description: User is not exist
    """
    # 搜尋資料庫中是否有此 user
    cursor.execute("SELECT id FROM users WHERE id=%s", (user_id,))
    find_user = cursor.fetchone()

    # 找不到 user
    if find_user is None :
        return jsonify({'message': 'User is not exist'}), 404

    # 取得購買紀錄
    else :
        cursor.execute("SELECT * FROM order_management WHERE user_id=%s", (user_id,))
        result = cursor.fetchall()

        # 將購買紀錄存成陣列並返回
        shopping_sheets = []
        for i in range(0, len(result)) :
            shopping_sheet = {}
            shopping_sheet['order_number'] = result[i][0]
            shopping_sheet['user_id'] = result[i][1]
            shopping_sheet['product_id'] = result[i][2]
            shopping_sheet['recipient'] = result[i][3]
            shopping_sheet['recipient_phone'] = result[i][4]
            shopping_sheet['recipient_address'] = result[i][5]
            shopping_sheet['transportation_status'] = result[i][6]
            shopping_sheet['order_status'] = result[i][7]
            shopping_sheets.append(shopping_sheet)
        return jsonify({'shopping_sheets': shopping_sheets}), 200


app.run(host='0.0.0.0', port=3000, debug=True)
