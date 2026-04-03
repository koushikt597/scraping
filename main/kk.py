
import uuid

from curl_cffi import requests


cookies = {
    'gr_1_deviceId': '51388f1c-74be-4f36-be50-4674c4181922',
    '_gcl_au': '1.1.122481430.1774793296',
    'gr_1_locality': '1849',
    '_fbp': 'fb.1.1774793301139.701234961703312830',
    'gr_1_lat': '28.4132534',
    'gr_1_lon': '77.07271589999999',
    'gr_1_landmark': 'undefined',
    '_ga_K8QWRE7TPK': 'GS2.1.s1775053647$o1$g1$t1775053675$j32$l0$h0',
    'city': '',
    '_gid': 'GA1.2.130186359.1775192442',
    '_cfuvid': 'JnE19B9boQk0STPQxt1a1jLqvJZuyRA6.LBDDbEkTkk-1775209444477-0.0.1.1-604800000',
    '_gcl_gs': '2.1.k1$i1775209441$u260607710',
    '_gcl_aw': 'GCL.1775209447.Cj0KCQjwyr3OBhD0ARIsALlo-OmoDLgC2JxyHvhpD1XodfuXR3jjp_zJmHI_GNEw8DtbkXPsz3FaBaoaAkB0EALw_wcB',
    '_ga': 'GA1.2.1066744819.1774793298',
    '__cf_bm': '0l_P.ly7DrjDHtn6Aus4ThnHFS0cfrVeGCPJX5eG8Ec-1775213952-1.0.1.1-TEf1n5ThDxrSYHg.cVpqH9zpm4ZsEk9U.dJf177LPOdLSeMEinn26w4Q.a.XlVHBhG7oZswRrNE3HTcwy0.DyYMWqdrZEoYdCgmRpO0cn1E',
    '_gac_UA-85989319-1': '1.1775213966.Cj0KCQjwyr3OBhD0ARIsALlo-OmoDLgC2JxyHvhpD1XodfuXR3jjp_zJmHI_GNEw8DtbkXPsz3FaBaoaAkB0EALw_wcB',
    '_gat_UA-85989319-1': '1',
    '_ga_DDJ0134H6Z': 'GS2.2.s1775213965$o6$g1$t1775213973$j52$l0$h0',
    '_ga_JSMJG966C7': 'GS2.1.s1775213966$o6$g0$t1775213973$j53$l0$h0',
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'access_token': 'null',
    'app_client': 'consumer_web',
    'app_version': '1010101010',
    'auth_key': 'c761ec3633c22afad934fb17a66385c1c06c5472b4898b866b7306186d0bb477',
    # 'content-length': '0',
    'content-type': 'application/json',
    'device_id': '5d3b3903ec62aea5',
    'lat': '28.4132534',
    'lon': '77.07271589999999',
    'origin': 'https://blinkit.com',
    'priority': 'u=1, i',
    'referer': 'https://blinkit.com/s/?q=milk',
    'rn_bundle_version': '1009003012',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'session_uuid': '3e996b64-0fda-4822-9570-19fe546e3a8d',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'web_app_version': '1008010016',
    # 'cookie': 'gr_1_deviceId=51388f1c-74be-4f36-be50-4674c4181922; _gcl_au=1.1.122481430.1774793296; gr_1_locality=1849; _fbp=fb.1.1774793301139.701234961703312830; gr_1_lat=28.4132534; gr_1_lon=77.07271589999999; gr_1_landmark=undefined; _ga_K8QWRE7TPK=GS2.1.s1775053647$o1$g1$t1775053675$j32$l0$h0; city=; _gid=GA1.2.130186359.1775192442; _cfuvid=JnE19B9boQk0STPQxt1a1jLqvJZuyRA6.LBDDbEkTkk-1775209444477-0.0.1.1-604800000; _gcl_gs=2.1.k1$i1775209441$u260607710; _gcl_aw=GCL.1775209447.Cj0KCQjwyr3OBhD0ARIsALlo-OmoDLgC2JxyHvhpD1XodfuXR3jjp_zJmHI_GNEw8DtbkXPsz3FaBaoaAkB0EALw_wcB; _ga=GA1.2.1066744819.1774793298; __cf_bm=0l_P.ly7DrjDHtn6Aus4ThnHFS0cfrVeGCPJX5eG8Ec-1775213952-1.0.1.1-TEf1n5ThDxrSYHg.cVpqH9zpm4ZsEk9U.dJf177LPOdLSeMEinn26w4Q.a.XlVHBhG7oZswRrNE3HTcwy0.DyYMWqdrZEoYdCgmRpO0cn1E; _gac_UA-85989319-1=1.1775213966.Cj0KCQjwyr3OBhD0ARIsALlo-OmoDLgC2JxyHvhpD1XodfuXR3jjp_zJmHI_GNEw8DtbkXPsz3FaBaoaAkB0EALw_wcB; _gat_UA-85989319-1=1; _ga_DDJ0134H6Z=GS2.2.s1775213965$o6$g1$t1775213973$j52$l0$h0; _ga_JSMJG966C7=GS2.1.s1775213966$o6$g0$t1775213973$j53$l0$h0',
}

params = {
    'offset': '12',
    'limit': '12',
    'actual_query': 'milk',
    'last_snippet_type': 'product_card_snippet_type_2',
    'last_widget_type': 'listing_container',
    'page_index': '1',
    'q': 'milk',
    'search_count': '122',
    'search_method': 'basic',
    'search_type': 'type_to_search',
    'total_entities_processed': '1',
    'total_pagination_items': '122',
}

def blinkit_search(query='milk', offset=0, limit=12):
    params['q'] = query
    params['actual_query'] = query
    params['offset'] = str(offset)
    params['limit'] = str(limit)
    response = requests.post('https://blinkit.com/v1/layout/search', params=params, cookies=cookies, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Blinkit API failed: {response.status_code} {response.text[:300]}")
    return response.json()


if __name__ == "__main__":
    data = blinkit_search("milk", offset=0, limit=12)
    print(f"products={len(data.get('data', {}).get('products', []))}")
