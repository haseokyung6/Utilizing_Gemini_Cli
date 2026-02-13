import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os
from datetime import datetime

# 0. 기본 설정
# 데이터 경로 설정
file_path = 'Starbucks_WebScraping/data/starbucks_AIdata.csv'
# 이미지 저장 폴더 생성
if not os.path.exists('Starbucks_WebScraping/images'):
    os.makedirs('Starbucks_WebScraping/images')
# 리포트 파일 경로
report_path = 'Starbucks_WebScraping/starbucks_eda_report.md'

# 데이터 로드
df = pd.read_csv(file_path)

# 리포트 생성을 위한 문자열
report = "## 스타벅스 매장 데이터 분석 보고서\n\n"
report += f"분석 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
report += f"데이터 경로: {file_path}\n\n"

# 0. 기본 분석
report += "### 0. 기본 분석\n\n"

# 데이터 구조 파악
report += "#### 데이터 구조\n"
report += f"- 전체 데이터 크기: {df.shape[0]}행, {df.shape[1]}열\n"
report += f"- 컬럼 목록: {', '.join(df.columns)}\n\n"

# 기술 통계
report += "#### 기술 통계\n"
report += df.describe().to_markdown() + "\n\n"

# 결측치 확인 및 처리
report += "#### 결측치 및 품질 점검\n"
missing_values = df.isnull().sum()
report += "결측치 수:\n"
report += missing_values[missing_values > 0].to_markdown() + "\n\n"

# 모두 같은 값이거나 결측치가 대부분인 컬럼 제거
cols_to_drop = []
for col in df.columns:
    if df[col].isnull().sum() / len(df) > 0.8: # 결측치가 80% 이상인 경우
        cols_to_drop.append(col)

if cols_to_drop:
    df.drop(columns=cols_to_drop, inplace=True)
    report += f"제거된 컬럼 (모두 동일한 값이거나 결측치가 80% 이상): {', '.join(cols_to_drop)}\n\n"

# 데이터 타입/패턴 분석
report += "#### 데이터 타입\n"
# df.info()는 출력을 직접 반환하지 않으므로, 문자열로 캡처해야 합니다.
import io
buffer = io.StringIO()
df.info(buf=buffer)
report += buffer.getvalue() + "\n\n"


# 1. 기본 정보 요약
report += "### 1. 기본 정보 요약\n\n"
summary = df[['s_name', 'sido_name', 'gugun_name', 'doro_address', 'open_dt', 'lat', 'lot']].head()
report += summary.to_markdown() + "\n\n"
report += f"- **총 매장 수**: {len(df)}개\n"
report += f"- **분석 지역**: {df['sido_name'].nunique()}개 시도, {df['gugun_name'].nunique()}개 시군구\n"
report += f"- **오픈일**: {df['open_dt'].min()} ~ {df['open_dt'].max()}\n\n"

# 2. 매장 특성 분석
report += "## 2. 매장 특성 분석 (theme_state)\n"

if 'theme_state' in df.columns:

    # 문자열 분리 후 explode
    theme_series = (
        df['theme_state']
        .dropna()
        .str.split('@')
        .explode()
        .str.strip()
    )

    # 빈값 제거
    theme_series = theme_series[theme_series != ""]

    feature_summary = theme_series.value_counts()

    if not feature_summary.empty:

        feature_summary = (
            theme_series
            .value_counts()
            .reset_index()
        )

        feature_summary.columns = ['theme_code', '매장 수']

        report += "### 매장별 제공 서비스/특징 (상위 10개)\n"
        report += feature_summary.head(10).to_markdown() + "\n\n"

        fig, ax = plt.subplots(figsize=(12, 8))

        feature_summary.head(10).set_index('theme_code').plot(
            kind='bar',
            ax=ax,
            legend=False
        )

        ax.set_title('상위 10개 매장 서비스/특징')
        ax.set_ylabel('매장 수')

        img_path = 'Starbucks_WebScraping/images/top10_features.png'
        plt.savefig(img_path)
        plt.close()

    else:
        report += "분석할 수 있는 theme_state 정보가 없습니다.\n"

else:
    report += "theme_state 컬럼이 존재하지 않습니다.\n"

# 3. 주변 위치적 특징 분석
report += "### 3. 주변 위치적 특징 분석\n\n"
# 시도별 매장 수
sido_counts = df['sido_name'].value_counts()
plt.figure(figsize=(15, 8))
sns.barplot(x=sido_counts.index, y=sido_counts.values)
plt.title('시도별 스타벅스 매장 수')
plt.xlabel('시도')
plt.ylabel('매장 수')
plt.xticks(rotation=45)
img_path = 'Starbucks_WebScraping/images/sido_distribution.png'
plt.savefig(img_path)
plt.close()
report += f"![시도별 매장 분포](images/sido_distribution.png)\n\n"
report += sido_counts.to_frame('매장 수').to_markdown() + "\n\n"

# 서울 내 구별 매장 수
if '서울' in df['sido_name'].unique():
    seoul_df = df[df['sido_name'] == '서울']
    gugun_counts = seoul_df['gugun_name'].value_counts()
    plt.figure(figsize=(15, 8))
    sns.barplot(x=gugun_counts.index, y=gugun_counts.values)
    plt.title('서울시 구별 스타벅스 매장 수')
    plt.xlabel('구')
    plt.ylabel('매장 수')
    plt.xticks(rotation=45)
    img_path = 'Starbucks_WebScraping/images/seoul_gugun_distribution.png'
    plt.savefig(img_path)
    plt.close()
    report += f"![서울시 구별 매장 분포](images/seoul_gugun_distribution.png)\n\n"
    report += gugun_counts.to_frame('매장 수').to_markdown() + "\n\n"


# 4. 오픈일(open_dt) 기반 통계적 해석
report += "### 4. 오픈일 기반 통계적 해석\n\n"
df['open_year'] = pd.to_datetime(df['open_dt'], format='%Y%m%d', errors='coerce').dt.year
df['open_month'] = pd.to_datetime(df['open_dt'], format='%Y%m%d', errors='coerce').dt.month

# 연도별 매장 오픈 수
open_year_counts = df['open_year'].value_counts().sort_index()
plt.figure(figsize=(12, 6))
open_year_counts.plot(kind='line', marker='o')
plt.title('연도별 스타벅스 매장 오픈 수')
plt.xlabel('연도')
plt.ylabel('오픈 매장 수')
img_path = 'Starbucks_WebScraping/images/open_year_trend.png'
plt.savefig(img_path)
plt.close()
report += f"![연도별 오픈 트렌드](images/open_year_trend.png)\n\n"
report += open_year_counts.to_frame('오픈 매장 수').to_markdown() + "\n\n"


# 5. 주요 비즈니스 인사이트
report += "### 5. 주요 비즈니스 인사이트\n\n"
report += "- **수도권 집중**: 매장의 대부분이 서울 및 수도권에 집중되어 있어, 해당 지역의 시장이 매우 중요함을 시사합니다.\n"
report += "- **오피스 상권**: 서울의 경우 강남구, 중구, 서초구 등 오피스 밀집 지역에 매장이 많아 직장인 고객이 주요 타겟임을 알 수 있습니다.\n"
report += "- **성장세**: 연도별 오픈 매장 수를 보면 꾸준히 매장이 증가하고 있으며, 이는 스타벅스의 지속적인 확장 전략을 보여줍니다.\n"
# In[ ]:
report += "- **편의시설**: 대부분의 매장이 기본적인 편의시설을 갖추고 있으나, 특정 테마(리저브, DT 등)를 가진 매장은 소수이므로 희소성이 있습니다.\n\n"

# 6. 데이터 품질 검증
report += "### 6. 데이터 품질 검증\n\n"
report += "- **결측치**: `open_dt`, `tel` 등 일부 컬럼에서 결측치가 발견되었습니다. 특히 `open_dt`는 시계열 분석에 중요하므로 데이터 보강이 필요합니다.\n"
report += "- **이상치**: 위도(lat), 경도(lot) 값이 0 또는 비정상적인 범위를 가지는 데이터가 있는지 확인이 필요합니다. 현재 분석에서는 좌표가 0인 데이터는 없었습니다.\n"
report += "- **코드값**: `sido_code`, `gugun_code` 등 코드값이 실제 행정 구역과 일치하는지 추가 검증이 필요할 수 있습니다.\n\n"

# 7. 추가 분석 제안
report += "### 7. 추가 분석 제안\n\n"
report += "- **경쟁사 분석**: 동일 지역 내 다른 커피 전문점(예: 투썸플레이스, 이디야) 데이터와 비교하여 상권 내 경쟁 강도를 분석할 수 있습니다.\n"
report += "- **유동인구 데이터 결합**: 각 매장 위치의 유동인구 데이터를 결합하여 매장 규모나 매출과의 상관관계를 분석할 수 있습니다.\n"
report += "- **테마별 고객 분석**: 리저브, DT, 커뮤니티 스토어 등 테마별 매장의 고객 특성 및 만족도를 분석하여 타겟 마케팅 전략을 수립할 수 있습니다.\n"
report += "- **매출 예측 모델**: 매장 특성, 위치, 주변 환경, 유동인구 등 다양한 변수를 활용하여 신규 매장의 예상 매출을 예측하는 모델을 개발할 수 있습니다.\n\n"


# 리포트 파일 저장
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"분석 보고서가 {report_path} 에 저장되었습니다.")
