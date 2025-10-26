from impacket.smbconnection import SMBConnection

def list_shares(target, username='', password=''):
    try:
        conn = SMBConnection(target, 445)
        conn,login(username, password)
        shares = conn.listshares()
        print(f'[+] SMB Shares on {target}:')
        for share in shares:
            print(f'    - {share['shi1_netname']}')
            conn.close()
    except Exception as e:
        print(f'[-] Error: {e}')

if __name__ == '__main__':
    target = '192.168.40.246'
    list_shares(target)