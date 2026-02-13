import koreanize_matplotlib
import matplotlib.pyplot as plt
from loguru import logger

# Matplotlib 한글 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Loguru 설정
logger.add("file_{time}.log", rotation="500 MB")

def main():
    print("Hello from webscraping-gemini!")
    logger.info("메인 함수가 실행되었습니다.")


if __name__ == "__main__":
    main()
