number_of_products = 1000
number_of_stores = 200
number_of_customers = 20000
customer_desc_max_size = 5000
number_of_orders = 300000

SQL_TABLES = f"""\
drop table if exists customers;
drop sequence if exists customers_id;
create sequence customers_id start {number_of_customers + 1};
create table customers (
    id int not null default nextval('customers_id') primary key
    , name varchar(150)
    , phone_number varchar(15)
    , address_line varchar(200)
    , zip_code varchar(25)
);

drop table if exists products;
drop sequence if exists products_id;
create sequence products_id start {number_of_products + 1};
create table products (
    id int not null default nextval('products_id') primary key
    , name varchar(150)
    , description varchar ({customer_desc_max_size})
);

drop table if exists stores;
drop sequence if exists stores_id;
create sequence stores_id start {number_of_stores + 1};
create table stores (
    id int not null default nextval('stores_id') primary key
    , name varchar(150)
    , address_line varchar(200)
    , zip_code varchar(25)
);

drop table if exists orders;
drop sequence if exists orders_id;
create sequence orders_id start {number_of_orders + 1};
create table orders (
    id int not null default nextval('orders_id') primary key
    , ordered_by_customer int not null references customers (id)
    , ordered_product int not null references products (id)
    , order_placed_at_store int not null references stores (id)
    , order_timestamp date not null
);

"""

import logging
import random
import sys
import typing as t
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

import ipsum

# def insert_random_product(lines):
#     lines.append()


class Table(t.Protocol):
    def insert_line(self) -> str:
        raise NotImplementedError


@dataclass
class Product:
    id: int
    name: str
    description: str

    def insert_line(self) -> str:
        return f"insert into products (id, name, description) values ({self.id}, '{self.name}', '{self.description}');"


@dataclass
class Store:
    id: int
    name: str
    address_line: str
    zip_code: str

    def insert_line(self) -> str:
        return f"insert into stores (id, name, address_line, zip_code) values ({self.id}, '{self.name}', '{self.address_line}', '{self.zip_code}');"


@dataclass
class Customer:
    id: int
    name: str
    phone_number: str
    address_line: str
    zip_code: str

    def insert_line(self) -> str:
        return f"insert into customers (id, name, address_line, zip_code) values ({self.id}, '{self.name}', '{self.address_line}', '{self.zip_code}');"


@dataclass
class Order:
    id: int
    ordered_by_customer: int
    ordered_product: int
    order_placed_at_store: int
    order_timestamp: str

    def insert_line(self) -> str:
        return f"insert into customers (id, ordered_by_customer, ordered_product, order_placed_at_store, order_timestamp) values ({self.id}, {self.ordered_by_customer}, {self.ordered_product}, {self.order_placed_at_store}, '{self.order_timestamp}');"


from io import TextIOWrapper


class RandomInfoGenerator:
    def __init__(self, language: str, file: TextIOWrapper) -> None:
        self._logger = logging.getLogger("random_info_generator")
        self._model: ipsum.LanguageModel = ipsum.load_model(language)
        self._file = file

    def set_file(self, file: TextIOWrapper):
        self._file = file

    def get_names(self, desired_number: int, word_length=5) -> list[str]:
        logging.debug(f"Generating {desired_number} names")
        all_words: list[str] = []

        while len(all_words) < desired_number:
            words = self._model.generate_words(15)
            words = list(filter(lambda w: len(w) > word_length, words))
            if not words:
                self._logger.debug(
                    f"No words were longer than {word_length} characters!"
                )
            all_words.extend(words)

        return [word.replace("'", "''").title() for word in all_words]

    def get_a_product_description(self, max_length: int) -> str:
        current_desc = ""
        next_desc = ""

        while len(current_desc + "\n" + next_desc) <= max_length:
            if next_desc:
                current_desc += "\n" + next_desc
            next_desc = self._model.generate_paragraphs(1)[0].replace("'", "''")

        if len(current_desc) > max_length:
            self._logger.warning("Product description is too long! Truncating")
            current_desc = current_desc[:max_length]

        return current_desc

    def get_random_address(self) -> str:
        street_number = f"{random.randint(100, 9999)}"
        street_name = " ".join(
            random.choice(
                [self.get_names(1, 8), self.get_names(2, 5), self.get_names(3, 5)]
            )
        )
        street_type = random.choice(
            [
                "Street",
                "Avenue",
                "Boulevard",
                "Road",
                "Drive",
                "Way",
                "Lane",
                "Place",
                "Terrace",
                "Court",
            ]
        )
        return f"{street_number} {street_name} {street_type}"

    def get_random_zip_code(self) -> str:
        return f"{random.randint(0, 99999):05d}"

    def get_random_phone_number(self) -> str:
        intl_code = "+" + str(random.randint(1, 300))
        lengths = list(range(7, 11))
        random_phone_num_length = random.choice(lengths)
        phone = [str(random.randint(0, 9)) for _ in range(random_phone_num_length)]
        return intl_code + "".join(phone)

    def get_customers(self, desired_count: int) -> list[Customer]:
        customers = []
        for cid, customer in enumerate(self.get_names(desired_count)):
            item = Customer(
                id=cid,
                name=customer,
                phone_number=self.get_random_phone_number(),
                address_line=self.get_random_address(),
                zip_code=self.get_random_zip_code(),
            )
            customers.append(item)
            logging.debug(
                f"Generated 1 customer; total customers = {len(customers)} / {desired_count}"
            )
            self._file.write(item.insert_line())
            self._file.write("\n")
        return customers

    def get_stores(self, desired_count: int) -> list[Customer]:
        stores = []
        for sid, store in enumerate(self.get_names(desired_count)):
            item = Store(
                id=sid,
                name=store,
                address_line=self.get_random_address(),
                zip_code=self.get_random_zip_code(),
            )
            stores.append(item)
            logging.debug(
                f"Generated 1 store; total stores = {len(stores)} / {desired_count}"
            )
            self._file.write(item.insert_line())
            self._file.write("\n")
        return stores

    def get_products(self, desired_count: int, max_desc: int) -> list[Product]:
        products = []
        for pid, product in enumerate(self.get_names(desired_count)):
            item = Product(
                id=pid,
                name=product,
                description=self.get_a_product_description(max_length=max_desc),
            )
            products.append(item)
            logging.debug(
                f"Generated 1 product; total products = {len(products)} / {desired_count}"
            )
            self._file.write(item.insert_line())
            self._file.write("\n")
        return products

    def get_random_timestamp(self) -> str:
        current = datetime.now().replace(microsecond=0)
        random_offset = timedelta(
            weeks=random.randint(-52, 52),
            days=random.randint(-365, 365),
            hours=random.randint(-24, 24),
            minutes=random.randint(-60, 60),
            seconds=random.randint(-60, 60),
        )
        return (current + random_offset).isoformat()

    def get_orders_for_customer(
        self,
        customer: Customer,
        stores: list[Store],
        products: list[Product],
        start_order_id: int,
        max_orders: int,
    ) -> list[Order]:
        orders = []
        for i in range(random.randint(1, max_orders)):
            item = Order(
                id=start_order_id + i,
                ordered_by_customer=customer.id,
                ordered_product=random.choice(products).id,
                order_placed_at_store=random.choice(stores).id,
                order_timestamp=self.get_random_timestamp(),
            )
            orders.append(item)
        return orders

    def get_orders(
        self,
        customers: list[Customer],
        products: list[Product],
        stores: list[Store],
        desired_order_count: int,
    ) -> list[Order]:
        orders = []
        while len(orders) < desired_order_count:
            for customer in customers:
                items = self.get_orders_for_customer(
                    customer, stores, products, len(orders), 100
                )
                if len(orders) + len(items) > desired_order_count:
                    remove_num = -1 * ((len(orders) + len(items)) - desired_order_count)
                    logging.warning(
                        f"Too many orders! Truncating... Removing {-1 * remove_num}"
                    )
                    items = items[:remove_num]
                orders.extend(items)
                logging.debug(
                    f"Generated {len(items)} order(s); total orders = {len(orders)} / {desired_order_count}"
                )

                for order in items:
                    self._file.write(order.insert_line())
                    self._file.write("\n")

                if len(orders) >= desired_order_count:
                    break
        return orders


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level="INFO")

    with open("data/random_data_0_tables.sql", "w") as f:
        f.write(SQL_TABLES)
        f.write("\n")
        f.write("\n")

    with open("data/random_data_1_customers.sql", "w") as f:
        generator = RandomInfoGenerator("en", f)

        logging.info("Generating customers")
        f.write("\n-- CUSTOMER DATA\n")
        customers = generator.get_customers(number_of_customers)
        f.write("\n")

    with open("data/random_data_2_products.sql", "w") as f:
        generator.set_file(f)

        logging.info("Generating products")
        f.write("\n-- PRODUCT DATA\n")
        products = generator.get_products(number_of_customers, customer_desc_max_size)
        f.write("\n")

    with open("data/random_data_3_stores.sql", "w") as f:
        generator.set_file(f)

        logging.info("Generating stores")
        f.write("\n-- STORE DATA\n")
        stores = generator.get_stores(number_of_stores)
        f.write("\n")

    with open("data/random_data_4_orders.sql", "w") as f:
        generator.set_file(f)

        logging.info("Generating orders")
        f.write("\n-- ORDER DATA\n")
        orders = generator.get_orders(customers, products, stores, number_of_orders)
        f.write("\n")

    logging.info("Done writing data to file")
