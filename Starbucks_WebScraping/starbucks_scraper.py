
import requests
import pandas as pd
from loguru import logger
import os

# 로그 파일 설정
log_path = os.path.join("Starbucks_WebScraping", "scraping.log")
logger.add(log_path, rotation="500 MB")

def get_starbucks_stores():
    """
    스타벅스 매장 정보를 전국적으로 스크레이핑합니다.
    p_sido_cd=01부터 17까지 순회하며 매장 데이터를 수집합니다.
    """
    url = "https://www.starbucks.co.kr/store/getStore.do"
    headers = {
        "host": "www.starbucks.co.kr",
        "origin": "https://www.starbucks.co.kr",
        "referer": "https://www.starbucks.co.kr/store/store_map.do",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
        "x-requested-with": "XMLHttpRequest"
    }
    all_stores = []

    for sido_cd in range(1, 18):
        p_sido_cd = f"{sido_cd:02d}"
        payload = {
            "in_biz_cds": "0",
            "in_scodes": "0",
            "ins_lat": "37.56682",
            "ins_lng": "126.97865",
            "search_text": "",
            "p_sido_cd": p_sido_cd,
            "p_gugun_cd": "",
            "isError": "true",
            "in_distance": "0",
            "in_biz_cd": "",
            "iend": "1000",
            "searchType": "C",
            "set_date": "",
            "all_store": "0",
            "whcroad_yn": "0",
            "new_bool": "0"
        }
        
        try:
            logger.info(f"Sido Code '{p_sido_cd}'의 매장 정보를 수집합니다.")
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킵니다.
            
            data = response.json()
            stores = data.get("list", [])
            
            if stores:
                logger.info(f"Sido Code '{p_sido_cd}'에서 {len(stores)}개의 매장을 찾았습니다.")
                all_stores.extend(stores)
            else:
                logger.warning(f"Sido Code '{p_sido_cd}'에 대한 매장 정보가 없습니다.")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Sido Code '{p_sido_cd}' 수집 중 오류 발생: {e}")
        except ValueError as e: # JSONDecodeError
            logger.error(f"Sido Code '{p_sido_cd}' 응답 JSON 파싱 오류: {e}")

    return all_stores

def save_stores_to_csv(stores):
    """
    수집된 매장 목록을 CSV 파일로 저장합니다.
    """
    if not stores:
        logger.warning("저장할 매장 정보가 없습니다.")
        return

    output_dir = os.path.join("Starbucks_WebScraping", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "starbucks_AIdata.csv")
    
    df = pd.DataFrame(stores)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info(f"총 {len(stores)}개의 매장 정보를 '{output_path}'에 저장했습니다.")

if __name__ == "__main__":
    logger.info("스타벅스 매장 정보 스크레이핑을 시작합니다.")
    starbucks_stores = get_starbucks_stores()
    save_stores_to_csv(starbucks_stores)
    logger.info("스크레이핑 프로세스가 완료되었습니다.")
