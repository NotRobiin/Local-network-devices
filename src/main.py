from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
import config as cfg
import datetime
import sys


def connect_to_router(login: str, password: str, ip: str) -> Client:
    credentials = f"http://{login}:{password}@{ip}/"
    connection = Connection(credentials)

    return Client(connection)


def get_device_info(c: Client) -> dict:
    devices = c.dhcp.dhcp_host_info()["Hosts"]["Host"]
    output = {}
    tags = cfg.known_hosts.keys()

    for device in devices:
        key = device["ClientIndex"]
        name = device["ClientName"]

        if name in cfg.known_hosts.keys():
            name = cfg.known_hosts[name]

        # Skip unknown devices (they have no data)
        if name == "Unknown" or name is None:
            continue

        # Skip duplicate entries
        if name in [output[i]["name"] for i in output.keys()]:
            continue

        dhcp_lease = int(c.dhcp.settings()["DhcpLeaseTime"])
        elapsed = dhcp_lease - int(device["ClientExpires"])
        last_active = str(datetime.timedelta(seconds=elapsed))

        if elapsed >= dhcp_lease:
            last_active += " (timed out)"

        output[key] = {
            "name": name,
            "device_name": device["ClientName"],
            "last_active": last_active,
            "last_active_sec": elapsed,
        }

    return output


def display_devices(c: Client) -> None:
    if c is None:
        print("Provided client is not a valid object.")
        return

    users_info = get_device_info(c)
    users_info = dict(
        sorted(users_info.items(), key=lambda item: item[1]["last_active_sec"])
    )

    if len(users_info) == 0:
        print("There are no connected users.")
        return

    print("Connected devices:")
    print(f"{'Tag':<30} {'Name':<30} Last active\n")

    for user in users_info.values():
        name = user["name"]
        sys_name = user["device_name"]
        last = user["last_active"]

        print(f"{name:<30} {sys_name:<30} {last}")


def get_arg(which):
    if len(sys.argv) >= which + 1:
        return sys.argv[which]


def main():
    login = get_arg(1) or "admin"
    password = get_arg(2) or "admin"
    ip = get_arg(3)

    if ip is None:
        print("Cannot connect without router ip.")
        return

    client = connect_to_router(login, password, ip)
    display_devices(client)


if __name__ == "__main__":
    main()
