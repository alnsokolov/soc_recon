import vk_api
import os
import cache


def auth(check_saved=1):
    def tfa_handler():
        code = input("[!] 2FA detected! Please enter code you've just received: ")
        return code, 0

    def inner_auth(i_login=None, i_password=None, tfa=tfa_handler):
        session = vk_api.VkApi(login=i_login,
                               password=i_password,
                               auth_handler=tfa)

        session.auth()
        vk = session.get_api()
        if vk.users.get(user_ids='1')[0]['id'] == 1:
            print("[+] Auth succeeded!")
            return vk
        else:
            print("[-] Some error occurred, try again or Ctrl-C")
            return -1

    if "creds.log" in os.listdir("resources") and check_saved:
        print('[.] Trying to auth using saved creds')
        with open("resources/creds.log", "r") as f:
            lines = f.readlines()
            if len(lines) == 2:
                res = inner_auth(i_login=lines[0], i_password=lines[1])
            else:
                print("[!] Auth using saved creds failed, login manually!")
                return auth(0)

            if res == -1:
                print("[!] Auth using saved creds failed, login manually!")
                auth(0)
            else:
                return res
    else:
        login = input("[?] Enter your login: ")
        password = input("[?] Enter you password: ")
        if input("Do you want to save your creds? They WON'T be encrypted [Y/es, N/o] ").upper().startswith("Y"):
            with open("resources/creds.log", "w") as f:
                f.write("\n".join((login, password)))
        return inner_auth(i_login=login, i_password=password)


def get_all_info(session=None, targets=None):
    # do not need to check whether data is given since all checks are done before
    os.chdir("resources")
    with open("full_info", "r") as f:
        scope = f.readlines()[0]
    os.chdir("..")
    return session.users.get(user_ids=targets, fields=scope)


def get_friends(session=None, target=None):
    starget = str(target)
    if cache.contains(starget):
        return cache.get(starget)
    else:
        try:
            friends = session.friends.get(user_id=target)["items"]
        except vk_api.exceptions.ApiError:
            print("[!] ID " + str(target) + " is private. Skipping")
            return -1
        cache.add(starget, friends)
        return friends


def get_names(session, targets):
    resp = session.users.get(user_ids=",".join(targets))
    result = {}
    for data in resp:
        name = data["first_name"] + " " + data["last_name"]
        result.update({str(data['id']): name})
    return result


def get_groups(session=None, target=None):
    pass

