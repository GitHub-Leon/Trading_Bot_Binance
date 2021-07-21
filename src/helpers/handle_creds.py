def load_trading_creds(creds):
    return creds['prod']['access_key'], creds['prod']['secret_key']


def load_discord_creds(creds):
    return creds['discord']['DISCORD_WEBHOOK']
