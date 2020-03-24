from configparser import ConfigParser
from pymysql import connect
import requests
import argparse
import json

def create_config(config_path):
    config = dict()
    config_raw = ConfigParser()
    config_raw.read("default.ini")
    config_raw.read(config_path)
    
    # CONFIG #
    config['bbox'] = config_raw.get(
        'Config',
        'BBOX')
    config['chat'] = config_raw.get(
        'Config',
        'CHAT_APP')
    config['bbox'] = list(config['bbox'].split(','))
    config['language'] = config_raw.get(
        'Config',
        'LANGUAGE')

    # DB #
    config['db_scheme'] = config_raw.get(
        'DB',
        'SCANNER')
    config['db_dbname'] = config_raw.get(
        'DB',
        'SCANNER_DB_NAME')
    config['db_manual_dbname'] = config_raw.get(
        'DB',
        'MANUAL_DB_NAME')
    config['db_host'] = config_raw.get(
        'DB',
        'HOST')
    config['db_port'] = config_raw.getint(
        'DB',
        'PORT')
    config['db_user'] = config_raw.get(
        'DB',
        'USER')
    config['db_pass'] = config_raw.get(
        'DB',
        'PASSWORD')

    # EX PASSES #
    config['do_wh'] = config_raw.getboolean(
        'EX Pass Webhooks',
        'SEND_WEBHOOKS')
    config['webhook'] = config_raw.get(
        'EX Pass Webhooks',
        'WEBHOOK_URL')
    config['ava_img'] = config_raw.get(
        'EX Pass Webhooks',
        'AVATAR_URL')
    config['em_color'] = config_raw.get(
        'EX Pass Webhooks',
        'EMBED_COLOR')
    config['tg_sticker'] = config_raw.get(
        'EX Pass Webhooks',
        'TG_STICKER')
    config['tg_bot_id'] = config_raw.get(
        'EX Pass Webhooks',
        'TG_BOT_ID')
    config['tg_chat_id'] = config_raw.get(
        'EX Pass Webhooks',
        'TG_CHAT_ID')

    # EX GYMS #
    config['do_ex_wh'] = config_raw.getboolean(
        'EX Gym Webhooks',
        'SEND_WEBHOOKS')
    config['ex_webhook'] = config_raw.get(
        'EX Gym Webhooks',
        'WEBHOOK_URL')
    config['ava_img_ex'] = config_raw.get(
        'EX Gym Webhooks',
        'AVATAR_URL')
    config['em_color_ex'] = config_raw.get(
        'EX Gym Webhooks',
        'EMBED_COLOR')
    config['tg_sticker_ex'] = config_raw.get(
        'EX Gym Webhooks',
        'TG_STICKER')
    config['tg_bot_id_ex'] = config_raw.get(
        'EX Gym Webhooks',
        'TG_BOT_ID')
    config['tg_chat_id_ex'] = config_raw.get(
        'EX Gym Webhooks',
        'TG_CHAT_ID')

    # LEEVO PMSF #
    config['use_leevo'] = config_raw.getboolean(
        'Leevo PMSF',
        'ENABLE')
    config['dir_leevo'] = config_raw.get(
        'Leevo PMSF',
        'DIRECTORY')

    if config['db_scheme'] == "mad":
        config['db_id'] = "gym_id"
        config['db_ex'] = "is_ex_raid_eligible"
        config['db_details'] = "gymdetails"
        config['db_lat'] = "latitude"
        config['db_lon'] = "longitude"
    elif config['db_scheme'] == "rdm":
        config['db_id'] = "id"
        config['db_ex'] = "ex_raid_eligible"
        config['db_details'] = "gym"
        config['db_lat'] = "lat"
        config['db_lon'] = "lon"
    else:
        print("Unknown Scanner scheme. Please only put `rdm` or `mad` in.")

    return config

def connect_db(config):
    mydb = connect(
        host=config['db_host'],
        user=config['db_user'],
        passwd=config['db_pass'],
        database=config['db_dbname'],
        port=config['db_port'],
        autocommit=True)

    return mydb

def send_discord_webhook(data, webhook):
    webhooks = json.loads(webhook)
    for url in webhooks:
        result = requests.post(url, json=data)
        print(result)

def send_tg_webhook(data, bot_id, sticker):
    result = requests.get(f"https://api.telegram.org/bot{bot_id}/sendSticker", params=sticker)
    if result.status_code > 200:
        print("Error while sending sticker")
        print(result.text)
    else:
        print("Succes sending sticker")
    result = requests.get(f"https://api.telegram.org/bot{bot_id}/sendMessage", params=data)
    if result.status_code > 200:
        print("Error while sending Webhook")
        print(result.text)
    else:
        print("Succes sending text")

def check_passes(config, cursor):
    print("Checking for new EX gyms...")
    cursor.execute(f"SELECT gym.{config['db_id']} FROM {config['db_dbname']}.gym LEFT JOIN {config['db_manual_dbname']}.ex_gyms ON ex_gyms.gym_id = gym.{config['db_id']} WHERE gym.{config['db_ex']} = 1 AND ex_gyms.ex IS NULL AND gym.{config['db_lon']} > {float(config['bbox'][0])} AND gym.{config['db_lon']} < {float(config['bbox'][2])} AND gym.{config['db_lat']} > {float(config['bbox'][1])} AND gym.{config['db_lat']} < {float(config['bbox'][3])};")
    new_ex = cursor.fetchall()

    for sublist in new_ex:
        for gym_id in sublist:
            if gym_id == None:
                print("Found no new EX gyms.")
            else:
                print(f"Found new EX gym {gym_id} - updating manualdb")
                cursor.execute(f"INSERT INTO {config['db_manual_dbname']}.ex_gyms (gym_id, ex, pass) VALUES ('{gym_id}', 1, 0)")
                if config['do_ex_wh']:
                    print("Sending a Webhook for it")
                    cursor.execute(f"SELECT name, url FROM {config['db_dbname']}.{config['db_details']} WHERE {config['db_id']} = '{gym_id}'")
                    details = cursor.fetchall()
                    for name, img in details:
                        if config['chat'] == "discord":
                            data = {
                                "username": locale['discord_new_ex_avatar'],
                                "avatar_url": config['ava_img_ex'],
                                "embeds": [{
                                    "title": name,
                                    "color": config['em_color_ex'],
                                    "thumbnail": {
                                        "url": img
                                    }
                                    }
                                ]
                            }
                            send_discord_webhook(data, config['ex_webhook'])
                        elif config['chat'] == "telegram":
                            data = {
                                "chat_id": config['tg_chat_id_ex'],
                                "parse_mode": "markdown",
                                "text": f"{locale['telegram_new_ex_title']}\n{name}"
                            }
                            sticker = {
                                "chat_id": config["tg_chat_id_ex"],
                                "parse_mode": "markdown",
                                "sticker": config['tg_sticker_ex']
                            }
                            send_tg_webhook(data, config['tg_bot_id_ex'], sticker)
                        else:
                            print("Unknown chat app! Only `discord` or `telegram are allowed`")

    print("Checking for EX Passes...")
    if config['db_scheme'] == "rdm":
        query = f"SELECT gym.name, gym.id, lon, lat FROM {config['db_manual_dbname']}.ex_gyms LEFT JOIN {config['db_dbname']}.gym ON ex_gyms.gym_id = gym.id WHERE gym.ex_raid_eligible = 0 AND ex_gyms.ex = 1 AND ex_gyms.pass = 0 AND gym.{config['db_lon']} > {float(config['bbox'][0])} AND gym.{config['db_lon']} < {float(config['bbox'][2])} AND gym.{config['db_lat']} > {float(config['bbox'][1])} AND gym.{config['db_lat']} < {float(config['bbox'][3])}"
    elif config['db_scheme'] == "mad":
        query = f"SELECT gymdetails.name, gym.gym_id, longitude, latitude FROM {config['db_manual_dbname']}.ex_gyms LEFT JOIN {config['db_dbname']}.gym ON ex_gyms.gym_id = gym.gym_id LEFT JOIN {config['db_dbname']}.gymdetails ON gym.gym_id = gymdetails.gym_id WHERE gym.is_ex_raid_eligible = 0 AND ex_gyms.ex = 1 AND ex_gyms.pass = 0 AND gym.{config['db_lon']} > {float(config['bbox'][0])} AND gym.{config['db_lon']} < {float(config['bbox'][2])} AND gym.{config['db_lat']} > {float(config['bbox'][1])} AND gym.{config['db_lat']} < {float(config['bbox'][3])}"
    cursor.execute(query)
    passes = cursor.fetchall()
    print("Resetting Passes")
    cursor.execute(f"UPDATE {config['db_manual_dbname']}.ex_gyms SET pass = 0 WHERE pass = 1 AND gym_id IN (SELECT {config['db_id']} FROM {config['db_dbname']}.gym WHERE {config['db_ex']} = 1)")

    text = ""
    if len(passes) == 0:
        print("Found no gyms with EX passes on them.")
    else:
        for name, gym_id, lon, lat in passes:
            cursor.execute(f"UPDATE {config['db_manual_dbname']}.ex_gyms SET pass = 1 WHERE gym_id = '{gym_id}'")
            #if lon > float(config['bbox'][0]) and lon < float(config['bbox'][2]) and lat > float(config['bbox'][1]) and lat < float(config['bbox'][3]):
            text = text + f"{name}\n"

    if config['do_wh']:
        print("Sending Webhook...")
        if len(text) > 1:
            text = text[:-1]
            if config['chat'] == "discord":
                data = {
                    "username": locale['discord_pass_avatar'],
                    "avatar_url": config['ava_img'],
                    "embeds": [{
                        "title": locale['discord_pass_title'],
                        "description": text,
                        "color": config['em_color']
                        }
                    ]
                }
                send_discord_webhook(data, config['webhook'])
            elif config['chat'] == "telegram":
                data = {
                        "chat_id": config['tg_chat_id'],
                        "parse_mode": "markdown",
                        "text": f"{locale['telegram_pass_title']}\n{text}"
                    }
                sticker = {
                        "chat_id": config['tg_chat_id'],
                        "parse_mode": "markdown",
                        "sticker": config['tg_sticker']
                }
                send_tg_webhook(data, config['tg_bot_id'], sticker)
            else:
                print("Unknown chat app! Only `discord` or `telegram are allowed`")
        else:
           print("Not sending a Webhook if no Passes went out in the given area.")   

def leevo(config, cursor):
    cursor.execute(f"SELECT gym_id FROM {config['db_manual_dbname']}.ex_gyms WHERE pass = 1;")
    pass_gyms = cursor.fetchall()

    with open(config['dir_leevo'], 'r') as f:
        jsongyms = json.load(f)

    for gym_id in pass_gyms:
        if not gym_id in jsongyms["gyms"]:
            jsongyms["gyms"].append(gym_id)

    with open(config['dir_leevo'], "w") as f:
        f.write(json.dumps(jsongyms, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="default.ini", help="Config file to use")
    args = parser.parse_args()
    config_path = args.config
    config = create_config(config_path)
    mydb = connect_db(config)
    cursor = mydb.cursor()

    with open(f"locale/{config['language']}.json") as localejson:
        locale = json.load(localejson)

    check_passes(config, cursor)
    if config['use_leevo']:
        leevo(config, cursor)
    cursor.close()
    mydb.close()
