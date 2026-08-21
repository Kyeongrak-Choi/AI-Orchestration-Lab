create table users (
    id uuid primary key default gen_random_uuid(),
    email text not null unique,
    username varchar(30) not null check (length(username) >= 2),
    created_at timestamptz not null default now()
);

insert into users(username,email) 
    values ('박길동','park@gil.dong'),
           ('최길동','choi@gil.dong'),
           ('김길동','kim@gil.dong'),
           ('조길동','cho@gil.dong');