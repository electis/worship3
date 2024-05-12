import logging
import os
from contextlib import contextmanager

# import ffmpeg
import requests

from conf import Config

logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worship.log'), level=logging.INFO,
    format='%(asctime)s %(levelname)s %(module)s.%(funcName)s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S',
)


def send_message(text, chat_id, token, parse_mode='Markdown'):
    try:
        response = requests.get(f'https://api.telegram.org/bot{token}/sendMessage', timeout=10, params=dict(
            chat_id=chat_id, text=text, parse_mode=parse_mode))
    except Exception as exc:
        logging.warning(f'send_message Exception: {exc}')
        return False
    else:
        if response.status_code == 200:
            return response.json()
        else:
            logging.warning(f'send_message status_code {response.status_code}')
            return False


def log_tg(text, tg=None):
    if tg:
        send_message(text, tg.chat_id, tg.token)


@contextmanager
def notify(text, tg=None, only_error=True):
    logging.info(f'start {text}')
    if not only_error:
        log_tg(f'start {text}', tg)
    try:
        yield
    except Exception as exc:
        logging.exception(f'{text}: Exception {exc}')
        log_tg(f'Exception {exc}', tg)
    else:
        logging.info(f'stop {text}')
        if not only_error:
            log_tg(f'stop {text}', tg)


def run_task(conf: Config, params):
    if conf.post_.task_url and conf.post_.task_token:
        try:
            from requests.adapters import HTTPAdapter
            s = requests.Session()
            s.mount(conf.post_.task_url, HTTPAdapter(max_retries=5))
            s.post(conf.post_.task_url, headers=dict(Authorization=f'Token {conf.post_.task_token}'),
                   json=params)
        except Exception:
            requests.post(conf.post_.task_url, headers=dict(Authorization=f'Token {conf.post_.task_token}'),
                          json=params)
            raise


def post2group(conf: Config):
    if conf.post_ and conf.post_.youtube_channel and conf.post_.chat_id:
        params = {
            "task": "start_worship",
            "params": {
                "chat_id": conf.post_.chat_id,
                "text": "#ВремяМолитвы",
                "youtube_live": conf.post_.youtube_channel,
                "youtube_filter": "Время молитвы"
            }
        }
        with notify('post2group'):
            run_task(conf, params)


@contextmanager
def log_ffmpeg(ff, conf):
    if conf.debug:
        logging.getLogger().addHandler(logging.StreamHandler())
    result = [None]
    try:
        yield result
    # except ffmpeg.Error as exc:
    #     logging.exception(exc)
    #     logging.error(' '.join(ff.get_args()))
    #     logging.error(f'stderr: {exc.stderr.decode("utf8")}')
    #     logging.error(f'stdout: {exc.stdout.decode("utf8")}')
    #     log_tg(str(exc), conf.tg_)
    #     result[0] = exc
    except Exception as exc:
        logging.exception(exc)
        logging.error(' '.join(ff.get_args()))
        log_tg(str(exc), conf.tg_)
        result[0] = exc
    else:
        result[0] = True
