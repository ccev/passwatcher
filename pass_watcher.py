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
    config['do_wh'] = config_raw.getboolean(
        'Config',
        'SEND_WEBHOOKS')
    config['webhook'] = config_raw.get(
        'Config',
        'WEBHOOK_URL')
    config['bbox'] = config_raw.get(
        'Config',
        'BBOX')
    config['bbox'] = list(config['bbox'].split(','))

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

    # VISUAL #
    config['ava_img'] = config_raw.get(
        'Visual',
        'AVATAR_URL')
    config['ava_name'] = config_raw.get(
        'Visual',
        'AVATAR_NAME')
    config['em_title'] = config_raw.get(
        'Visual',
        'EMBED_TITLE')
    config['em_color'] = config_raw.get(
        'Visual',
        'EMBED_COLOR')

    if config['db_scheme'] == "mad":
        config['db_id'] = "gym_id"
        config['db_ex'] = "is_ex_raid_eligible"
    elif config['db_scheme'] == "rdm":
        config['db_id'] = "id"
        config['db_ex'] = "ex_raid_eligible"
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

    cursor = mydb.cursor()

    return cursor

def check_passes(config, cursor):
    print("Checking for new EX gyms...")
    cursor.execute(f"SELECT gym.{config['db_id']} FROM {config['db_dbname']}.gym LEFT JOIN {config['db_manual_dbname']}.ex_gyms ON ex_gyms.gym_id = gym.{config['db_id']} WHERE gym.{config['db_ex']} = 1 AND ex_gyms.ex IS NULL;")
    new_ex = cursor.fetchall()

    for sublist in new_ex:
        for gym_id in sublist:
            if gym_id == None:
                print("Found no new EX gyms.")
            else:
                print(f"Found new EX gym {gym_id} - updating manualdb")
                cursor.execute(f"INSERT INTO {config['db_manual_dbname']}.ex_gyms (gym_id, ex, pass) VALUES ('{gym_id}', 1, 0)")

    print("Checking for EX Passes...")
    if config['db_scheme'] == "rdm":
        query = f"SELECT gym.name, gym.id, lon, lat FROM {config['db_manual_dbname']}.ex_gyms LEFT JOIN {config['db_dbname']}.gym ON ex_gyms.gym_id = gym.id WHERE gym.is_ex_eligible = 0 AND ex_gyms.ex = 1"
    elif config['db_scheme'] == "mad":
        query = f"SELECT gymdetails.name, gym.gym_id, longitude, latitude FROM {config['db_manual_dbname']}.ex_gyms LEFT JOIN {config['db_dbname']}.gym ON ex_gyms.gym_id = gym.gym_id LEFT JOIN {config['db_dbname']}.gymdetails ON gym.gym_id = gymdetails.gym_id WHERE gym.is_ex_raid_eligible = 0 AND ex_gyms.ex = 1"
    cursor.execute(query)
    passes = cursor.fetchall()
    print("Resetting Passes")
    cursor.execute(f"UPDATE {config['db_manual_dbname']}.ex_gyms SET pass = 0 WHERE pass = 1")

    text = ""
    if len(passes) == 0:
        print("Found no gyms with EX passes on them.")
    else:
        for name, gym_id, lon, lat in passes:
            cursor.execute(f"UPDATE {config['db_manual_dbname']}.ex_gyms SET pass = 1 WHERE gym_id = '{gym_id}'")
            if lon > float(config['bbox'][0]) and lon < float(config['bbox'][2]) and lat > float(config['bbox'][1]) and lat < float(config['bbox'][3]):
                text = text + f"{name}\n"

    if config['do_wh']:
        print("Sending Webhook...")
        if len(text) > 1:
            text = text[:-1]
            data = {
                "username": config['ava_name'],
                "avatar_url": config['ava_img'],
                "embeds": [{
                    "title": config['em_title'],
                    "description": text,
                    "color": config['em_color']
                    }
                ]
            }
            webhooks = json.loads(config['webhook'])
            for webhook in webhooks:
                result = requests.post(webhook, json=data)
                print(result)
        else:
           print("Not sending a Webhook if no Passes went out.")     

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default="default.ini", help="Config file to use")
    args = parser.parse_args()
    config_path = args.config
    config = create_config(config_path)
    cursor = connect_db(config)
    check_passes(config, cursor)