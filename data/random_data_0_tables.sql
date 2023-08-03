drop table if exists customers;
drop sequence if exists customers_id;
create sequence customers_id start 20001;
create table customers (
    id int not null default nextval('customers_id') primary key
    , name varchar(150)
    , phone_number varchar(15)
    , address_line varchar(200)
    , zip_code varchar(25)
);

drop table if exists products;
drop sequence if exists products_id;
create sequence products_id start 1001;
create table products (
    id int not null default nextval('products_id') primary key
    , name varchar(150)
    , description varchar (5000)
);

drop table if exists stores;
drop sequence if exists stores_id;
create sequence stores_id start 201;
create table stores (
    id int not null default nextval('stores_id') primary key
    , name varchar(150)
    , address_line varchar(200)
    , zip_code varchar(25)
);

drop table if exists orders;
drop sequence if exists orders_id;
create sequence orders_id start 300001;
create table orders (
    id int not null default nextval('orders_id') primary key
    , ordered_by_customer int not null references customers (id)
    , ordered_product int not null references products (id)
    , order_placed_at_store int not null references stores (id)
    , order_timestamp date not null
);



