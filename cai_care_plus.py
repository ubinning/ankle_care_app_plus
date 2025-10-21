import streamlit as st
import pandas as pd
import datetime
from google.auth.credentials import AnonymousCredentials
from google.cloud import firestore as client_firestore
import random
import time

# -------------------------------
# 🔹 Firestore 초기화
# -------------------------------
project_id = "cai-care-app"
db = client_firestore.Client(project=project_id, credentials=AnonymousCredentials())

# -------------------------------
# 🔹 기본 설정
# -------------------------------
st.set_page_config(page_title="발목 기록 앱 PLUS", page_icon="👣", layout="centered")

KST = datetime.timezone(datetime.timedelta(hours=9))
today = str(datetime.datetime.now(KST).date())

if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "start"

# -------------------------------
# 🌿 메시지 뱅크
# -------------------------------
MOTIVATION_BANNER = [
    "기록을 남긴다는 건, 스스로를 관리하려는 의지의 표현이에요.",
    "오늘도 발목 상태를 확인했네요. 그게 회복의 기본이에요.",
    "꾸준히 체크하는 게 가장 확실한 예방이에요.",
    "기록은 치료보다 먼저 오는 관리의 습관이에요.",
    "오늘의 기록이 내일의 변화를 만듭니다.",
    "좋은 날과 나쁜 날이 함께 있는 게 정상이에요. 방향만 잃지 않으면 돼요.",
    "회복은 직선이 아니에요. 오르내림 속에서도 조금씩 좋아집니다.",
    "조금씩이라도 기록을 이어가는 게 제일 어렵고, 제일 가치 있어요.",
    "기록이 쌓일수록 당신의 몸이 달라질 거예요.",
    "오늘도 발목을 챙긴 것만으로 충분히 잘한 하루예요.",
    "통증이 있는 날도, 없는 날도 모두 회복의 일부예요.",
    "지금처럼 꾸준히 모니터링하는 게 가장 큰 재활입니다.",
    "하루 1분의 기록이 쌓이면, 그게 결국 관리의 루틴이 돼요.",
    "꾸준함이 완벽함보다 훨씬 중요해요.",
    "스스로의 회복을 관찰한다는 건 이미 전문가적인 태도예요.",
    "불편했던 날을 남겨두면, 좋아지는 날이 더 분명히 보입니다.",
    "회복은 갑자기 오는 게 아니라, 이렇게 조용히 쌓여요.",
    "기록은 나를 위한 가장 간단한 관리예요.",
    "완벽할 필요 없어요. 그냥 계속 가면 됩니다."
]

FEEDBACK = {
    "first": "첫 기록을 남겼어요. 시작이 가장 어렵지만, 잘 해내셨어요 👣",
    "pain_down": "통증이 줄었네요. 작은 변화지만 분명한 회복의 신호예요.",
    "pain_same": "큰 변화는 없지만, 꾸준히 관리하고 있다는 게 정말 중요해요.",
    "pain_up": "오늘은 조금 불편했죠? 그래도 이렇게 기록 남긴 게 제일 잘한 일이에요.",
    "instability_down": "균형감이 조금씩 돌아오고 있네요. 방향이 좋아요 👍",
    "management_done": "오늘도 스스로 관리했네요. 이런 습관이 결국 차이를 만듭니다.",
    "default": "기록 남겼네요. 이렇게 꾸준히 확인하는 게 회복의 핵심이에요."
}

# -------------------------------
# 🔹 홈 진입 시 중앙 문구 표시
# -------------------------------
def show_random_motivation_center():
    msg = random.choice(MOTIVATION_BANNER)
    st.markdown(
        f"""
        <div style='display:flex; justify-content:center; align-items:center; height:80vh;'>
            <p style='font-size:22px; text-align:center; opacity:0; animation: fadeIn 2s forwards;'>
                💬 {msg}
            </p>
        </div>
        <style>
            @keyframes fadeIn {{
                from {{opacity:0; transform: translateY(10px);}}
                to {{opacity:1; transform: translateY(0);}}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(1.8)
    st.empty()

# -------------------------------
# 🔹 시작 화면
# -------------------------------
if st.session_state.page == "start":
    st.title("👣 발목 기록 앱 PLUS")

    action = st.radio("동작 선택", ["회원가입", "로그인"])

    if action == "회원가입":
        new_user = st.text_input("새 아이디를 입력하세요")
        if st.button("회원가입"):
            if new_user.strip():
                doc_ref = db.collection("users").document(new_user)
                if doc_ref.get().exists:
                    st.error("⚠️ 이미 존재하는 아이디입니다.")
                else:
                    doc_ref.set({"join_date": today})
                    st.success("✅ 회원가입 완료! 로그인하세요.")

    elif action == "로그인":
        user = st.text_input("아이디 입력")
        if st.button("로그인"):
            if user.strip():
                doc_ref = db.collection("users").document(user)
                if doc_ref.get().exists:
                    st.session_state.user = user
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("⚠️ 등록되지 않은 아이디입니다. 회원가입을 먼저 해주세요.")

# -------------------------------
# 🔹 홈 화면
# -------------------------------
elif st.session_state.page == "home":
    show_random_motivation_center()
    st.title(f"👋 환영합니다, {st.session_state.user} 님")

    if st.button("✍️ 오늘 발목 기록하기 / 수정하기"):
        st.session_state.page = "record"
        st.rerun()

    records = db.collection("ankle_records").where("user", "==", st.session_state.user).stream()
    data = [r.to_dict() for r in records]
    df = pd.DataFrame(data)

    if not df.empty:
        df = df.sort_values("date")
        st.subheader("📊 최근 기록 요약")
        st.dataframe(df.tail(7))
        st.line_chart(df.set_index("date")[["instability", "pain", "activity"]])

        recent = df.tail(7)
        avg_pain = recent["pain"].mean()
        trend_increase = len(recent) >= 2 and recent["pain"].iloc[-1] - recent["pain"].iloc[0] >= 2

        if avg_pain < 4:
            st.success("😊 이번 주는 통증이 전반적으로 안정적이에요. 좋은 흐름이에요.")
        elif avg_pain >= 6:
            st.warning("⚠️ 최근 평균 통증이 높습니다. 발목 사용을 줄이고 회복에 집중하세요.")
        elif trend_increase:
            st.warning("⚠️ 통증이 점점 증가하는 추세입니다. 과사용에 주의하세요.")
        else:
            st.info("💪 최근 발목 상태가 안정적이에요. 꾸준히 관리하고 있습니다.")
    else:
        st.info("아직 기록이 없습니다. 상단 버튼을 눌러 첫 기록을 남겨보세요!")

    if st.button("🚪 로그아웃"):
        st.session_state.page = "start"
        st.session_state.user = None
        st.rerun()

# -------------------------------
# 🔹 기록 화면 (접질림/삐끗 여부 추가됨)
# -------------------------------
elif st.session_state.page == "record":
    st.title("✍️ 오늘 발목 기록하기")

    user = st.session_state.user
    doc_id = f"{user}_{today}"
    doc_ref = db.collection("ankle_records").document(doc_id)
    existing_record = doc_ref.get().to_dict()

    with st.form("ankle_form"):
        condition = st.slider("오늘 발목 불안정감", 0, 10, existing_record["instability"] if existing_record else 5)
        pain = st.slider("오늘 통증 정도", 0, 10, existing_record["pain"] if existing_record else 3)
        activity = st.slider("오늘 활동 수준", 0, 10, existing_record["activity"] if existing_record else 5)
        balance = st.radio("균형감/불안정감 인지", ["없음", "있음"],
                           index=["없음", "있음"].index(existing_record["balance"]) if existing_record else 0)
        
        # ✅ 접질림/삐끗 여부 추가
        sprain = st.radio("오늘 접질림/삐끗 여부", ["없음", "있음"],
                          index=["없음", "있음"].index(existing_record["sprain"]) if existing_record and "sprain" in existing_record else 0)

        with st.expander("오늘의 관리 기록"):
            management = st.multiselect(
                "🏥 오늘 한 관리 (해당되는 항목 모두 선택)",
                ["테이핑", "보호대", "냉찜질", "온찜질", "스트레칭", "마사지"],
                default=existing_record["management"].split(", ") if existing_record and existing_record["management"] else []
            )
            shoe = st.radio("👟 주로 신은 신발", ["운동화", "구두", "슬리퍼", "맨발", "부츠"],
                            index=["운동화", "구두", "슬리퍼", "맨발", "부츠"].index(existing_record["shoe"]) if existing_record else 0)
            surface = st.radio("🛤️ 주로 걸은 지면", ["평지", "계단", "경사로", "울퉁불퉁", "미끄러움"],
                               index=["평지", "계단", "경사로", "울퉁불퉁", "미끄러움"].index(existing_record["surface"]) if existing_record else 0)

        submitted = st.form_submit_button("저장하기")
        if submitted:
            previous_docs = db.collection("ankle_records").where("user", "==", user).stream()
            all_records = [p.to_dict() for p in previous_docs if "date" in p.to_dict()]
            prev = None
            if all_records:
                prev = max(all_records, key=lambda x: x["date"])
            prev_pain = prev["pain"] if prev else None
            prev_instability = prev["instability"] if prev else None

            record = {
                "user": user,
                "date": today,
                "instability": condition,
                "pain": pain,
                "activity": activity,
                "balance": balance,
                "sprain": sprain,  # ✅ 추가된 부분
                "management": ", ".join(management),
                "shoe": shoe,
                "surface": surface
            }
            doc_ref.set(record)

            feedback_key = "default"
            if prev is None:
                feedback_key = "first"
            elif pain < prev_pain:
                feedback_key = "pain_down"
            elif pain == prev_pain:
                feedback_key = "pain_same"
            elif condition < (prev_instability if prev_instability is not None else condition):
                feedback_key = "instability_down"
            elif len(management) > 0:
                feedback_key = "management_done"
            else:
                feedback_key = "pain_up"

            st.info(FEEDBACK[feedback_key])

            st.markdown(
                """
                <div style='display:flex; justify-content:center; align-items:center; height:70vh;'>
                    <p style='font-size:22px; text-align:center; color:#2E7D32; animation: fadeIn 1.5s forwards;'>
                        ✅ 오늘 기록이 저장되었습니다<br>잠시 후 홈으로 이동합니다...
                    </p>
                </div>
                <style>
                    @keyframes fadeIn {
                        from {opacity:0;}
                        to {opacity:1;}
                    }
                </style>
                """,
                unsafe_allow_html=True
            )

            time.sleep(2.3)
            st.session_state.page = "home"
            st.rerun()

    if st.button("🏠 홈으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()


