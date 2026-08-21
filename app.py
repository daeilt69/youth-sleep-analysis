import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="청소년 수면시간 분석 앱", layout="wide")
st.title("📱 수면 부족 대한민국 청소년: 폰 때문일까, 학원 때문일까?")
st.subheader("청소년 건강행태조사 데이터를 활용한 분석")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('survey_data_100.csv')
    except Exception as e:
        st.error("데이터 파일을 읽을 수 없습니다.")
        return pd.DataFrame()

    # 컬럼명 자동 매핑
    sleep_col = None
    for col in ['주중_평균_수면시간', '수면시간']:
        if col in df.columns:
            sleep_col = col
            break
            
    if not sleep_col or '스마트폰_사용시간' not in df.columns:
        st.error("CSV 파일에 '스마트폰_사용시간' 또는 '수면시간' 컬럼이 없습니다.")
        return pd.DataFrame()
        
    df['주중_평균_수면시간'] = df[sleep_col]
    df_clean = df.dropna(subset=['주중_평균_수면시간', '스마트폰_사용시간']).copy()
    valid_sleep = (df_clean['주중_평균_수면시간'] > 0) & (df_clean['주중_평균_수면시간'] < 24)
    return df_clean[valid_sleep]

df_clean = load_data()

if df_clean.empty:
    st.warning("표시할 데이터가 없습니다.")
else:
    st.sidebar.header("🔍 데이터 필터링")
    grade_options = ["전체"] + sorted([f"{g}학년" for g in df_clean['학년'].unique()])
    selected_grade = st.sidebar.selectbox("학년을 선택하세요", grade_options)

    if selected_grade == "전체":
        filtered_df = df_clean
    else:
        grade_num = int(selected_grade.replace("학년", ""))
        filtered_df = df_clean[df_clean['학년'] == grade_num]

    col1, col2, col3 = st.columns(3)
    col1.metric("📊 분석 대상 학생 수", f"{len(filtered_df)} 명")
    col2.metric("🌙 평균 수면시간", f"{filtered_df['주중_평균_수면시간'].mean():.2f} 시간")
    col3.metric("📲 평균 스마트폰 사용시간", f"{filtered_df['스마트폰_사용시간'].mean():.2f} 시간")

    st.divider()
    st.subheader(f"📈 [{selected_grade}] 스마트폰 사용시간 vs 수면시간 산점도")

    fig = px.scatter(
        filtered_df, 
        x='스마트폰_사용시간', 
        y='주중_평균_수면시간', 
        color='학년',
        hover_data={'학년': True, '주중_평균_수면시간': ':.1f시간', '스마트폰_사용시간': ':.1f시간'},
        template='plotly_white', 
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        xaxis_title='스마트폰 사용시간(시간)', 
        yaxis_title='주중 평균 수면시간(시간)', 
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 인사이트: 두 변수의 상관계수를 확인해 보세요.")
