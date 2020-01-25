# Pass Watcher
Pass Watcher will send a Webhook to Discord with every gym that recieved an EX Pass this wave.

## Notes/todo
- brand new repo
- requirements.txt missing (just pymysql pretty much)
- cron command
- -c will work

## How does it work?
Gyms lose their EX Tag when there's a scheduled EX Raid taking place on it. Pass watcher makes use of this mechanic by having a seperate table with all EX gyms you scanned in it. When running the script, it will compare your gym table with the extra table and see if any gym lost its EX tag.
It will send Webhooks to Discord and Discord only. You can however run the script without webhooks turned off to just fill the database.


![Sample message with default config options](https://i.imgur.com/ujixheG.png)

*Sample message with default config options*

## Usage
1. Create the `ex_gyms` table using the `ex_gyms.sql` file. Make sure to `USE [manualdb];` before.
2. `git clone https://github.com/ccev/passwatcher.git && cd passwatcher`, `pip[3[.6]] install -r requirements.txt`, then copy and rename `default.ini.example` to `default.ini` and fill out everything.
3. Use cron to have the script running once everytime passes are going out. (put cron command here)
4. Run the script once. It will fill out the extra table and that's it. First pass webhooks will be going out next time passes are going out.

## Configs
Important config options that aren't self explanatory:
- `WEBHOOK_URL`: Needs to be in `[""]` - you can send multiple webhooks by formatting them like this: `["https://www.url.com/1","https://www.url.com/2"]`
- `BBOX`: http://bboxfinder.com/ - draw a rectangle - copy the numbers right to the `Box` part on the bottom
- `SCANNER_DB_NAME` = The database where your scanned data is in. `MANUAL_DB_NAME` = The database where your extra table is in (preferably your PMSF manualdb)
