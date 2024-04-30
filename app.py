from openai import OpenAI
import streamlit as st

# 페이지 설정: wide 모드로 설정하여 전체 너비를 사용
st.set_page_config(layout="wide")

st.title("돈버는 설문. AI 설문생성.")

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

response_slot0 = st.empty()
response_slot0.text("장점 1: 효율적인 데이터 분석을 위한 설문 설계\nSKT 데이터와 연관된 설문을 생성함으로써, 교차 분석과 같은 후속 데이터 분석이 보다 용이하게 가능합니다.\n이러한 접근은 데이터 간의 상관관계를 깊이 있게 탐색할 수 있는 기회를 제공합니다.\n\n장점 2: 간편하고 제약 없는 설문 생성 과정\n설문 생성 과정이 단순하고 유연하여, 다른 경쟁 설문 업체 대비 사용자는 복잡한 설정이나 제약 조건(글자 수 제한, 규칙 설정, 명확화 의도 요구 등) 없이 쉽게 설문을 만들 수 있습니다.\n이는 설문 준비 과정을 대폭 간소화하며, 빠르고 효과적인 설문 작성을 가능하게 합니다.")

st.markdown("---")

# 사용자 입력 받기
survey_intent = st.text_input("설문 의도를 적어주세요:", placeholder="Type here...")

# 입력된 내용을 화면에 표시하고, 설명 요청
if survey_intent:
    # st.write(f"You entered: {survey_intent}")

    # step1. 설문 의도 파악

    prompt = f"""
        너는 세계 최고의 설문 제작자이다.

        사용자 설문의도: {survey_intent}

        사용자가 제공한 설문의도를 검토하여 그것이 구체적이고 실현 가능한 목적에 부합하는지 평가합니다.
        검토 과정에서 설문의도가 우리의 기준에 맞지 않거나, 구현 가능한 설문으로 변환할 수 없다면, 그 이유를 명확히 하여 아래 형식에 따라 결과를 출력합니다.

        만약 설문의도가 불분명하거나, 너무 일반적이거나, 악의적인 내용을 포함하고 있거나, 비윤리적인 목표를 가진 경우:
        결과: X
        이유: 설문의도가 명확하지 않거나 구현 불가능하기 때문에 적합하지 않습니다. (예시로, 설문의도가 너무 일반적이거나 단 한 두 단어로만 이루어져 있을 경우)

        반면, 설문의도가 구체적이고, 우리의 기준에 부합하며, 실현 가능한 설문으로 재생성이 가능하다고 판단될 경우:
        결과: 구체화된 설문의도 (예: '아이폰 사용자 중 안드로이드로 전환 고려자의 주요 이유와 장벽에 대해 파악하기')
    """

    response_slot1 = st.empty()
    response_slot1.text("설문 의도 파악중 ...")

    # GPT-4를 사용하여 설명 요청
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(f"response: {response}")

    # 응답의 content 부분만 출력
    if response.choices and response.choices[0].message:
        content = response.choices[0].message.content
        print(f"content: {content}")

        # "결과:" 뒤의 값을 가져오기
        if "결과:" in content:
            result_value = content.split("결과: ")[1].split("\n")[0].strip("'")
        else:
            result_value = 'X'

        # "이유:" 뒤의 값을 가져오기
        if "이유:" in content:
            reason_value = content.split("이유: ")[1]
        else:
            reason_value = None

        # print(f"result_value: {result_value}")
        # print(f"reason_value: {reason_value}")

        if result_value == 'X':
            response_slot1.markdown(f"""
            <style>
            .text {{
                word-wrap: break-word;
            }}
            .markdown-style {{
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            }}
            </style>

            <div class="text markdown-style">
                {reason_value}<br><br>의도를 다시 적어주세요.
            </div>
            """, unsafe_allow_html=True)
        else:
            response_slot1.text(f"설문의도: {result_value}")
            st.markdown("---")

            survey_cnt = 5

            prompt = f"""
                설문의도: '{result_value}'

                설문제작 전문가로서, 주어진 설문의도를 바탕으로 창의적이고 기발한 방식으로 설문제목을 생성하고, 해당 제목 아래에서 객관식 형태의 설문 문항들만을 '{survey_cnt}'개 구성합니다.
                이 설문은 성별, 연령, 거주지 등과 같은 단순한 정보를 묻지 않으며, 설문의도를 충실히 반영합니다.

                포맷 규칙:
                - 설문제목은 설문의도를 간결하게 요약하면서 창의적이고 기발하게 표현합니다.
                - 각 설문 질문은 '-'로 시작하며, 해당하는 객관식 답변은 바로 다음 줄에 '+'로 시작합니다.
                - 각 답변은 반드시 '/'로 구분하여 나열하며, 반드시 객관식 형태로만 제한됩니다.
                - 설문문항들은 설문의도를 명확하게 반영하며, 다양한 의견을 수렴할 수 있도록 구성합니다.
                - 질문과 답변의 시작에 추가 문자나 숫자를 붙이지 않으며, 모든 문장은 한국어로 공손하게 표현되고, 높임말로 마무리됩니다.
                - 설문의 갯수는 반드시 '{survey_cnt}'로 지정된 갯수만큼 제공됩니다.
                - 반드시 아래 출력 포맷을 지켜서 출력합니다.

                출력 포맷:

                설문제목: [설문의도를 위트 있게 표현한 제목]

                - 설문 질문
                + 답변1 / 답변2 / 답변3

                - 설문 질문
                + 답변1 / 답변2 / 답변3

                ...
            """

            # 스트리밍 응답을 표시할 빈 슬롯 생성
            response_slot2 = st.empty()
            response_slot2.text("설문 생성 ...")

            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            print(f"stream: {stream}")

            # 스트리밍 응답을 순차적으로 처리하고 표시
            full_response = ""
            try:
                for part in stream:
                    if part.choices:
                        # 각 Choice 객체의 delta에서 content 추출
                        for choice in part.choices:

                            # content가 None일 경우 스트리밍 중지
                            if choice.delta.content is None:
                                response_slot2.text(full_response)  # 마지막 유효한 응답 표시
                                st.markdown("---")

                                # SKT 데이터
                                response_slot3 = st.empty()
                                response_slot3.text("SKT 고객 맞춤형 설문")

                                response_slot4 = st.empty()
                                response_slot4.text("SKT 데이터 리스트1: ['성별', '연령', '거주지', '외국인', '모바일종류', '일인가구', '직장인', '자영업', ...]")

                                response_slot5 = st.empty()
                                response_slot5.text("SKT 데이터 리스트2: ['운동관심도', '투자관심도', '패션관심도', '여행관심도', '쇼핑관심도', 'SNS관심도', '음식관심도', '게임관심도', 'OTT관심도', ...]")
                                st.markdown("---")

                                response_slot6 = st.empty()
                                response_slot6.text("[성별] 관련 설문")

                                response_slot7 = st.empty()
                                response_slot7.text("설문 생성 ...")

                                item = '성별'
                                survey_cnt = 2
                                prompt = f"""
                                    설문의도: {survey_intent}
                                    아이템: {item}

                                    설문의도와 (아이템)과 관련된 최근 사회적 이슈에 대한 설문조사 질문과 답변을 만들어주세요.
                                    (아이템) 정보를 얻는 간단한 질문은 하지 않고 논쟁적인 질문을 생성한다.
                                    설문의도와 (아이템)과 연관된 설문조사 질문을 생성할 수 없다면 'X'를 출력한다.
                                    (아이템)과 연관없는 설문은 만들 필요 없습니다.

                                    포맷 규칙:
                                    - 각 설문 질문은 '-'로 시작하며, 해당하는 객관식 답변은 바로 다음 줄에 '+'로 시작합니다.
                                    - 각 답변은 반드시 '/'로 구분하여 나열하며, 반드시 객관식 형태로만 제한됩니다.
                                    - 질문과 답변의 시작에 추가 문자나 숫자를 붙이지 않으며, 모든 문장은 한국어로 공손하게 표현되고, 높임말로 마무리됩니다.
                                    - 설문의 갯수는 반드시 '{survey_cnt}'로 지정된 갯수만큼 제공됩니다.
                                    - 반드시 아래 출력 포맷을 지켜서 출력합니다.

                                    출력 포맷:
                                    - 설문 질문
                                    + 답변1 / 답변2 / 답변3

                                    - 설문 질문
                                    + 답변1 / 답변2 / 답변3

                                """

                                stream = client.chat.completions.create(
                                    model=st.session_state["openai_model"],
                                    messages=[
                                        {"role": "user", "content": prompt}
                                    ],
                                    stream=True
                                )
                                print(f"stream: {stream}")

                                # 스트리밍 응답을 순차적으로 처리하고 표시
                                full_response = ""
                                try:
                                    for part in stream:
                                        if part.choices:
                                            # 각 Choice 객체의 delta에서 content 추출
                                            for choice in part.choices:

                                                # content가 None일 경우 스트리밍 중지
                                                if choice.delta.content is None:
                                                    response_slot7.text(full_response)  # 마지막 유효한 응답 표시
                                                    st.markdown("---")
                                                    break
                                                else:
                                                    full_response += choice.delta.content
                                                    response_slot7.text(full_response)  # 업데이트된 응답을 슬롯에 표시
                                except Exception as e:
                                    st.error(f"An error occurred: {e}")

                                response_slot8 = st.empty()
                                response_slot8.text("[연령] 관련 설문")

                                response_slot9 = st.empty()
                                response_slot9.text("설문 생성 ...")

                                item = '연령'
                                survey_cnt = 2
                                prompt = f"""
                                    설문의도: {survey_intent}
                                    아이템: {item}

                                    설문의도와 (아이템)과 관련된 최근 사회적 이슈에 대한 설문조사 질문과 답변을 만들어주세요.
                                    (아이템) 정보를 얻는 간단한 질문은 하지 않고 논쟁적인 질문을 생성한다.
                                    설문의도와 (아이템)과 연관된 설문조사 질문을 생성할 수 없다면 'X'를 출력한다.
                                    (아이템)과 연관없는 설문은 만들 필요 없습니다.

                                    포맷 규칙:
                                    - 각 설문 질문은 '-'로 시작하며, 해당하는 객관식 답변은 바로 다음 줄에 '+'로 시작합니다.
                                    - 각 답변은 반드시 '/'로 구분하여 나열하며, 반드시 객관식 형태로만 제한됩니다.
                                    - 질문과 답변의 시작에 추가 문자나 숫자를 붙이지 않으며, 모든 문장은 한국어로 공손하게 표현되고, 높임말로 마무리됩니다.
                                    - 설문의 갯수는 반드시 '{survey_cnt}'로 지정된 갯수만큼 제공됩니다.
                                    - 반드시 아래 출력 포맷을 지켜서 출력합니다.

                                    출력 포맷:
                                    - 설문 질문
                                    + 답변1 / 답변2 / 답변3

                                    - 설문 질문
                                    + 답변1 / 답변2 / 답변3

                                """

                                stream = client.chat.completions.create(
                                    model=st.session_state["openai_model"],
                                    messages=[
                                        {"role": "user", "content": prompt}
                                    ],
                                    stream=True
                                )
                                print(f"stream: {stream}")

                                # 스트리밍 응답을 순차적으로 처리하고 표시
                                full_response = ""
                                try:
                                    for part in stream:
                                        if part.choices:
                                            # 각 Choice 객체의 delta에서 content 추출
                                            for choice in part.choices:

                                                # content가 None일 경우 스트리밍 중지
                                                if choice.delta.content is None:
                                                    response_slot9.text(full_response)  # 마지막 유효한 응답 표시
                                                    st.markdown("---")
                                                    break
                                                else:
                                                    full_response += choice.delta.content
                                                    response_slot9.text(full_response)  # 업데이트된 응답을 슬롯에 표시
                                except Exception as e:
                                    st.error(f"An error occurred: {e}")

                                response_slot10 = st.empty()
                                response_slot10.text(" ... ")
                                st.markdown("---")

                                # 버튼 추가
                                if st.button('설문 생성하기'):
                                    # 버튼이 클릭되면 실행될 코드
                                    # st.write('Button was clicked!')
                                    pass








                                break
                            else:
                                full_response += choice.delta.content
                                response_slot2.text(full_response)  # 업데이트된 응답을 슬롯에 표시
            except Exception as e:
                st.error(f"An error occurred: {e}")

        # st.write(content)
        print(f"Content from the response: {content}")
    else:
        st.write("No content available in the response.")
