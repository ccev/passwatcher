# Pass Watcher
Pass Watcher will send a Webhook to Discord or Telegram with every gym that recieved an EX Pass this wave. It can also notify you about gyms that recently got their EX Tag

## How does it work?
Gyms lose their EX Tag when there's a EX Raid scheduled on it. Pass Watcher makes use of this mechanic by checking if a gym lost its EX Tag. When running the script, it will first put all EX gyms in the extra table and then compare it with your gym table to see if any gym lost its EX tag.
It's possible to have Pass Watcher send Webhooks to Discord or Telegram, but it's totally fine to turn them off and just have the script fill in the extra table.


![Sample message with default config options](https://i.imgur.com/ujixheG.png)

*Sample message with default config options*

## Usage
1. Create the `ex_gyms` table using the `ex_gyms.sql` file. Make sure to `USE [manualdb];` before.
2. `git clone https://github.com/ccev/passwatcher.git && cd passwatcher`, `pip[3[.6]] install -r requirements.txt`, then copy and rename `default.ini.example` to `default.ini` and fill out everything.
3. Set up the script to run in a loop. I recommend to use cron to have it running everyday at around 7:40pm GMT (the time passes are given out) (we'll find out the exact perfect time soon!)
4. Run the script once. It will fill out the extra table and that's it. First pass webhooks will be going out next time passes are given out.

## Configs
Important config options that aren't self explanatory:
- `WEBHOOK_URL`: Needs to be in `[""]` - you can send multiple webhooks by formatting them like this: `["https://www.url.com/1","https://www.url.com/2"]`
- `BBOX`: http://bboxfinder.com/ - draw a rectangle - copy the numbers right to the `Box` part on the bottom
- `SCANNER_DB_NAME` = The database where your scanned data is in. `MANUAL_DB_NAME` = The database where your extra table is in (preferably your PMSF manualdb)
