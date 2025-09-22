from flask import Flask, request
import asyncpg
import asyncio
from flask import Flask, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "root",
    "host": "34.131.223.3",
    "port": 5432
}
PG_HOST = DB_CONFIG["host"]
PG_DB = DB_CONFIG["dbname"]
PG_USER = DB_CONFIG["user"]
PG_PASSWORD = DB_CONFIG["password"]
 


async def pg_con():
    return await asyncpg.connect(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    

async def save_token(token, orderid):
    conn = await pg_con()
    await conn.execute(
        "UPDATE info SET fmc_token = $1 WHERE orderid = $2",
        token, orderid
    )
    await conn.close()

@app.route('/register-token', methods=['POST'])
def register_token():
    data = request.get_json()
    token = data.get('token')
    orderid = data.get('orderid')
    print(f"Received token: {token[:10]}...{token[-5:]} for orderid {orderid}")
    if token:
        asyncio.run(save_token(token, orderid if orderid else 1))
        return {'status': 'success'}, 200
    return {'status': 'error', 'message': 'No token provided'}, 400
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)