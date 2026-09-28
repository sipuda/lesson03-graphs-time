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

genre_counts = df['first_genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화편수']

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

fig2 = px.treemap(
    df,
    path=[px.Constant("전체 영화"), 'first_genre', 'movieNm'],
    values='total_audi',
    color='first_genre',
    title="<b>장르별 및 영화별 총 관객수 비중 (트리맵)</b>",
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig2.update_traces(
    hovertemplate="<b>영화명 / 장르:</b> %{label}<br><b>총 관객수:</b> %{value:,}명<extra></extra>"
)

fig2.update_layout(
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 장르 전체의 총 관객 규모와 그 안에서 특정 개별 영화가 차지하는 흥행 비중을 한눈에 비교 분석할 수 있습니다.")

st.markdown("---")

# =============================================================================
# 구역 3: 총 관객수 분포 (히스토그램)
# =============================================================================
st.header("📌 구역 3: 총 관객수 히스토그램")

max_movie = df.loc[df['total_audi'].idxmax()]
max_movie_name = max_movie['movieNm']
max_movie_audi = int(max_movie['total_audi'])

fig3 = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    title="<b>개봉 영화 총 관객수 분포 (히스토그램)</b>",
    labels={'total_audi': '총 관객수(명)', 'count': '영화 수(편)'},
    color_discrete_sequence=['#3366CC']
)

fig3.update_traces(
    hovertemplate="<b>관객수 구간:</b> %{x}명<br><b>영화 수:</b> %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객수 (명)",
    yaxis_title="영화 수 (편)",
    template="plotly_white"
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    f"💡 **이 그래프로 알 수 있는 것:**\n"
    f"- 대부분의 영화는 관객수 **하위 구간(초반 구간)**에 빽빽하게 몰려 있으며, 고흥행 영화로 갈수록 편수가 급격히 줄어드는 **비대칭적 분포**를 보입니다.\n"
    f"- 이 기간 동안 가장 관객이 많은 1위 영화는 **[{max_movie_name}]** (총 **{max_movie_audi:,}명**)입니다."
)

st.markdown("---")

# =============================================================================
# 구역 4: 개봉일 스크린수 vs 총 관객수 (산점도)
# =============================================================================
st.header("📌 구역 4: 개봉일 스크린수와 총 관객수의 관계")

fig4 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='first_genre',
    hover_name='movieNm',
    title="<b>개봉일 스크린수 vs 총 관객수 (산점도)</b>",
    labels={
        'first_scrn': '개봉일 스크린수(개)',
        'total_audi': '총 관객수(명)',
        'first_genre': '장르',
        'movieNm': '영화명'
    },
    color_discrete_sequence=px.colors.qualitative.Alphabet
)

fig4.update_traces(
    marker=dict(size=10, opacity=0.8),
    hovertemplate="<b>영화명:</b> %{hovertext}<br><b>장르:</b> %{fullData.name}<br><b>개봉일 스크린수:</b> %{x:,}개<br><b>총 관객수:</b> %{y:,}명<extra></extra>"
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수 (개)",
    yaxis_title="총 관객수 (명)",
    template="plotly_white"
)

st.plotly_chart(fig4, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 개봉 당일 확보한 스크린수가 많을수록 최종 누적 관객수도 증가하는 양의 상관관계를 보이는지, 장르별 스크린 확보 수준에 차이가 있는지 파악할 수 있습니다.")

st.markdown("---")

# =============================================================================
# 구역 5: 주요 장르별 총 관객수 분포 (박스플롯)
# =============================================================================
st.header("📌 구역 5: 영화 10편 이상 주요 장르의 총 관객수 분포")

# 영화 편수가 10편 이상인 장르 필터링
genre_counts_series = df['first_genre'].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()
df_filtered_genres = df[df['first_genre'].isin(top_genres)]

fig5 = px.box(
    df_filtered_genres,
    x='first_genre',
    y='total_audi',
    color='first_genre',
    hover_name='movieNm',
    points='outliers',  # 이상치 점만 표시
    title="<b>영화 10편 이상 장르별 총 관객수 분포 (박스플롯)</b>",
    labels={
        'first_genre': '장르',
        'total_audi': '총 관객수(명)',
        'movieNm': '영화명'
    },
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig5.update_traces(
    hovertemplate="<b>영화명:</b> %{hovertext}<br><b>장르:</b> %{x}<br><b>총 관객수:</b> %{y:,}명<extra></extra>"
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객수 (명)",
    showlegend=False,
    template="plotly_white"
)

st.plotly_chart(fig5, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 각 장르별 관객수의 중앙값과 편차 범위, 그리고 상자 밖으로 튀어나온 이상치(Outlier) 점을 통해 해당 장르에서 특별히 흥행 대박을 터뜨린 대작 영화가 누구인지 확인할 수 있습니다.")

st.markdown("---")

# =============================================================================
# 구역 6: 개봉일 스크린수 vs 총 관객수 (첫 주 관객수 버블 차트)
# =============================================================================
st.header("📌 구역 6: 개봉일 스크린수, 총 관객수 및 첫 주 관객수 (버블 차트)")

fig6 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    color='first_genre',
    hover_name='movieNm',
    size_max=50,  # 버블 최대 크기 설정
    title="<b>개봉일 스크린수 vs 총 관객수 (버블 크기: 첫 주 관객수)</b>",
    labels={
        'first_scrn': '개봉일 스크린수(개)',
        'total_audi': '총 관객수(명)',
        'first_week_audi': '첫 주 관객수(명)',
        'first_genre': '장르',
        'movieNm': '영화명'
    },
    color_discrete_sequence=px.colors.qualitative.Alphabet
)

fig6.update_traces(
    hovertemplate="<b>영화명:</b> %{hovertext}<br><b>장르:</b> %{fullData.name}<br><b>개봉일 스크린수:</b> %{x:,}개<br><b>총 관객수:</b> %{y:,}명<br><b>첫 주 관객수:</b> %{marker.size:,}명<extra></extra>"
)

fig6.update_layout(
    xaxis_title="개봉일 스크린수 (개)",
    yaxis_title="총 관객수 (명)",
    template="plotly_white"
)

st.plotly_chart(fig6, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 원의 크기(첫 주 관객수)를 함께 비교함으로써 초기 집객력이 좋았던 영화가 최종 관객수까지 안정적으로 연결되었는지 다차원적으로 분석할 수 있습니다.")

st.markdown("---")
