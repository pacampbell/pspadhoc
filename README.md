# PSP Adhoc Server

Source code for the pspadhoc server found in a random forum thread. Looking to
understand how it works, and add ncurses support for better server administration.

# Dependencies
1. gcc
2. sqlite-3
	* To install on a debian based machine `sudo apt-get install libsqlite3-dev`
3. gmake

# Usage

TODO:

# database.db explanation

| Table      | Create Statements                                                 | Description |
| :--------: | :---------------------------------------------------------------: | :---------- |
| productids | CREATE TABLE productids(id text primary key, name text not null); |             |
| crosslinks | CREATE TABLE crosslinks(id_from text, id_to text);                |             |
