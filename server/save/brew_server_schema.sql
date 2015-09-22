create table brews(
  name text primary key,
  style text not null,
  brew_date date not null,
  in_bottles integer not null,
  on_tap integer not null,
  fermenting integer not null
);

create table grain(
  name text primary key,
  type text not null,
  amount float not null
);

create table hops(
  name text primary key,
  type text not null,
  amount float not null,
  minutes text not null
);

create table yeast(
  name text primary key,
  type text not null,
  starter_vol float not null,
  starter_dme float not null,
  vol_pitched float not null
);

create table mash(
  name text primary key,
  pre_boil_vol float,
  strike_temp integer,
  mash_temp integer,
  mash_time integer,
  OG text,
  FG text,
  ABV float,
  vol_into_fermenter float
);

create table temperatures(
  name text primary key,
  timestamp datetime not null,
  temperature float not null
);
