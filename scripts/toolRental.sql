create table if not exists client (
	login text not null primary key,
  	password text not null,
  	email text not null,
  	requisites text not null,
  	check(login != ''),
  	check(password != md5('')),
  	check(length(requisites) = 20),
  	check(email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$')
);

create table if not exists employee (
	login text not null primary key,
  	password text not null,
  	name text not null,
  	check(login != ''),
  	check(password != md5(''))
);

create table if not exists instrument (
	id serial not null primary key,
	title text not null,
	type text not null,
	manufacturer text not null,
  	hazard_class int null,
  	price money not null default '0.00',
  	pledge money not null default '0.00',
  	status text not null,
  	photo text null,
  	check(title != ''),
  	check(type != ''),
  	check(manufacturer != ''),
  	check(hazard_class in (null, 1, 2, 3, 4)),
  	check(price >= '0.00'),
  	check(pledge >= '0.00'),
  	check(status in ('in use', 'ready for rent', 'need check', 'need repair', 'scrapped'))
);

create table if not exists verification (
	id serial not null primary key,
	time_verification timestamp not null default now(),
	employee text not null,
	instrument serial not null,
	constraint fk_verificationemployee
		foreign key(employee)
			references employee(login),
	constraint fk_verificationinstrument
		foreign key(instrument)
			references instrument(id)
);

create table if not exists contract (
	id serial not null primary key,
  	time_execution timestamp not null default now(),
  	date_rental_end date not null,
  	instrument serial not null,
  	client text not null,
  	check(date_rental_end > now()),
  	constraint fk_clientinstrument
  		foreign key(instrument)
  			references instrument(id),
  	constraint fk_clientcontract
  		foreign key(client)
  			references client(login)
);

create view all_contracts as
select contract.id, time_execution, date_rental_end, type, manufacturer, hazard_class, price, pledge, client.login, client.email
from contract inner join instrument
on contract.instrument = instrument.id
inner join client
on contract.client = client.login;