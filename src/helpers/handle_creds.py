from src.helpers.scripts.logger import debug_log


def load_correct_creds(creds):
    return creds['prod']['access_key'], creds['prod']['secret_key']
