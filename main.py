import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 제목
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("개봉 영화의 장르, 국가, 스크린수, 관객수 등의 데이터를 활용하여 영화 시장의 분포와 다양한 변수 간의 관계를 시각화합니다.")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. 데이터 불러오기 및 전처리
# -----------------------------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 대표 장르 추출 (세로막대 기호 '|'가 있는 경우 첫 번째 장르만 추출)
    if 'genre' in df.columns:
        df['first_genre'] = df['genre'].astype(str).apply(
            lambda x: x.split('|')[0].strip() if pd.notna(x) and x != 'nan' else '기타'
        )
    else:
        df['first_genre'] = '미분류'

    # 수치형 컬럼 안전 변환
    numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

try:
    df = load_data()
    st.sidebar.success("✅ 데이터 불러오기 성공!")
    st.sidebar.info(f"📊 분석 대상 영화: 총 {len(df):,}편")
except Exception as e:
    st.error(f"⚠️ 데이터 로딩 실패: {e}")
    st.stop()

# =============================================================================
# 구역 1: 장르별 영화 편수 분포 (도넛 그래프)
# =============================================================================
st.header("📌 구역 1: 장르별 영화 편수 분포")

# 장르별 편수 집계
genre_counts = df['first_genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화편수']

# 도넛 그래프 생성 (hole=0.4)
fig1 = px.pie(
    genre_counts,
    names='장르',
    values='영화편수',
    hole=0.4,
    title="<b>개봉 영화 장르별 비중 (도넛 그래프)</b>",
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig1.update_traces(
    textposition='inside',
    textinfo='percent+label',
    hovertemplate="<b>장르:</b> %{label}<br><b>영화 수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>"
)

fig1.update_layout(
    legend_title_text="장르 목록",
    template="plotly_white"
)

st.plotly_chart(fig1, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권에 진입한 영화 중 어떤 장르가 가장 많은 비중을 차지하는지 장르별 시장 분포를 파악할 수 있습니다.")

st.markdown("---")

# =============================================================================
# 구역 2: 장르 및 영화별 총 관객수 분포 (트리맵)
# =============================================================================
st.header("📌 구역 2: 장르 내 영화별 총 관객수 분포")

# 트리맵 생성 (계층 구조: 대표 장르 -> 영화명, 사각형 크기: 총 관객수)
fig2 = px.treemap(
    df,
    path=[px.Constant("전체 영화"), 'first_genre', 'movieNm'],
    values='total_audi',
    color='first_genre',
    title="<b>장르별 및 영화별 총 관객수 비중 (트리맵)</b>",
    color_discrete_sequence=px.colors.qualitative.Set3
)

# 마우스 호버 시 영화명과 총 관객수가 보이도록 설정
fig2.update_traces(
    hovertemplate="<b>영화명 / 장르:</b> %{label}<br><b>총 관객수:</b> %{value:,}명<extra></extra>"
)

fig2.update_layout(
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 장르 전체의 총 관객 규모와 그 안에서 특정 개별 영화가 차지하는 흥행 비중을 한눈에 비교 분석할 수 있습니다.")

st.markdown("---")
