from src.helpers.scripts.logger import debug_log


def load_correct_creds(creds):
    debug_log(f"Load correct creds {creds}", False)
    return creds['prod']['access_key'], creds['prod']['secret_key']
