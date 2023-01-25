# Local devices info

Script displays information about devices connected to local network based on router's DHCP.
Displayed devices are sorted by last actvity (latest active device on top).
Can be used to check who and when has used the network.

## Running the code

```
python main.py <router_login> <router_password> <router_ip>
```

## Requirements

-   Huawei router
-   Python 3.8+
-   Huawei API Package [huawei-lte-api](https://pypi.org/project/huawei-lte-api/)

### Why?

Because the router's website did not work and I had to find a workaround.
