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
    "🎥 [구역 1] 분석할 영화를 선택하세요",
    options=all_movies,
    index=0,
    help="1년 간 일별 박스오피스 10위에 등재되었던 영화 목록입니다."
)

st.sidebar.markdown("---")
st.sidebar.info(f"📊 총 **{len(all_movies)}**편의 영화 데이터가 수록되어 있습니다.")


# ==========================================
# 📌 구역 1: 개별 영화 일관객수 시간 추이
# ==========================================
st.header("📌 구역 1: 단일 영화 일관객수 시간 추이 (Line Chart)")
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

    fig1 = px.line(
        movie_df,
        x='날짜_dt',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 일별 관객수 변화 추이",
        labels={'날짜_dt': '날짜', '일관객': '일일 관객수(명)'},
        markers=True
    )

    # 툴팁(Hover) 맞춤 설정
    fig1.update_traces(
        hovertemplate="<b>날짜</b>: %{x|%Y년 %m월 %d일}<br><b>일관객수</b>: %{y:,}명<extra></extra>",
        line=dict(color="#FF4B4B", width=3),
        marker=dict(size=7, color="#D32F2F")
    )

    # 차트 레이아웃 미화
    fig1.update_layout(
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
        height=450
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** "
        f"영화 **[{selected_movie}]**은(는) {movie_df['날짜_dt'].min().strftime('%Y년 %m월 %d일')}에 차트에 진입하여 "
        f"**{max_date_row['날짜_dt'].strftime('%Y년 %m월 %d일')}**에 최고 관객수({int(max_daily):,}명)를 기록한 후 "
        f"시간 경과에 따라 흥행 선호도가 변화하는 흐름을 직관적으로 확인할 수 있습니다."
    )

st.divider()


# ==========================================
# 📌 구역 2: Top 5 흥행작 일관객수 비교
# ==========================================
st.header("📌 구역 2: 흥행 Top 5 영화의 일관객수 시간 비교 (Multi-Line Chart)")
st.caption("해당 기간 동안 일관객수 합계가 가장 컸던 상위 5개 영화의 관객수 추이를 한 그래프에서 함께 비교합니다.")

# 일관객 합계 상위 5개 영화 선정
top5_movies = movie_totals.head(5).index.tolist()
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜_dt')

# Top 5 목록 안내 Badge
top5_str = "  ·  ".join([f"**{i+1}위**: {m}" for i, m in enumerate(top5_movies)])
st.markdown(f"🏆 **기간 내 최고 흥행 Top 5 영화:** {top5_str}")
st.write("")

fig2 = px.line(
    top5_df,
    x='날짜_dt',
    y='일관객',
    color='영화명',
    title="<b>Top 5 흥행작 일별 관객수 시간 추이 비교</b>",
    labels={'날짜_dt': '날짜', '일관객': '일일 관객수(명)', '영화명': '영화 제목'},
    markers=True
)

# 다중 라인 hover 및 미화 설정
fig2.update_traces(
    hovertemplate="<b>%{data.name}</b><br>날짜: %{x|%Y년 %m월 %d일}<br>일관객수: %{y:,}명<extra></extra>",
    marker=dict(size=6)
)

fig2.update_layout(
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
    legend=dict(
        title="🎬 영화 선택 (클릭 시 토글)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=50, b=20),
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

# Top 1 영화 및 개봉 시기 정리
top1_movie = top5_movies[0]
st.info(
    f"💡 **이 그래프로 알 수 있는 것:** "
    f"기간 내 전체 1위 흥행작인 **[{top1_movie}]**을 비롯한 Top 5 영화들의 개봉 시기별 관객 집중 폭발 시점과 "
    f"영화 간 흥행 정점(Peak)의 높이 및 상영 유지 기간의 차이를 서로 비교해 볼 수 있습니다. "
    f"(오른쪽 상단 범례의 영화 이름을 클릭하면 특정 영화의 선을 켜거나 끌 수 있습니다.)"
)

st.divider()

st.header("📌 구역 3: 누적 관객수 성장 곡선 (추가 예정)")
st.caption("차후 개봉 일수 경과에 따른 S-커브 성숙도 분석 및 스크린 수 대비 관객 효율 분석 그래프가 추가될 예정입니다.")
