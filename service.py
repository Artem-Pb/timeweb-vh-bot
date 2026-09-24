from enum import Enum

import aiohttp
import logging

import config
import exeptions
import texts

logger = logging.getLogger(__name__)


class ApiEndpoint(Enum):
    URL_FOR_BALANCE = f"https://api.timeweb.ru/v1.1/finances/accounts/{config.LOGIN}"
    URL_FOR_SITE = f"https://api.timeweb.ru/v1.1/sites/{config.LOGIN}"
    HEADERS = {
        "Accept": "application/json",
        "x-app-key": f"{config.API_KEY}",
        "Authorization": f"Bearer {config.TOKEN}"
    }


async def check_balance(session: aiohttp.ClientSession) -> list[dict]:
    return await _get(session, ApiEndpoint.URL_FOR_BALANCE.value, ApiEndpoint.HEADERS.value)

async def check_sites(session: aiohttp.ClientSession) -> list[dict]:
    all_sites = await _get(session, ApiEndpoint.URL_FOR_SITE.value, ApiEndpoint.HEADERS.value)
    return _extract_sites(all_sites)

async def check_domains(session: aiohttp.ClientSession) -> list[dict]:
    all_domains = await _get(session, ApiEndpoint.URL_FOR_SITE.value, ApiEndpoint.HEADERS.value)
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