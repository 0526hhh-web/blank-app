#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

/* 전체 패딩 */
[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* 🔁 메트릭 카드 가독성 개선: 흰 배경 + 테두리 + 그림자 */
[data-testid="stMetric"] {
    background-color: #ffffff !important;   /* ← 검정에서 흰색으로 변경 */
    color: #111 !important;
    text-align: center;
    padding: 15px 0;
    border: 1px solid #e9e9e9;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* 라벨/값/델타 텍스트 컬러 */
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  color: #111 !important;
  font-weight: 600;
}

/* 값(퍼센트 등) 컬러 */
[data-testid="stMetricValue"] {
  color: #111 !important;
}

/* 델타 아이콘 위치 유지 */
[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

/* 델타 텍스트 색상 보정(상/하 모두 가독성 있게) */
[data-testid="stMetricDelta"] {
  color: #0f5132 !important;  /* 진한 초록 */
  font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv') ## 분석 데이터 넣기


#######################
# Sidebar
with st.sidebar:
    # -----------------------------
    # 앱 타이틀 & 간단 설명
    # -----------------------------
    st.title("Titanic Survival Dashboard")
    st.caption("필터를 선택해 생존률 분석을 탐색하세요.")

    # -----------------------------
    # 기본 정보
    # -----------------------------
    st.markdown("**데이터 요약**")
    st.write(f"총 승객 수: **{len(df_reshaped):,}**")

    st.markdown("---")
    st.subheader("필터")

    # -----------------------------
    # 객실 등급, 성별, 승선 항구
    # -----------------------------
    pclass_opts = sorted(df_reshaped["Pclass"].dropna().unique().tolist())
    pclass_sel = st.multiselect(
        "Pclass (객실 등급)",
        options=pclass_opts,
        default=pclass_opts,
        help="분석할 객실 등급을 선택하세요."
    )

    sex_opts = sorted(df_reshaped["Sex"].dropna().unique().tolist())
    sex_sel = st.multiselect(
        "Sex (성별)",
        options=sex_opts,
        default=sex_opts,
        help="분석할 성별을 선택하세요."
    )

    embarked_series = df_reshaped["Embarked"]
    embarked_opts = sorted(embarked_series.dropna().unique().tolist())
    include_embarked_na = st.checkbox("승선 항구 결측 포함", value=False)
    embarked_sel = st.multiselect(
        "Embarked (승선 항구)",
        options=embarked_opts,
        default=embarked_opts,
        help="C = Cherbourg, Q = Queenstown, S = Southampton"
    )

    # -----------------------------
    # 나이, 운임(Fare) 범위
    # -----------------------------
    st.markdown("### 연령/운임 범위")

    age_min = int(df_reshaped["Age"].min(skipna=True))
    age_max = int(df_reshaped["Age"].max(skipna=True))
    age_range = st.slider(
        "Age (나이 범위)",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
        help="해당 범위의 나이만 포함합니다. (결측치는 아래 옵션으로 처리)"
    )

    fare_min = float(df_reshaped["Fare"].min(skipna=True))
    fare_max = float(df_reshaped["Fare"].max(skipna=True))
    fare_range = st.slider(
        "Fare (운임 범위)",
        min_value=float(fare_min),
        max_value=float(fare_max),
        value=(float(fare_min), float(fare_max)),
        help="해당 범위의 운임만 포함합니다."
    )

    # -----------------------------
    # 가족 동승 여부
    # -----------------------------
    st.markdown("### 가족 동승 여부")
    family_mode = st.radio(
        "가족 동승 필터",
        options=["전체", "가족 동승", "혼자"],
        horizontal=True,
        help="SibSp + Parch > 0 이면 '가족 동승'으로 간주합니다."
    )

    # -----------------------------
    # 결측치 처리 옵션
    # -----------------------------
    st.markdown("### 결측치 처리")
    age_missing_policy = st.selectbox(
        "나이(Age) 결측 처리",
        options=["포함(제외 안 함)", "제외", "중앙값으로 대체"],
        index=0,
        help="시각화/계산 시 나이 결측치를 어떻게 다룰지 선택하세요."
    )

    cabin_include_na = st.checkbox("Cabin 결측 포함(필터 시 사용될 수 있음)", value=True)

    # -----------------------------
    # 색상/테마
    # -----------------------------
    st.markdown("### 테마")
    color_theme = st.selectbox(
        "색상 테마",
        options=["blues", "greens", "reds", "purples", "greys"],
        index=0,
        help="차트 색상 팔레트를 선택하세요."
    )

    # -----------------------------
    # 필터 적용 & 초기화
    # -----------------------------
    apply_filters = st.button("필터 적용", use_container_width=True)
    reset_filters = st.button("초기화", use_container_width=True)

    if reset_filters:
        st.experimental_rerun()

    # -----------------------------
    # 실제 필터링 로직 (세션에 저장)
    # -----------------------------
    df_side = df_reshaped.copy()

    # Age 결측 처리 정책
    if age_missing_policy == "제외":
        df_side = df_side[~df_side["Age"].isna()]
    elif age_missing_policy == "중앙값으로 대체":
        median_age = df_side["Age"].median(skipna=True)
        df_side["Age"] = df_side["Age"].fillna(median_age)

    # 기본 필터
    if pclass_sel:
        df_side = df_side[df_side["Pclass"].isin(pclass_sel)]
    if sex_sel:
        df_side = df_side[df_side["Sex"].isin(sex_sel)]

    # Embarked 필터
    if embarked_sel:
        if include_embarked_na:
            df_side = df_side[(df_side["Embarked"].isin(embarked_sel)) | (df_side["Embarked"].isna())]
        else:
            df_side = df_side[df_side["Embarked"].isin(embarked_sel)]
    else:
        if not include_embarked_na:
            df_side = df_side[~df_side["Embarked"].isna()]

    # 범위 필터: Age, Fare
    df_side = df_side[
        (df_side["Age"].between(age_range[0], age_range[1], inclusive="both")) &
        (df_side["Fare"].between(fare_range[0], fare_range[1], inclusive="both"))
    ]

    # 가족 동승 여부
    fam_count = (df_side["SibSp"] + df_side["Parch"])
    if family_mode == "가족 동승":
        df_side = df_side[fam_count > 0]
    elif family_mode == "혼자":
        df_side = df_side[fam_count == 0]

    # 필터 결과 요약
    st.markdown("---")
    st.metric(label="필터 후 승객 수", value=f"{len(df_side):,}")

    # 세션 스테이트로 전달 (메인 패널에서 사용)
    st.session_state["filters"] = {
        "pclass": pclass_sel,
        "sex": sex_sel,
        "embarked": embarked_sel,
        "include_embarked_na": include_embarked_na,
        "age_range": age_range,
        "fare_range": fare_range,
        "family_mode": family_mode,
        "age_missing_policy": age_missing_policy,
        "cabin_include_na": cabin_include_na,
        "color_theme": color_theme,
    }
    st.session_state["df_filtered"] = df_side



#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.subheader("🚢 Survival Overview")

    df_filtered = st.session_state.get("df_filtered", df_reshaped)

    # 전체 생존률
    total_survived = df_filtered["Survived"].sum()
    total_passengers = len(df_filtered)
    survival_rate = total_survived / total_passengers * 100 if total_passengers > 0 else 0

    st.metric(
        label="전체 생존률",
        value=f"{survival_rate:.1f}%",
        delta=f"{total_survived} / {total_passengers}"
    )

    st.markdown("---")

    # 성별 생존률
    st.subheader("성별 생존률")
    sex_summary = df_filtered.groupby("Sex")["Survived"].mean().reset_index()
    for _, row in sex_summary.iterrows():
        st.metric(
            label=row["Sex"].capitalize(),
            value=f"{row['Survived']*100:.1f}%"
        )

    st.markdown("---")

    # 객실 등급별 생존률
    st.subheader("객실 등급별 생존률")
    pclass_summary = df_filtered.groupby("Pclass")["Survived"].mean().reset_index()
    for _, row in pclass_summary.iterrows():
        st.metric(
            label=f"{int(row['Pclass'])}등실",
            value=f"{row['Survived']*100:.1f}%"
        )

    st.markdown("---")

    # 가족 동승 여부
    st.subheader("가족 동승 여부")
    df_filtered = df_filtered.copy()
    df_filtered["Family"] = (df_filtered["SibSp"] + df_filtered["Parch"]) > 0
    fam_summary = df_filtered.groupby("Family")["Survived"].mean().reset_index()
    for _, row in fam_summary.iterrows():
        label = "가족 동승" if row["Family"] else "혼자"
        st.metric(label=label, value=f"{row['Survived']*100:.1f}%")

with col[1]:
    st.subheader("📊 시각화 패널")

    df_filtered = st.session_state.get("df_filtered", df_reshaped).copy()
    color_theme = st.session_state.get("filters", {}).get("color_theme", "blues")

    # Plotly 색상 스케일 매핑
    scale_map = {
        "blues": "Blues",
        "greens": "Greens",
        "reds": "Reds",
        "purples": "Purples",
        "greys": "Greys",
    }
    px_scale = scale_map.get(color_theme, "Blues")

    # 1) 연령대 × 객실등급 생존률 히트맵
    st.markdown("#### 연령대 × 객실등급 생존률 (Heatmap)")
    age_bins = [0, 12, 18, 30, 45, 60, 80]
    age_labels = ["0-11", "12-17", "18-29", "30-44", "45-59", "60+"]
    df_filtered["AgeGroup"] = pd.cut(df_filtered["Age"], bins=age_bins, labels=age_labels, include_lowest=True)

    heat = (
        df_filtered.dropna(subset=["AgeGroup"])
        .groupby(["Pclass", "AgeGroup"])["Survived"]
        .mean()
        .reset_index()
    )
    heat_pivot = heat.pivot(index="Pclass", columns="AgeGroup", values="Survived").sort_index(ascending=True)

    fig_heat = px.imshow(
        heat_pivot * 100,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=px_scale,
        labels=dict(color="생존률(%)"),
        title="객실등급별·연령대별 평균 생존률 (%)"
    )
    fig_heat.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")

    # 2) 승선 항구별 생존률 막대그래프
    st.markdown("#### 승선 항구(Embarked)별 평균 생존률")
    embark_map = {"C": "Cherbourg (C)", "Q": "Queenstown (Q)", "S": "Southampton (S)"}
    emb = (
        df_filtered.dropna(subset=["Embarked"])
        .groupby("Embarked")["Survived"]
        .mean()
        .mul(100)
        .reset_index()
    )
    emb["EmbarkedLabel"] = emb["Embarked"].map(embark_map).fillna(emb["Embarked"])

    fig_emb = px.bar(
        emb,
        x="EmbarkedLabel",
        y="Survived",
        text=emb["Survived"].round(1).astype(str) + "%",
        color="EmbarkedLabel",
        color_discrete_sequence=px.colors.sequential.__dict__.get(px_scale, px.colors.sequential.Blues),
        labels={"EmbarkedLabel": "승선 항구", "Survived": "생존률(%)"},
        title="승선 항구별 평균 생존률 (%)"
    )
    fig_emb.update_traces(textposition="outside")
    fig_emb.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10), yaxis_range=[0, 100])
    st.plotly_chart(fig_emb, use_container_width=True)

    st.markdown("---")

    # 3) 생존자 vs 사망자 나이 분포 (히스토그램)
    st.markdown("#### 생존자 vs 사망자 나이 분포")
    age_dist = df_filtered.dropna(subset=["Age"]).copy()
    age_dist["Outcome"] = age_dist["Survived"].map({1: "Survived", 0: "Died"})

    fig_hist = px.histogram(
        age_dist,
        x="Age",
        nbins=30,
        color="Outcome",
        barmode="overlay",
        opacity=0.6,
        labels={"Age": "나이(Age)"},
        title="생존 여부에 따른 나이 분포"
    )
    fig_hist.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)

with col[2]:
    st.subheader("🔎 상세 분석")

    df_filtered = st.session_state.get("df_filtered", df_reshaped).copy()

    # 1) Top Groups (생존률 상위 그룹)
    st.markdown("#### 생존률 상위 그룹 Top 5")
    age_bins = [0, 12, 18, 30, 45, 60, 80]
    age_labels = ["0-11", "12-17", "18-29", "30-44", "45-59", "60+"]
    df_filtered["AgeGroup"] = pd.cut(df_filtered["Age"], bins=age_bins, labels=age_labels, include_lowest=True)

    group_summary = (
        df_filtered.dropna(subset=["AgeGroup"])
        .groupby(["Sex", "Pclass", "AgeGroup"])["Survived"]
        .mean()
        .mul(100)
        .reset_index()
    )
    top_groups = group_summary.sort_values("Survived", ascending=False).head(5)

    for _, row in top_groups.iterrows():
        st.metric(
            label=f"{row['Sex'].capitalize()}, {int(row['Pclass'])}등실, {row['AgeGroup']}",
            value=f"{row['Survived']:.1f}%"
        )

    st.markdown("---")

    # 2) 운임(Fare) 분석 (Boxplot)
    st.markdown("#### 운임(Fare) 분포와 생존 여부")
    fare_box = df_filtered.copy()
    fare_box["Outcome"] = fare_box["Survived"].map({1: "Survived", 0: "Died"})

    if not fare_box.empty:
        fig_fare = px.box(
            fare_box,
            x="Outcome",
            y="Fare",
            color="Outcome",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            points="all",
            labels={"Outcome": "생존 여부", "Fare": "운임"},
            title="생존 여부에 따른 운임(Fare) 분포"
        )
        fig_fare.update_layout(showlegend=False, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_fare, use_container_width=True)
    else:
        st.info("선택된 조건에 해당하는 데이터가 없습니다.")

    st.markdown("---")

    # 3) About 섹션
    st.markdown("#### ℹ️ About")
    st.markdown("""
    - **데이터 출처**: Kaggle Titanic dataset
    - **분석 목적**:
        - 타이타닉호 승객의 생존 여부에 영향을 준 요인 파악  
        - 성별, 나이, 객실 등급, 가족 동반 여부, 승선 항구 등 주요 요인 분석  
    - **대시보드 구성**:  
        - **칼럼1**: 요약 지표 (생존률, 성별/등급별/가족 여부별)  
        - **칼럼2**: 시각화 (히트맵, 막대, 히스토그램)  
        - **칼럼3**: 상세 분석 (Top 그룹, 운임 분포, 설명)
    """)
