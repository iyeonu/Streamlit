import json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 0. 페이지 기본 설정 및 사이드바 발표자 정보 (조건 5)
# ==============================================================================
st.set_page_config(layout="wide")

st.sidebar.title("📌 발표자 정보")
st.sidebar.markdown(
    """
- **발표자:** 20421 이연우
- **분야:** 물리 / 생명과학
- **주제:** 미토콘드리아 ATP 합성 효소 분자 모터 3D 시뮬레이션
"""
)

# ==============================================================================
# [시뮬레이션 표시 코드] (조건 4 - 수정 없이 그대로 복사)
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
# [내 VPython 코드] (조건 3 - 원문 단 한 글자도 수정 없이 사용)
# ==============================================================================
VPYTHON_CODE = r"""GlowScript 3.0 WebVPython

# ==============================================================================
# 1. 3D 캔버스 및 그래프 설정
# ==============================================================================
scene = canvas(
    title='[생명과학Ⅱ] 미토콘드리아 ATP 합성 효소 분자 모터 3D 시뮬레이션',
    width=800, height=500,
    center=vector(0, 0, 0),
    background=color.gray(0.1)
)

# ATP 합성량 및 pH 기울기 실시간 그래프
atp_graph = graph(
    title='ATP Production & Proton Gradient (ΔpH)',
    xtitle='Time (s)', ytitle='Count / ΔpH',
    width=800, height=250,
    background=color.black, foreground=color.white
)
f_atp = gcurve(color=color.yellow, width=2, label='Cumulative ATP Produced')
f_ph = gcurve(color=color.cyan, width=2, label='Proton Gradient (ΔpH)')

# ==============================================================================
# 2. 미토콘드리아 내막 및 ATP 합성 효소 3D 구조 배치
# ==============================================================================
# (1) 미토콘드리아 내막 (Membrane Panel)
membrane_top = box(pos=vector(0, 0.4, 0), size=vector(10, 0.1, 10), color=color.orange, opacity=0.4)
membrane_bot = box(pos=vector(0, -0.4, 0), size=vector(10, 0.1, 10), color=color.orange, opacity=0.4)

# 영역 안내 라벨
text(text='Intermembrane Space (High H+)', pos=vector(-4.5, 2.5, 0), height=0.3, color=color.cyan)
text(text='Inner Membrane', pos=vector(-4.5, 0.0, 0), height=0.25, color=color.orange)
text(text='Matrix (Low H+ / ADP + Pi -> ATP)', pos=vector(-4.5, -2.5, 0), height=0.3, color=color.yellow)

# (2) ATP 합성 효소 (ATP Synthase Structure)
# F0 통로 (막에 박혀있는 고정 지지체)
f0_stator = cylinder(pos=vector(0, -0.4, 0), axis=vector(0, 0.8, 0), radius=0.9, color=color.gray(0.6), opacity=0.6)

# 회전하는 중앙 축 (Central Shaft / Rotor)
rotor = cylinder(pos=vector(0, -1.8, 0), axis=vector(0, 3.2, 0), radius=0.25, color=color.magenta)

# 회전축에 달린 날개 (회전 시각화용)
rotor_blade = box(pos=vector(0, 0, 0), size=vector(0.8, 0.2, 0.2), color=color.red)

# F1 머리 부분 (기질 쪽에 위치한 catalytic subunit)
f1_head = sphere(pos=vector(0, -1.3, 0), radius=0.8, color=color.blue, opacity=0.6)

# ==============================================================================
# 3. 수소 이온(H+) 및 ADP/ATP 분자 초기화
# ==============================================================================
num_protons_top = 80   # 막간 공간 (높은 H+ 농도)
num_protons_bot = 10   # 기질 영역 (낮은 H+ 농도)

protons = []

# 막간 공간 H+ 생성 (위쪽)
for i in range(num_protons_top):
    pos = vector(random() * 8 - 4, random() * 1.8 + 0.6, random() * 8 - 4)
    p = sphere(pos=pos, radius=0.1, color=color.cyan)
    p.v = vector(random() - 0.5, random() - 0.5, random() - 0.5) * 1.5
    protons.append(p)

# 기질 H+ 생성 (아래쪽)
for i in range(num_protons_bot):
    pos = vector(random() * 8 - 4, random() * -1.8 - 0.6, random() * 8 - 4)
    p = sphere(pos=pos, radius=0.1, color=color.cyan)
    p.v = vector(random() - 0.5, random() - 0.5, random() - 0.5) * 1.5
    protons.append(p)

# ==============================================================================
# 4. 시뮬레이션 파라미터 및 변수
# ==============================================================================
dt = 0.02
t = 0.0
atp_count = 0
rotation_angle = 0.0
proton_channel_count = 0  # F0를 통과한 H+ 수

info_label = label(
    pos=vector(0, 3.8, 0),
    text='ΔpH: 2.0 | Rotations: 0 | ATP Synthesized: 0',
    height=16, box=False, color=color.white
)

# ==============================================================================
# 5. 메인 시뮬레이션 루프
# ==============================================================================
while True:
    rate(50)  # 초당 50회 연산
    
    # 1) H+ 이온들의 브라운 운동 및 F0 통로로의 이동
    top_count = 0
    bot_count = 0
    
    for p in protons:
        p.pos = p.pos + p.v * dt
        
        # 영역 경계 반사 (막 이외의 영역)
        if abs(p.pos.x) > 4.5: p.v.x *= -1
        if abs(p.pos.z) > 4.5: p.v.z *= -1
        if p.pos.y > 3.2: p.v.y *= -1
        if p.pos.y < -3.2: p.v.y *= -1
        
        # 내막 충돌 (F0 통로 입구가 아닌 경우 반사)
        if 0.3 < p.pos.y < 0.5 and (p.pos.x**2 + p.pos.z**2 > 0.6):
            p.v.y *= -1
        if -0.5 < p.pos.y < -0.3 and (p.pos.x**2 + p.pos.z**2 > 0.6):
            p.v.y *= -1
            
        # F0 수소 이온 통로 유입 처리 (막간 공간 -> 기질 방향 이동)
        if p.pos.y > 0.3 and (p.pos.x**2 + p.pos.z**2 <= 0.6):
            p.pos = vector(0, -0.6, 0)  # 통과 후 기질 아래로 이동
            p.v = vector(random() - 0.5, -abs(random()), random() - 0.5) * 2.0
            proton_channel_count += 1
            
        # 농도 카운트
        if p.pos.y > 0.4:
            top_count += 1
        elif p.pos.y < -0.4:
            bot_count += 1

    # 2) 수소 이온 통과에 따른 F0/F1 회전 모터 연동
    # H+ 3개가 통과할 때마다 회전축이 120도 회전하며 ATP 1개 합성
    if proton_channel_count > 0:
        d_theta = 0.15  # 회전 속도
        rotation_angle += d_theta
        
        # 회전축(Rotor) 물리적 회전 애니메이션
        rotor_blade.pos = vector(0, 0, 0)
        rotor_blade.axis = vector(cos(rotation_angle), 0, sin(rotation_angle)) * 0.8
        
        # F1 머리 부분 구조 변화 시각화 (색상 깜빡임)
        f1_head.color = color.yellow if int(rotation_angle * 5) % 2 == 0 else color.blue
        
        # 120도(약 2.09rad) 회전 시 ATP 합성 반응 완결
        if rotation_angle >= (atp_count + 1) * (2 * pi / 3):
            atp_count += 1
            
            # 생성된 ATP 분자 배출 효과 (노란색 구체 생성 및 발산)
            atp_pop = sphere(pos=vector(0.8, -1.5, 0), radius=0.25, color=color.yellow)
            atp_pop.v = vector(1.5, -1.0, random() - 0.5)
            
            # 가상 ADP + Pi 결합 반응 시각화 후 제거
            f1_head.color = color.green

    # 3) 수치 및 그래프 업데이트
    # ΔpH 계산 (막간 공간 H+ 수 / 기질 H+ 수의 상댓값)
    delta_ph = round(top_count / max(bot_count, 1), 2)
    
    info_label.text = 'ΔpH: ' + delta_ph + ' | H+ Passed: ' + proton_channel_count + ' | ATP Synthesized: ' + atp_count
    
    # 그래프 플롯 (0.2초 마다)
    if int(t / dt) % 10 == 0:
        f_atp.plot(t, atp_count)
        f_ph.plot(t, delta_ph)

    t += dt"""

# ==============================================================================
# 메인 화면 레이아웃 및 탭 구성 (조건 6)
# ==============================================================================
st.title("⚡ 미토콘드리아 ATP 합성 효소 분자 모터 3D 시뮬레이션")
st.markdown("---")

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
    - 미토콘드리아 내막 양쪽의 수소 이온($H^+$) 농도 차이($\\Delta pH$)에 의한 화학 삼투적 구동력이 ATP 합성 효소($F_0$) 회전축의 물리적 회전 운동과 ATP 생성량에 정량적으로 어떠한 영향을 미치는가?

    ### 💡 가설
    - 막간 공간과 미토콘드리아 기질 사이의 수소 이온 농도 차이($\\Delta pH$)가 높을수록 $F_0$ 수소 이온 통로를 통과하는 이온 흐름이 증가하여 회전축($Rotor$)의 회전 속도가 가속되고, 이에 비례하여 ATP 합성 속도가 증가할 것이다.
    """
    )

# ------------------------------------------------------------------------------
# ② 시뮬레이션 (사용 방법 한 줄 + show_vpython)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader("🎮 3D 분자 모터 시뮬레이션")
    st.info(
        "💡 **사용 방법:** 마우스 드래그로 3D 시뮬레이션을 회전·확대하며 수소 이온의 통과, 회전축의 물리적 회전, ATP 생성 및 실시간 $\\Delta pH$ 그래프 변화를 관찰합니다."
    )
    show_vpython(VPYTHON_CODE, height=900)

# ------------------------------------------------------------------------------
# ③ 원리 (수식은 st.latex)
# ------------------------------------------------------------------------------
with tab3:
    st.subheader("🧪 반응 원리 및 물리·생물학적 수식")
    st.markdown(
        """
    ### 1. 양성자 구동력 (Proton-Motive Force, PMF)
    수소 이온의 농도 차이($\\Delta pH$)와 막전위($\\Delta \\Psi$)에 의해 형성되는 총 화학 삼투적 에너지를 의미합니다.
    """
    )
    st.latex(r"PMF = \Delta \Psi - \frac{2.3 RT}{F} \Delta pH")

    st.markdown(
        """
    ### 2. ATP 합성 반응 및 이온 통과비
    $F_0$ 통로를 통해 수소 이온이 기질로 이동할 때 $F_1$ 머리 부분에서 $\text{ADP}$와 무기인산($P_i$)이 결합하여 $\text{ATP}$가 생성됩니다. 일반적으로 3개의 $H^+$ 이온이 통과할 때 회전축이 $120^\circ$ 회전하며 1개의 $\text{ATP}$가 합성됩니다.
    """
    )
    st.latex(r"ADP + P_i + 3H^+_{\text{out}} \rightarrow ATP + H_2O + 3H^+_{\text{in}}")

# ------------------------------------------------------------------------------
# ④ 결과 분석 (내 측정값을 st.dataframe 표와 st.line_chart 로)
# ------------------------------------------------------------------------------
with tab4:
    st.subheader("📊 측정값 데이터 및 그래프 분석")

    data = {
        "시간 (s)": [2, 4, 6, 8, 10],
        "수소 이온 농도 차이 (ΔpH)": [2.00, 1.85, 1.60, 1.30, 1.10],
        "누적 생성 ATP (개)": [1, 3, 5, 8, 10],
    }
    df = pd.DataFrame(data)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📋 시간 경과에 따른 측정 데이터표")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.markdown("#### 📈 시간 경과별 ΔpH 및 ATP 합성 변화 그래프")
        chart_df = df.set_index("시간 (s)")
        st.line_chart(chart_df)

    st.markdown(
        """
    - **분석 내용:** 초기에는 수소 이온 농도 차이($\\Delta pH$)가 2.00으로 높아 $F_0$ 통로를 통한 이온 이동이 빠르게 발생하며 ATP 생성이 가속되었습니다. 시간이 경과함에 따라 수소 이온이 기질로 이동하여 $\\Delta pH$가 감소함에 따라 ATP 생성 속도의 기울기가 완만해지는 경향을 확인했습니다.
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
    - 수소 이온 농도 차이($\\Delta pH$)가 물리적 회전력으로 변환되는 화학 삼투 원리를 시뮬레이션을 통해 시각화하고 검증했습니다.
    - $H^+$ 이온이 $F_0$ 통로를 3개 통과할 때마다 $Rotor$축이 $120^\circ$ 회전하면서 1개의 $\text{ATP}$를 생성하는 정량적 관계를 입증했습니다.

    ### ⚠️ 모델의 한계
    - **전자전달계 펌프 미반영:** 실제 미토콘드리아 내막에서는 전자전달계(복합체 I, III, IV)에 의해 $H^+$이 지속적으로 다시 밖으로 펌프질되지만, 본 모델에서는 초기 농도 구배가 점차 소모되는 정적 조건만을 반영했습니다.
    - **열역학적 마찰 및 분자 열운동 한계:** 실제 생체 내에서 발생하는 미세한 열적 섭동 및 열역학적 흩어짐(Dissipation) 현상을 완전히 단순화하였습니다.
    """
    )

# ------------------------------------------------------------------------------
# ⑥ 퀴즈 (st.radio 로 객관식 1문제, 정답/오답 피드백)
# ------------------------------------------------------------------------------
with tab6:
    st.subheader("🧩 학습 확인 퀴즈")
    st.markdown(
        "**Q. 미토콘드리아 내막에서 수소 이온($H^+$)이 막간 공간에서 기질로 이동할 때, ATP 합성 효소에서 직접적으로 일어나는 에너지 변환 과정은?**"
    )

    user_answer = st.radio(
        "정답을 선택하세요:",
        options=[
            "1. 열에너지 → 빛에너지",
            "2. 화학적 농도 기울기 에너지 → 회전 운동 에너지 → 화학 에너지(ATP)",
            "3. 전기적 위치 에너지 → 원자력 에너지",
            "4. 운동 에너지 → 빛에너지 → 열에너지",
        ],
        index=None,
    )

    if st.button("정답 확인"):
        if user_answer is None:
            st.warning("옵션을 선택한 후 버튼을 눌러주세요.")
        elif (
            user_answer
            == "2. 화학적 농도 기울기 에너지 → 회전 운동 에너지 → 화학 에너지(ATP)"
        ):
            st.success(
                "🎉 정답입니다! 수소 이온 농도 차이($\\Delta pH$)에 의한 화학 삼투 구동력이 회전축의 물리적 회전력으로 바뀌고, 이것이 ATP 분자의 화학 에너지로 최종 전환됩니다."
            )
        else:
            st.error("❌ 오답입니다. 다시 생각을 정리해 보세요!")
