# Database

The `halite-tournaments` database has the following structure :

- `halite-tournaments` (database name)
  - `players` (collection with players info)
  - `settings` (collection with environment settings)
  - `queues` (where actions get queued for handler)
  - `arena` (arena environment settings)

###### Users

`root` : has access to all databases and collections

`arena` : only has access to `halite-tournaments`'s collections :
- `players` (only find and update)
- `queues` (find, update and insert)
- `arena` (only find and update)

Check the **templates** in json in this folder for more info
