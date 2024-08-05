from typing import Union

import asyncpg

from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result


    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, username, telegram_id, language):
        sql = "INSERT INTO account_telegramuser (username, telegram_id, language) VALUES($1, $2, 'ru') returning *"
        return await self.execute(sql, username, telegram_id, fetchrow=True)
    
    async def update_user_phone(self, phone, telegram_id):
        sql = "UPDATE account_telegramuser SET phone=$1 WHERE telegram_id=$2"
        return await self.execute(sql, phone, telegram_id, execute=True)
    
    async def update_user_address(self, address, lat, long, phone, telegram_id):
        sql = "UPDATE account_telegramuser SET address=$1, latitude=$2, longitude=$3, phone=$4 WHERE telegram_id=$5"
        return await self.execute(sql, address, lat, long, phone, telegram_id, execute=True)
    
    async def update_user_language(self, language, telegram_id):
        sql = "UPDATE account_telegramuser SET language=$1 WHERE telegram_id=$2"
        return await self.execute(sql, language, telegram_id, execute=True)

    async def select_all_users(self):
        sql = "SELECT * FROM account_telegramuser"
        return await self.execute(sql, fetch=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM account_telegramuser WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
    
    async def get_user(self, user_id):
        sql = "SELECT * FROM account_telegramuser WHERE telegram_id = $1;"
        return await self.execute(sql, user_id, fetchrow=True)
    
    async def get_users_telegram_id(self):
        sql = "SELECT telegram_id FROM account_telegramuser;"
        return await self.execute(sql, fetch=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM account_telegramuser"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE account_telegramuser SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)
    
    async def update_user_fullname_birthdate(self, fullname, dob, telegram_id):
        sql = "UPDATE account_telegramuser SET full_name=$1, date_of_birth=$2 WHERE telegram_id=$3"
        return await self.execute(sql, fullname, dob, telegram_id, execute=True)

    async def delete_users(self):
        await self.execute("DELETE FROM account_telegramuser WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE account_telegramuser", execute=True)

    async def get_category(self, cat_id):
        sql = "SELECT * FROM product_category WHERE id = $1;"
        return await self.execute(sql, cat_id, fetchrow=True)
    
    async def get_categories(self):
        sql = "SELECT * FROM product_category WHERE parent_id IS NULL;"
        return await self.execute(sql, fetch=True)
    
    async def get_subcategories(self, cat_id):
        sql = "SELECT * FROM product_category WHERE parent_id = $1"
        return await self.execute(sql, cat_id, fetch=True)

    async def get_products(self, cat_id):
        sql = f"SELECT * FROM product_product WHERE category_id = $1"
        return await self.execute(sql, cat_id, fetch=True)

    async def get_product(self, product_id):
        sql = "SELECT * FROM product_product WHERE id = $1;"
        return await self.execute(sql, product_id, fetchrow=True)
    
    async def get_product_by_id(self, product_id):
        sql = "SELECT * FROM product_product WHERE id = $1"
        return await self.execute(sql, product_id, fetchrow=True)

    async def add_cart(self, buyer, item_id, item_count, current_time):
        sql = "INSERT INTO cart_cart (buyer, item_id, item_count, created) VALUES ($1, $2, $3, $4) returning *"
        return await self.execute(
            sql,
            buyer,
            item_id,
            item_count,
            current_time,
            fetchrow=True,
        )
    
    async def get_cart_item(self, user_id, product_id):
        sql = "SELECT * FROM cart_cart WHERE buyer = $1 AND item_id = $2"
        return await self.execute(sql, user_id, product_id, fetchrow=True)

    async def get_cart_all(self, user_id):
        sql = "SELECT * FROM cart_cart WHERE buyer = $1;"
        return await self.execute(sql, user_id, fetch=True)

    async def drop_cart_item(self, cart_id):
        await self.execute(f"DELETE FROM cart_cart WHERE id = $1", cart_id, execute=True)

    async def drop_all_cart_item(self, user_id):
        await self.execute(f"DELETE FROM cart_cart WHERE buyer = $1", user_id, execute=True)
    
    async def update_cart(self, item_count, user_id, product_id):
        sql = "UPDATE cart_cart SET item_count=$1 WHERE buyer = $2 AND item_id = $3"
        return await self.execute(sql, item_count, user_id, product_id, fetchrow=True)

    async def create_order(self, buyer, phone_number, lang_code, address, latitude, longitude, amount, status, payment_click, is_paid, current_time, delivery_amount, is_pick_up):
        sql = "INSERT INTO order_customorder (buyer, phone_number, lang_code, address, latitude, longitude, amount, status, payment_click, is_paid, created, delivery_amount, is_pick_up) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) RETURNING *"
        return await self.execute(sql, buyer, phone_number, lang_code, address, latitude, longitude, amount, status, payment_click, is_paid, current_time, delivery_amount, is_pick_up, fetchrow=True)

    async def create_order_item(self, order_id, product_id, quantity, price, min_count, measure, org_count_in_measure, org_measure):
        sql = "INSERT INTO order_orderitem (order_id, product_id, quantity, price, min_count, measure, org_count_in_measure, org_measure) VALUES($1, $2, $3, $4, $5, $6, $7, $8) returning *"
        return await self.execute(sql, order_id, product_id, quantity, price, min_count, measure, org_count_in_measure, org_measure, fetchrow=True)
    
    async def get_orders(self, user_id):
        sql = f"SELECT *, COUNT(*) OVER (PARTITION BY buyer) AS total_orders_count FROM order_customorder WHERE buyer=$1 ORDER BY created ASC LIMIT 5;"
        return await self.execute(sql, user_id, fetch=True)
    
    async def get_delivered_or_rejected_orders(self, user_id):
        sql = """SELECT * FROM (SELECT *, COUNT(*) OVER (PARTITION BY buyer) AS total_orders_count 
            FROM order_customorder WHERE buyer=$1 AND (status='delivered' OR status='rejected') 
            ORDER BY id DESC LIMIT 5) AS subquery ORDER BY id ASC
        """
        return await self.execute(sql, user_id, fetch=True)

    async def get_order_only(self, order_id):
        sql = f"SELECT * FROM order_customorder WHERE id=$1 "
        return await self.execute(sql, order_id, fetchrow=True)
    
    async def update_order_status(self, status, order_id):
        sql = "UPDATE order_customorder SET status=$1 WHERE id = $2;"
        return await self.execute(sql, status, order_id, execute=True)
    
    async def update_order_transaction(self, transaction_id, order_id):
        sql = "UPDATE order_customorder SET transaction_id=$1 WHERE id = $2;"
        return await self.execute(sql, transaction_id, order_id, execute=True)
    
    async def update_order_status_and_supplier(self, status, supplier, order_id):
        sql = "UPDATE order_customorder SET status=$1, supplier=$2 WHERE id = $3;"
        return await self.execute(sql, status, supplier, order_id, execute=True)

    async def get_order_items(self, order_id):
        sql = f"SELECT * FROM order_orderitem WHERE order_id=$1"
        return await self.execute(sql, order_id, fetch=True)
    
    async def get_suppliers(self):
        sql = f"SELECT * FROM order_supplier"
        return await self.execute(sql, fetch=True)
    
    async def get_statistics(self, current_year, current_month):
        sql = """
            SELECT COUNT(*) AS item_count, SUM(amount) AS price_all
            FROM products_order
            WHERE EXTRACT(YEAR FROM created) = $1
            AND EXTRACT(MONTH FROM created) = $2
            AND status = 'delivered';
        """
        return await self.execute(sql, current_year, current_month, fetchrow=True)

    async def get_best_seller(self, current_year, current_month):
        sql = """
            SELECT oi.product_id, p.uz, SUM(oi.product_count) AS total_count
            FROM products_orderitem AS oi
            JOIN products_product AS p ON oi.product_id = p.id
            JOIN "products_order" AS o ON oi.order_id = o.id
            WHERE EXTRACT(YEAR FROM o.created) = $1
            AND EXTRACT(MONTH FROM o.created) = $2
            GROUP BY oi.product_id, p.uz
            ORDER BY total_count DESC
            LIMIT 1;
        """
        return await self.execute(sql, current_year, current_month, fetchrow=True)
    
    
    async def create_click_transaction(self, order_id, amount, current_time):
        sql = "INSERT INTO clickpayment_clicktransaction (click_paydoc_id, order_id, amount, status, created, modified, extra_data, message) VALUES('', $1, $2, 'waiting', $3, $3, '', '') RETURNING *"
        return await self.execute(sql, order_id, amount, current_time, fetchrow=True)

    async def get_transaction_only(self, order_id):
        sql = f"SELECT * FROM clickpayment_clicktransaction WHERE order_id=$1"
        return await self.execute(sql, order_id, fetchrow=True)
    
    async def get_fillials(self):
        sql = f"SELECT * FROM main_office"
        return await self.execute(sql, fetch=True)
    
    async def get_fillial_only(self, fillial_id):
        sql = f"SELECT * FROM main_office WHERE id=$1 "
        return await self.execute(sql, fillial_id, fetchrow=True)
    
    async def get_fillial_by_name(self, name):
        sql = f"SELECT * FROM main_office WHERE name=$1 "
        return await self.execute(sql, name, fetchrow=True)