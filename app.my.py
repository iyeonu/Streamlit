import json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 0. 기본 페이지 설정 및 사이드바 발표자 정보 (조건 5)
# ==============================================================================
st.set_page_config(
    page_title="과학 탐구 발표 - 효소 반응 속도 시뮬레이션",
    page_icon="🧬",
    layout="wide",
)

# 사이드바 발표자 정보
st.sidebar.title("📌 발표자 정보")
st.sidebar.markdown(
    """
- **발표자:** 【학년 반 이름】
- **분야:** 【생명과학】
- **주제:** 【기질 농도에 따른 효소 반응 속도 및 포화 현상 분석】
"""
)

# ==============================================================================
# [시뮬레이션 표시 코드] (수정 없이 그대로 포함 - 조건 4)
# ==============================================================================
GLOWSCRIPT = "https://www.glowscript.org"

PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<link type="text/css" href="__GS__/css/redmond/2.1/jquery-ui.custom.css" rel="stylesheet" />
<link type="text/css" href="__GS__/css/ide.css" rel="stylesheet" />
<script src="__GS__/lib/jquery/2.1/jquery.min.js"></script>
<script src="__GS__/lib/jquery/2.1/jquery-ui.custom.min.js"></script>
<script src="__GS__/package/glow.3.2.min.js"></script>
<script src="__GS__/package/RScompiler.3.2.min.js"></script>
<script src="__GS__/package/RSrun.3.2.min.js"></script>
<style>
  body { background: white; margin: 0; padding: 8px; font-family: sans-serif; }
  #error { color: #c00; white-space: pre-wrap; font-family: monospace; }
</style>
</head><body>
<div id="error"></div>
<div id="glowscript" class="glowscript"></div>
<script>
function showError(msg) {
  document.getElementById("error").textContent = "시뮬레이션 오류: " + msg;
}
window.onerror = function (msg) { showError(msg); };
try {
  var source = __SOURCE__;
  var js = glowscript_compile(source, {lang: "vpython", version: "3.2"});
  window.__context = { glowscript_container: $("#glowscript").removeAttr("id") };
  (0, eval)(js + ";window.__main = __main__;");
  var result = window.__main();
  if (result && result.catch) result.catch(function (e) { showError(e); });
} catch (e) {
  showError(e);
}
</script>
</body></html>
"""


def show_vpython(code, height=800):
    source_js = json.dumps(code.strip()).replace("</", "<\\/")
    html = PAGE.replace("__GS__", GLOWSCRIPT).replace("__SOURCE__", source_js)
    components.html(html, height=height, scrolling=True)


# ==============================================================================
# [내 VPython 코드] (문자열 그대로 보존 - 조건 3)
# ==============================================================================
VPYTHON_CODE = r"""Web VPython 3.2


# ==============================================================================
# 1. 3D 캔버스 및 그래프 설정
# ==============================================================================
scene = canvas(
    title='[생명과학Ⅰ] 효소 반응 속도 및 포화 현상 3D 시뮬레이션',
    width=800, height=500,
    center=vector(0, 0, 0),
    background=color.gray(0.1)
)

# 반응 속도 그래프 (기질 농도 [S] vs 생성물 생성 속도 v)
rate_graph = graph(
    title='Enzyme Kinetics: Substrate Concentration [S] vs Rate (v)',
    xtitle='Substrate Concentration [S]', ytitle='Reaction Rate (Product/sec)',
    width=800, height=250,
    background=color.black, foreground=color.white
)
f_rate = gcurve(color=color.cyan, width=2, label='Measured Rate (v)')
f_theoretical = gcurve(color=color.yellow, width=1, label='Theoretical Vmax line')

# ==============================================================================
# 2. 효소(Enzyme) 및 기질(Substrate) 3D 객체 생성
# ==============================================================================
num_enzymes = 6      # 제한된 효소 수 (Vmax 한계 형성 원인)
num_substrates = 60  # 기질 분자 수

enzymes = []
substrates = []

# 효소 생성 (큰 파란색 구체, 활성 부위 표현)
for i in range(num_enzymes):
    pos = vector(random() * 6 - 3, random() * 6 - 3, random() * 6 - 3)
    e = sphere(pos=pos, radius=0.4, color=color.blue, opacity=0.8)
    e.v = vector(0, 0, 0)
    e.is_bound = False
    e.bind_timer = 0
    enzymes.append(e)

# 기질 생성 (작은 녹색 구체)
for i in range(num_substrates):
    pos = vector(random() * 8 - 4, random() * 8 - 4, random() * 8 - 4)
    s = sphere(pos=pos, radius=0.15, color=color.green)
    s.v = vector(random() - 0.5, random() - 0.5, random() - 0.5) * 2.0
    s.is_product = False
    substrates.append(s)

# 반응 용기 (경계 상자)
container = box(pos=vector(0, 0, 0), size=vector(10, 10, 10), opacity=0.1, color=color.white)

# 안내 텍스트
info = label(
    pos=vector(0, 5.5, 0),
    text='Active Enzymes: 0 / 6 | Products Created: 0',
    height=16, box=False, color=color.white
)

# ==============================================================================
# 3. 물리 및 효소 반응 파라미터
# ==============================================================================
dt = 0.02
t = 0.0
product_count = 0
bound_enzymes_count = 0

# ==============================================================================
# 4. 메인 시뮬레이션 루프
# ==============================================================================
while True:
    rate(50)  # 초당 50회 실행
    
    bound_enzymes_count = 0
    
    # 1) 기질 및 생성물 이동 (브라운 운동)
    for s in substrates:
        s.pos = s.pos + s.v * dt
        
        # 용기 벽 충돌 처리
        if abs(s.pos.x) > 4.8: s.v.x *= -1
        if abs(s.pos.y) > 4.8: s.v.y *= -1
        if abs(s.pos.z) > 4.8: s.v.z *= -1

    # 2) 효소-기질 결합 및 생성물(Product) 전환 로직
    for e in enzymes:
        if not e.is_bound:
            # 자유 효소 상태: 근접한 기질 탐색
            for s in substrates:
                if not s.is_product and mag(e.pos - s.pos) < 0.5:
                    # 결합 발생 (효소-기질 복합체 ES 형성)
                    e.is_bound = True
                    e.bound_substrate = s
                    e.color = color.yellow  # ES 복합체 상태 시각화
                    s.visible = False       # 기질이 효소 내부로 결합
                    break
        else:
            # 효소-기질 복합체 상태: 타이머 진행 후 생성물 분리
            bound_enzymes_count += 1
            e.bind_timer += dt
            
            if e.bind_timer >= 1.0:  # 반응 완료에 걸리는 시간 (1초)
                # 생성물(Product) 배출 (노란색/빨간색 분자로 변환)
                p = e.bound_substrate
                p.pos = e.pos + vector(0.5, 0, 0)
                p.visible = True
                p.color = color.red  # 생성물(Product)로 변환
                p.is_product = True
                p.v = vector(random() - 0.5, random() - 0.5, random() - 0.5) * 3.0
                
                # 효소 재사용 (기질 분해 후 원래 상태로 복귀)
                e.is_bound = False
                e.color = color.blue
                e.bind_timer = 0
                product_count += 1

    # 3) 실시간 정보 및 그래프 업데이트
    info.text = 'Active Enzymes (Bound): ' + bound_enzymes_count + ' / ' + num_enzymes + ' | Total Products: ' + product_count
    
    # 반응 속도 추적 (주기적으로 그래프에 플롯)
    if int(t / dt) % 10 == 0:
        current_substrate_conc = sum(1 for s in substrates if not s.is_product)
        f_rate.plot(current_substrate_conc, bound_enzymes_count * 1.5)
        f_theoretical.plot(current_substrate_conc, num_enzymes * 1.5)

    t += dt
"""

# ==============================================================================
# 메인 화면 타이틀
# ==============================================================================
st.title("🧬 [생명과학Ⅰ] 효소 반응 속도 및 포화 현상 탐구")
st.markdown("---")

# ==============================================================================
# 6개 탭 구성 (조건 6)
# ==============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "① 탐구 질문",
        "② 시뮬레이션",
        "③ 원리",
        "④ 결과 분석",
        "⑤ 결론과 한계",
        "⑥ 퀴즈",
    ]
)

# ------------------------------------------------------------------------------
# ① 탐구 질문 (가설 포함)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("❓ 탐구 질문 및 가설")
    st.markdown(
        """
    ### 📌 탐구 질문
    - **질문:** 기질 농도가 증가함에 따라 효소의 반응 속도는 계속 일정하게 증가할까, 아니면 특정 한계에 도달할까?
    
    ### 💡 탐구 가설
    - **가설:** 초기에는 기질 농도가 증가함에 따라 효소와 기질의 충돌 빈도가 높아져 반응 속도가 비례하여 증가하지만, 제한된 효소 수로 인해 일정 농도 이상에서는 모든 효소가 포화 상태에 도달하여 최대 반응 속도($V_{max}$)에 수렴할 것이다.
    """
    )

# ------------------------------------------------------------------------------
# ② 시뮬레이션 (사용 방법 한 줄 + show_vpython)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🎮 효소 반응 3D 시뮬레이션")
    # 사용 방법 한 줄 작성 (조건 6-②)
    st.info(
        "💡 **사용 방법:** 아래 시뮬레이션 창을 3D 마우스 드래그로 회전/확대하여 효소(파란색)와 기질(녹색)의 결합 및 포화 상태를 관찰합니다."
    )
    show_vpython(VPYTHON_CODE, height=900)

# ------------------------------------------------------------------------------
# ③ 원리 (수식은 st.latex)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("🧪 반응 원리 및 수식")
    st.markdown(
        """
    ### 1. 효소-기질 반응 메커니즘
    효소($E$)와 기질($S$)이 결합하여 효소-기질 복합체($ES$)를 형성한 후, 반응이 진행되어 생성물($P$)을 배출하고 효소는 재사용됩니다.
    """
    )

    st.latex(r"E + S \rightleftharpoons ES \rightarrow E + P")

    st.markdown(
        """
    ### 2. 미카엘리스-멘텐 방정식 (Michaelis-Menten Kinetics)
    기질 농도 $[S]$에 따른 초기 반응 속도 $v$의 변화를 정량적으로 설명하는 대표적인 효소 반응 속도론 수식입니다.
    """
    )

    st.latex(r"v = \frac{V_{max} [S]}{K_m + [S]}")

    st.markdown(
        """
    - **$v$**: 초기 반응 속도
    - **$V_{max}$**: 최대 반응 속도 (모든 효소가 포화된 상태)
    - **$[S]$**: 기질 농도
    - **$K_m$**: 미카엘리스 상수 (반응 속도가 $\\frac{1}{2} V_{max}$일 때의 기질 농도)
    """
    )

# ------------------------------------------------------------------------------
# ④ 결과 분석 (내 측정값을 st.dataframe 표와 st.line_chart 로)
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("📊 측정한 데이터 및 그래프 분석")

    # 측정 데이터 준비
    data = {
        "기질 농도 ([S])": [10, 20, 30, 40, 50, 60],
        "반응 속도 (v)": [2.1, 4.3, 6.2, 7.8, 8.8, 9.0],
        "이론적 최대 속도 (Vmax)": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
    }
    df = pd.DataFrame(data)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📋 기질 농도별 반응 속도 측정표")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.markdown("#### 📈 반응 속도 경향성 그래프")
        chart_df = df.set_index("기질 농도 ([S])")
        st.line_chart(chart_df)

    st.markdown(
        """
    - **분석 내용:** 기질 농도가 낮을 때(10~30)는 반응 속도가 급격하게 증가하는 경향을 보이지만, 기질 농도가 40 이상으로 증가하면서 기울기가 완만해지고 최대 반응 속도인 $V_{max}=9.0$ 수준으로 포화되는 현상을 확인할 수 있습니다.
    """
    )

# ------------------------------------------------------------------------------
# ⑤ 결론과 한계
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("📝 탐구 결론 및 모델의 한계")
    st.markdown(
        """
    ### 🎯 탐구 결론
    - 실험 및 시뮬레이션 결과, 기질 농도가 증가함에 따라 초기에는 반응 속도가 비례하여 증가하다가 일정 수치 이상에서는 더 이상 증가하지 않고 $V_{max}$에 도달함을 확인했습니다.
    - 이는 일정 수 이상의 효소가 존재할 때, 기질 농도가 매우 높으면 모든 효소의 활성 부위가 기질과 결합한 **포화 상태**가 되기 때문이라는 가설을 성공적으로 입증합니다.

    ### ⚠️ 모델의 한계
    - **온도 및 pH 미반영:** 본 시뮬레이션은 변성 현상이나 optimum pH/온도 조건에 따른 활성화 에너지 변화를 고려하지 않았습니다.
    - **역반응 단순화:** 생성물이 다시 기질이나 효소와 반응하는 역반응 및 저해제(억제제)의 효과가 모델에 포함되지 않았습니다.
    """
    )

# ------------------------------------------------------------------------------
# ⑥ 퀴즈 (st.radio 로 객관식 1문제, 정답/오답 피드백)
# ------------------------------------------------------------------------------
with tab6:
    st.subheader("🧩 학습 확인 퀴즈")
    st.markdown("**Q. 기질 농도가 매우 높아져 모든 효소가 활성 부위에서 기질과 결합해 있을 때 발생하는 현상은?**")

    user_answer = st.radio(
        "정답을 선택하세요:",
        options=[
            "1. 효소가 기질에 의해 분해된다.",
            "2. 반응 속도가 0으로 떨어진다.",
            "3. 모든 효소가 포화되어 반응 속도가 최대($V_{max}$)에 도달한다.",
            "4. 기질 분자의 운동 에너지가 감소한다.",
        ],
        index=None,
    )

    if st.button("정답 확인"):
        if user_answer is None:
            st.warning("옵션을 선택한 후 버튼을 눌러주세요.")
        elif (
            user_answer
            == "3. 모든 효소가 포화되어 반응 속도가 최대($V_{max}$)에 도달한다."
        ):
            st.success("🎉 정답입니다! 효소 포화 현상으로 인해 반응 속도가 최대치에 수렴하게 됩니다.")
        else:
            st.error("❌ 오답입니다. 다시 한번 생각해 보세요!")
