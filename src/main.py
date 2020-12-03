from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.Connection import Connection
import config as cfg
from pprint import pprint
import datetime


def connect(login: str, password: str, ip: str) -> Client:
    credentials = f"http://{login}:{password}@{ip}/"
    connection = AuthorizedConnection(credentials)
    client = Client(connection)

    return client


def real_name(name: str) -> str:
    if name is None:
        return "Unknown"

    if name not in cfg.known_hosts.keys():
        return name

    return cfg.known_hosts[name]


def name_in_info(info: list, name: str) -> bool:
    if name == "Unknown":
        return False

    names = [info[i]["name"] for i in info.keys()]

    return name in names


def get_users_info(c: Client) -> dict:
    data = c.dhcp.dhcp_host_info()["Hosts"]["Host"]
    output = {}

    for d in data:
        key = d["ClientIndex"]
        name = real_name(d["ClientName"])

        # Skip duplicates
        if name_in_info(output, name) or name == "Unknown":
            continue

        seconds = cfg.expire_time - int(d["ClientExpires"])
        last_active = str(datetime.timedelta(seconds=seconds))

        if seconds >= cfg.expire_time:
            last_active += " (timed out)"

        output[key] = {
            "name": name,
            "system_name": d["ClientName"],
            "last_active": last_active,
            "last_active_sec": seconds,
        }

    return output


def display_info(c: Client) -> None:
    if c is None:
        return

    users_info = get_users_info(c)
    users_info = dict(
        sorted(users_info.items(), key=lambda item: item[1]["last_active_sec"])
    )

    if len(users_info):
        print("Connected devices:")
        print(f"{'Tag':<30} {'Name':<30} Last active (!)\n")

        for user in users_info.values():
            name = user["name"]
            sys_name = user["system_name"]
            last = user["last_active"]

            print(f"{name:<30} {sys_name:<30} {last}")

    else:
        print("There are no connected users.")
        return


client = connect(cfg.login, cfg.password, cfg.ip)

display_info(client)
