import aiohttp
import logging

import config
import exeptions
import texts

logger = logging.getLogger(__name__)

ACCESS_URL = "https://api.timeweb.ru/v1.2/access"


def _balance_url(login: str) -> str:
    return f"https://api.timeweb.ru/v1.1/finances/accounts/{login}"


def _sites_url(login: str) -> str:
    return f"https://api.timeweb.ru/v1.1/sites/{login}"


def _auth_headers(token: str) -> dict:
    return {
        "Accept": "application/json",
        "x-app-key": config.API_KEY,
        "Authorization": f"Bearer {token}",
    }


async def login(session: aiohttp.ClientSession, login_value: str, password: str) -> str:
    headers = {"Accept": "application/json", "x-app-key": config.API_KEY}
    auth = aiohttp.BasicAuth(login_value, password)
    try:
        async with session.post(ACCESS_URL, headers=headers, auth=auth) as response:
            if response.status == 200:
                data = await response.json()
                return data["token"]
            error_msg = await response.text()
            logger.error(f"{texts.LogTexts.AUTH_NOT_AVAILABLE.value} -> {ACCESS_URL} : "
                         f"{texts.LogTexts.CODE.value} {response.status}, "
                         f"{texts.LogTexts.ANSWER.value} {error_msg}")
            raise exeptions.TimewebAuthError(error_msg)
    except aiohttp.ClientError:
        logger.exception(texts.LogTexts.SITE_IS_NOT_AVAILABLE.value)
        raise


async def check_balance(session: aiohttp.ClientSession, login_value: str, token: str) -> list[dict]:
    return await _get(session, _balance_url(login_value), _auth_headers(token))

async def check_sites(session: aiohttp.ClientSession, login_value: str, token: str) -> list[dict]:
    all_sites = await _get(session, _sites_url(login_value), _auth_headers(token))
    return _extract_sites(all_sites)

async def check_domains(session: aiohttp.ClientSession, login_value: str, token: str) -> list[dict]:
    all_domains = await _get(session, _sites_url(login_value), _auth_headers(token))
    return _extract_domains(all_domains)

async def _get(session: aiohttp.ClientSession, url: str, headers: dict) -> list[dict] :
    try:
        async with session.get(url, headers=headers) as response:
            logger.info(f"{texts.LogTexts.CHECK_STATUS_API.value}{response.status}")

            if response.status == 200:
                data = await response.json()
                return data
            if  response.status == 401:
                error_msg = await response.text()
                logger.error(f"{texts.LogTexts.AUTH_NOT_AVAILABLE.value} -> {url} : "
                             f"{texts.LogTexts.CODE.value} {response.status}, "
                             f"{texts.LogTexts.ANSWER.value} {error_msg}")
                raise exeptions.TimewebAuthError(error_msg)
            else:
                error_msg = await response.text()
                logger.error(f"{texts.LogTexts.API_NOT_FOUND.value} {url}: "
                             f"{texts.LogTexts.CODE.value} {response.status}, "
                             f"{texts.LogTexts.ANSWER.value} {error_msg}")
                raise exeptions.TimewebApiError(error_msg)
    except aiohttp.ClientError:
        logger.exception(texts.LogTexts.SITE_IS_NOT_AVAILABLE.value)
        raise

def _extract_domains(result: list[dict]) -> list[dict] :
    res = [domain for sites in result for domain in sites.get("domains", [])]
    if not res:
        raise exeptions.TimewebDomainsNotFound()
    return res

def _extract_sites(result: list[dict]) -> list[dict] :
    res = [site.get("directory", "") for site in result]
    if not res:
        raise exeptions.TimewebSiteIsNotFound()
    return res