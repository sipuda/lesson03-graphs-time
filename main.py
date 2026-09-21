import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="🎬 영화 데이터 그래프 도감 1 - 시간",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_movie_data():
    """GitHub에서 kobis_daily.csv 데이터를 불러와 날짜 및 전처리를 수행합니다."""
    data_url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    
    # CSV 데이터 로드
    df = pd.read_csv(data_url)
    
    # '날짜' 열을 문자열로 변환 후 datetime 객체로 포맷팅 (YYYYMMDD)
    df['날짜'] = df['날짜'].astype(str)
    df['날짜_dt'] = pd.to_datetime(df['날짜'], format='%Y%m%d', errors='coerce')
    
    # 숫자형 데이터 타입 변환 및 정제
    numeric_cols = ['순위', '일관객', '누적관객', '스크린수', '상영횟수']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    return df

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
박스오피스 데이터를 바탕으로 **시간의 흐름**에 따른 영화별 관객 수 추이와 흥행 패턴을 분석하는 시각화 도감입니다.  
사이드바 및 구역별 옵션을 통해 원하는 영화를 선택하여 그래프를 확인하세요.
""")
st.divider()

try:
    with st.spinner("박스오피스 데이터를 불러오는 중입니다..."):
        df = load_movie_data()
except Exception as e:
    st.error(f"❌ 데이터를 불러오는 도중 오류가 발생했습니다: {e}")
    st.stop()

st.sidebar.header("⚙️ 검색 및 필터 옵션")

# 영화 목록 추출 (총 누적관객수 내림차순 정렬하여 자주 검색되는 영화 상위 배치)
movie_totals = df.groupby('영화명')['일관객'].sum().sort_values(ascending=False)
all_movies = list(movie_totals.index)

# 개별 선택 기본값 지정
selected_movie = st.sidebar.selectbox(
    "🎥 분석할 영화를 선택하세요",
    options=all_movies,
    index=0,
    help="1년 간 일별 박스오피스 10위에 등재되었던 영화 목록입니다."
)

st.sidebar.markdown("---")
st.sidebar.info(f"📊 총 **{len(all_movies)}**편의 영화 데이터가 수록되어 있습니다.")


st.header("📌 구역 1: 영화별 일관객수 시간 추이 (Line Chart)")
st.caption("선택한 영화가 개봉 후 일별로 관객 수가 어떻게 변했는지 시간 순서대로 추적합니다.")

# 선택된 영화 데이터 필터링
movie_df = df[df['영화명'] == selected_movie].sort_values('날짜_dt')

if movie_df.empty:
    st.warning("선택한 영화의 데이터가 존재하지 않습니다.")
else:
    # 핵심 통계 지표 요약 카드
    col1, col2, col3, col4 = st.columns(4)
    
    max_daily = movie_df['일관객'].max()
    max_date_row = movie_df[movie_df['일관객'] == max_daily].iloc[0]
    total_days = len(movie_df)
    last_accum = movie_df['누적관객'].max()
    
    with col1:
        st.metric("🏆 일일 최고 관객수", f"{int(max_daily):,} 명")
    with col2:
        st.metric("📅 최고 관객 달성일", max_date_row['날짜_dt'].strftime('%Y-%m-%d'))
    with col3:
        st.metric("📊 Top 10 차트인 기간", f"{total_days} 일")
    with col4:
        st.metric("🍿 최고 기록 누적 관객수", f"{int(last_accum):,} 명")

    st.write("")

    fig = px.line(
        movie_df,
        x='날짜_dt',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 일별 관객수 변화 추이",
        labels={'날짜_dt': '날짜', '일관객': '일일 관객수(명)'},
        markers=True,
        text=None
    )

    # 툴팁(Hover) 맞춤 설정
    fig.update_traces(
        hovertemplate="<b>날짜</b>: %{x|%Y년 %m월 %d일}<br><b>일관객수</b>: %{y:,}명<extra></extra>",
        line=dict(color="#FF4B4B", width=3),
        marker=dict(size=7, color="#D32F2F")
    )

    # 차트 레이아웃 미화
    fig.update_layout(
        xaxis=dict(
            title="날짜",
            showgrid=True,
            gridcolor="rgba(200, 200, 200, 0.2)",
            tickformat="%Y-%m-%d"
        ),
        yaxis=dict(
            title="일일 관객수 (명)",
            showgrid=True,
            gridcolor="rgba(200, 200, 200, 0.2)"
        ),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        height=480
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** "
        f"영화 **[{selected_movie}]**은(는) {movie_df['날짜_dt'].min().strftime('%Y년 %m월 %d일')}에 차트에 진입하여 "
        f"**{max_date_row['날짜_dt'].strftime('%Y년 %m월 %d일')}**에 정점({int(max_daily):,}명)을 찍은 후 "
        f"시간 경과에 따른 흥행 지속 또는 감소 양상을 직관적으로 보여줍니다."
    )

st.divider()

st.header("📌 구역 2: 누적 관객수 증가 곡선 (추가 예정)")
st.caption("차후 영화별 누적 관객수 누적 성장 그래프 및 상영 횟수 대비 효율 분석 그래프가 이 구역에 추가될 예정입니다.")

with st.expander("🔮 향후 추가 예정 시각화 항목 보기"):
    st.markdown("""
    - **2-1. 누적 관객수 S-커브 성숙도 분석**: 개봉 일수 경과에 따른 총 관객수 누적 증가선
    - **2-2. 스크린수 & 상영횟수 대비 일관객 효율 추이**: 상영 스크린 수 감소 시점과 관객 감소 시점 비교
    - **2-3. 다중 영화 시간대별 관객수 비교**: 여러 영화를 동시에 선택하여 흥행 속도 비교
    """)
