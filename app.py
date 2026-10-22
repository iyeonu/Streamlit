import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="나만의 맞춤 여행지 추천 앱",
    page_icon="✈️",
    layout="wide"
)

# 2. 내장 여행지 데이터 (API/공공데이터 없이 자체 정의)
@st.cache_data
def load_travel_data():
    data = [
        {"이름": "제주도", "카테고리": "자연/휴양", "예산": 35, "기간": "3박 4일", "계절": "봄/가을", "위도": 33.4996, "경도": 126.5312, "설명": "푸른 바다와 한라산, 맛있는 음식이 가득한 국내 대표 휴양지"},
        {"이름": "강릉", "카테고리": "자연/휴양", "예산": 20, "기간": "1박 2일", "계절": "여름", "위도": 37.7519, "경도": 128.8761, "설명": "시원한 동해 바다와 안목해변 커피거리, 초당순두부가 유명한 곳"},
        {"이름": "경주", "카테고리": "역사/문화", "예산": 25, "기간": "2박 3일", "계절": "봄/가을", "위도": 35.8562, "경도": 129.2247, "설명": "첨성대, 안압지 등 천년 고도의 역사적 숨결과 황리단길의 감성"},
        {"이름": "부산", "카테고리": "도시/식도락", "예산": 30, "기간": "2박 3일", "계절": "여름", "위도": 35.1796, "경도": 129.0756, "설명": "해운대, 광안리 야경과 함께 즐기는 신선한 해산물과 돼지국밥"},
        {"이름": "여수", "카테고리": "자연/휴양", "예산": 25, "기간": "2박 3일", "계절": "여름/가을", "위도": 34.7604, "경도": 127.6622, "설명": "여수 밤바다와 돌산대교 야경, 케이블카를 즐길 수 있는 로맨틱한 도시"},
        {"이름": "전주", "카테고리": "도시/식도락", "예산": 18, "기간": "1박 2일", "계절": "봄/가을", "위도": 35.8242, "경도": 127.1480, "설명": "한옥마을 산책과 비빔밥, 콩나물국밥 등 먹거리가 풍부한 식도락 여행지"},
        {"이름": "도쿄", "카테고리": "도시/식도락", "예산": 80, "기간": "3박 4일", "계절": "사계절", "위도": 35.6762, "경도": 139.6503, "설명": "쇼핑, 테마파크, 최첨단 도시 문화와 다채로운 미식을 한 번에 경험"},
        {"이름": "교토", "카테고리": "역사/문화", "예산": 75, "기간": "3박 4일", "계절": "봄/가을", "위도": 35.0116, "경도": 135.7681, "설명": "고즈넉한 신사와 금각사, 단풍과 벚꽃이 어우러지는 전통적인 풍경"},
        {"이름": "방콕", "카테고리": "도시/식도락", "예산": 60, "기간": "4박 5일", "계절": "겨울", "위도": 13.7563, "경도": 100.5018, "설명": "화려한 왕궁과 스트리트 푸드, 합리적인 가격의 스파와 야시장"},
        {"이름": "발리", "카테고리": "자연/휴양", "예산": 120, "기간": "5박 6일", "계절": "여름", "위도": -8.4095, "경도": 115.1889, "설명": "평화로운 서핑 해변과 우붓의 초록빛 정글, 웰니스 리조트의 천국"},
        {"이름": "스위스 인터라켄", "카테고리": "액티비티", "예산": 250, "기간": "6박 7일", "계절": "여름/겨울", "위도": 46.6863, "경도": 7.8632, "설명": "융프라우요흐와 알프스 산맥의 압도적인 자연경관, 패러글라이딩 명소"},
        {"이름": "파리", "카테고리": "역사/문화", "예산": 220, "기간": "5박 6일", "계절": "봄/가을", "위도": 48.8566, "경도": 2.3522, "설명": "에펠탑과 루브르 박물관, 세느강변의 낭만이 흐르는 예술의 도시"}
    ]
    return pd.DataFrame(data)

df = load_travel_data()

# 3. 타이틀 및 안내
st.title("✈️ 취향 맞춤 여행지 추천 서비스")
st.markdown("원하는 **여행 스타일**, **예산**, **선호 계절**을 설정하면 최적의 여행지를 추천해 드립니다.")
st.divider()

# 4. 사이드바 - 사용자 조건 필터링
st.sidebar.header("🎯 여행 조건 선택")

# 카테고리 필터
categories = ["전체"] + list(df["카테고리"].unique())
selected_category = st.sidebar.selectbox("여행 테마", categories)

# 예산 범위 필터 (슬라이더)
max_budget_input = int(df["예산"].max())
selected_max_budget = st.sidebar.slider(
    "1인당 1일 예상 예산 (만원 이내)",
    min_value=10,
    max_value=max_budget_input,
    value=150,
    step=10
)

# 계절 필터
seasons = ["상관없음", "봄/가을", "여름", "겨울", "사계절"]
selected_season = st.sidebar.radio("추천 계절", seasons)

# 5. 데이터 필터링 로직
filtered_df = df[df["예산"] <= selected_max_budget]

if selected_category != "전체":
    filtered_df = filtered_df[filtered_df["카테고리"] == selected_category]

if selected_season != "상관없음":
    filtered_df = filtered_df[filtered_df["계절"].str.contains(selected_season, na=False) | (filtered_df["계절"] == "사계절")]

# 6. 대시보드 요약 지표 (Metrics)
col1, col2, col3 = st.columns(3)
col1.metric("조건에 맞는 여행지", f"{len(filtered_df)} 곳")
if not filtered_df.empty:
    col2.metric("평균 필요 예산", f"{int(filtered_df['예산'].mean())} 만원")
    col3.metric("가장 인접한 대표 테마", filtered_df['카테고리'].mode()[0] if not filtered_df['카테고리'].empty else "-")
else:
    col2.metric("평균 필요 예산", "0 만원")
    col3.metric("가장 인접한 대표 테마", "-")

st.divider()

# 7. 추천 결과 출력
if filtered_df.empty:
    st.warning("⚠️ 설정한 조건에 맞는 여행지가 없습니다. 예산을 늘리거나 다른 테마를 선택해 보세요!")
else:
    tab1, tab2, tab3 = st.tabs(["📌 추천 카드 목록", "🗺️ 지도 보기", "📊 예산 비교"])

    with tab1:
        # 카드 형태로 목록 출력
        cols = st.columns(2)
        for idx, row in filtered_df.reset_index().iterrows():
            with cols[idx % 2]:
                with st.container(border=True):
                    st.subheader(f"📍 {row['이름']}")
                    st.write(f"**테마:** {row['카테고리']} | **추천 기간:** {row['기간']}")
                    st.write(f"**예상 예산:** 약 {row['예산']}만원 / **추천 계절:** {row['계절']}")
                    st.caption(row['설명'])

    with tab2:
        # 지도 인터랙티브 시각화 (Plotly)
        st.subheader("🌐 추천 여행지 위치")
        fig = px.scatter_mapbox(
            filtered_df,
            lat="위도",
            lon="경도",
            hover_name="이름",
            hover_data=["카테고리", "예산", "기간"],
            color="카테고리",
            zoom=1,
            height=500
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0, "t":0, "l":0, "b":0}
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        # 예산 비교 바 차트 (Plotly)
        st.subheader("💰 여행지별 예상 예산 비교")
        fig_bar = px.bar(
            filtered_df,
            x="이름",
            y="예산",
            color="카테고리",
            text="예산",
            labels={"이름": "여행지", "예산": "예산 (만원)"},
            title="조건 내 여행지 예산 비교"
        )
        fig_bar.update_traces(texttemplate='%{text}만원', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
