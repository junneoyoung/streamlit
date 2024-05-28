import streamlit as st
import re
from openai import AzureOpenAI

import base64
from urllib.parse import quote

import random

import requests

import json

def create_basic_auth_header(client_id, password):
    # 클라이언트 ID를 URL 인코딩
    encoded_client_id = quote(client_id)

    # 클라이언트 ID와 비밀번호를 콜론으로 결합
    credentials = f"{encoded_client_id}:{password}"

    # Base64 인코딩
    auth_base64 = base64.b64encode(credentials.encode()).decode('utf-8')

    # 'Basic' 인증 스키마 생성
    result = f"Basic {auth_base64}"
    return result

# 랜덤스트링 생성
def generate_random_string():
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    result = ''
    characters_length = len(characters)
    for i in range(20):
        result += characters[random.randint(0, characters_length - 1)]

    return result

# 설문 생성 후 이전 페이지로 이동
def go_back():
    go_back_script = """
    <script type="text/javascript">
        window.history.back();
    </script>
    """
    st.markdown(go_back_script, unsafe_allow_html=True)

# 세션 상태 초기화
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# GPT 응답을 저장하기 위한 상태 변수 초기화
if 'gpt_response' not in st.session_state:
    st.session_state.gpt_response = None

if 'survey_title' not in st.session_state:
    st.session_state.survey_title = None

if 'survey_intent' not in st.session_state:
    st.session_state.survey_intent = None

if 'question1' not in st.session_state:
    st.session_state.question1 = None

if 'question2' not in st.session_state:
    st.session_state.question2 = None

if 'question3' not in st.session_state:
    st.session_state.question3 = None

if 'question4' not in st.session_state:
    st.session_state.question4 = None

if 'question5' not in st.session_state:
    st.session_state.question5 = None

if 'question1' not in st.session_state:
    st.session_state.question1 = None

if 'question1' not in st.session_state:
    st.session_state.question1 = None

if 'question1_gender' not in st.session_state:
    st.session_state.question1_gender = None

if 'question2_gender' not in st.session_state:
    st.session_state.question2_gender = None

if 'question1_age' not in st.session_state:
    st.session_state.question1_age = None

if 'question2_age' not in st.session_state:
    st.session_state.question2_age = None

if 'answer1' not in st.session_state:
    st.session_state.answer1 = None

if 'answer2' not in st.session_state:
    st.session_state.answer2 = None

if 'answer3' not in st.session_state:
    st.session_state.answer3 = None

if 'answer4' not in st.session_state:
    st.session_state.answer4 = None

if 'answer5' not in st.session_state:
    st.session_state.answer5 = None

if 'answer1_gender' not in st.session_state:
    st.session_state.answer1_gender = None

if 'answer2_gender' not in st.session_state:
    st.session_state.answer2_gender = None

if 'answer1_age' not in st.session_state:
    st.session_state.answer1_age = None

if 'answer2_age' not in st.session_state:
    st.session_state.answer2_age = None

surveyId = 'test123451'
surveyId_num = 690

# 페이지 설정: wide 모드로 설정하여 전체 너비를 사용
st.set_page_config(layout="wide")

st.title("돈버는 설문. AI 설문생성.")


# Azure OpenAI 설정
api_key = st.secrets["azure_openai"]["api_key_4o"]
api_base = st.secrets["azure_openai"]["api_base_4o"]
deployment_name = st.secrets["azure_openai"]["deployment_name_4o"]
api_version = st.secrets["azure_openai"]["api_version_4o"]

# client = OpenAI(api_key=st.secrets["openai"]["api_key"])
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=api_base
)

response_slot0 = st.empty()
response_slot0.text("장점 1: 효율적인 데이터 분석을 위한 설문 설계\nSKT 데이터와 연관된 설문을 생성함으로써, 교차 분석과 같은 후속 데이터 분석이 보다 용이하게 가능합니다.\n이러한 접근은 데이터 간의 상관관계를 깊이 있게 탐색할 수 있는 기회를 제공합니다.\n\n장점 2: 간편하고 제약 없는 설문 생성 과정\n설문 생성 과정이 단순하고 유연하여, 다른 경쟁 설문 업체 대비 사용자는 복잡한 설정이나 제약 조건(글자 수 제한, 규칙 설정, 명확화 의도 요구 등) 없이 쉽게 설문을 만들 수 있습니다.\n이는 설문 준비 과정을 대폭 간소화하며, 빠르고 효과적인 설문 작성을 가능하게 합니다.")

st.markdown("---")

# 사용자 입력 받기
survey_intent = st.text_input("설문 의도를 적어주세요:", placeholder="Type here...")

# 입력된 내용을 화면에 표시하고, 설명 요청
if survey_intent and not st.session_state.gpt_response:
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
        model=deployment_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(f"response: {response}")
    st.session_state.gpt_response = response  # GPT 응답을 세션 상태에 저장

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

        print(f"result_value: {result_value}")
        print(f"reason_value: {reason_value}")

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
                model=deployment_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            # print(f"stream: {stream}")

            # 스트리밍 응답을 순차적으로 처리하고 표시
            full_response = ""
            try:
                for part in stream:
                    # print(f"part: {part}")
                    if part.choices:
                        # 각 Choice 객체의 delta에서 content 추출
                        for choice in part.choices:
                            # print(f"choice: {choice}")
                            finish_reason = choice.finish_reason

                            # finish_reason이 stop일 경우 종료
                            if finish_reason == 'stop':
                                response_slot2.text(full_response)  # 마지막 유효한 응답 표시
                                st.markdown("---")

                                print(f"full_response: {full_response}")

                                survey_title = re.findall(r'설문제목: "?([^"\n]+)"?', full_response)[0]
                                # print(f"survey_title: {survey_title}")

                                # 질문과 답변 추출
                                questions = re.findall(r'- (.*?)[\n\+]', full_response)
                                answers = re.findall(r'\+ (.*?)(?:\n|$)', full_response)

                                # 답변을 배열로 변환
                                answers = [answer.split(' / ') for answer in answers]

                                # 변수에 저장
                                question1, question2, question3, question4, question5 = questions
                                answer1, answer2, answer3, answer4, answer5 = answers

                                # 결과 출력
                                print("Survey Title:", survey_title)
                                print("Question 1:", question1)
                                print("Answer 1:", answer1)
                                print("Question 2:", question2)
                                print("Answer 2:", answer2)
                                print("Question 3:", question3)
                                print("Answer 3:", answer3)
                                print("Question 4:", question4)
                                print("Answer 4:", answer4)
                                print("Question 5:", question5)
                                print("Answer 5:", answer5)






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
                                    model=deployment_name,
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

                                                finish_reason = choice.finish_reason

                                                # content가 None일 경우 스트리밍 중지
                                                if finish_reason == 'stop':
                                                    response_slot7.text(full_response)  # 마지막 유효한 응답 표시
                                                    st.markdown("---")
                                                    break
                                                else:
                                                    delta_content = choice.delta.content
                                                    if delta_content:
                                                        full_response += choice.delta.content
                                                        response_slot7.text(full_response)
                                except Exception as e:
                                    st.error(f"An error occurred: {e}")

                                if len(full_response) < 10:
                                    print(f"full_response: {full_response}")

                                if full_response == 'X':
                                    response_slot7.text('이 데이터로는 설문을 만들 수 없습니다.')

                                    question1_gender = ''
                                    answer1_gender = []
                                    question2_gender = ''
                                    answer2_gender = []
                                else:
                                    # 질문과 답변 추출
                                    questions_gender = re.findall(r'- (.*?)[\n\+]', full_response)
                                    answers_gender = re.findall(r'\+ (.*?)(?:\n|$)', full_response)

                                    # 답변을 배열로 변환
                                    answers_gender = [answer.split(' / ') for answer in answers_gender]

                                    # 변수에 저장
                                    question1_gender, question2_gender = questions_gender
                                    answer1_gender, answer2_gender = answers_gender

                                    # 결과 출력
                                    print("Question 1:", question1_gender)
                                    print("Answer 1:", answer1_gender)
                                    print("Question 2:", question2_gender)
                                    print("Answer 2:", answer2_gender)



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
                                    model=deployment_name,
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

                                                finish_reason = choice.finish_reason

                                                # content가 None일 경우 스트리밍 중지
                                                if finish_reason == 'stop':
                                                    response_slot9.text(full_response)  # 마지막 유효한 응답 표시
                                                    st.markdown("---")
                                                    break
                                                else:
                                                    delta_content = choice.delta.content
                                                    if delta_content:
                                                        full_response += choice.delta.content
                                                        response_slot9.text(full_response)

                                except Exception as e:
                                    st.error(f"An error occurred: {e}")

                                if len(full_response) < 10:
                                    print(f"full_response: {full_response}")

                                if full_response == 'X':
                                    response_slot7.text('이 데이터로는 설문을 만들 수 없습니다.')

                                    question1_age = ''
                                    answer1_age = []
                                    question2_age = ''
                                    answer2_age = []
                                else:
                                    # 질문과 답변 추출
                                    questions_age = re.findall(r'- (.*?)[\n\+]', full_response)
                                    answers_age = re.findall(r'\+ (.*?)(?:\n|$)', full_response)

                                    # 답변을 배열로 변환
                                    answers_age = [answer.split(' / ') for answer in answers_age]

                                    # 변수에 저장
                                    question1_age, question2_age = questions_age
                                    answer1_age, answer2_age = answers_age

                                    # 결과 출력
                                    print("Question 1:", question1_age)
                                    print("Answer 1:", answer1_age)
                                    print("Question 2:", question2_age)
                                    print("Answer 2:", answer2_age)

                                response_slot10 = st.empty()
                                response_slot10.text(" ... ")
                                st.markdown("---")


                                survey_intent = result_value
                                print(f"survey_title: {survey_title}")
                                print(f"survey_intent: {survey_intent}")
                                print(f"question1: {question1}")
                                print(f"answer1: {answer1}")
                                print(f"question2: {question2}")
                                print(f"answer2: {answer2}")
                                print(f"question3: {question3}")
                                print(f"answer3: {answer3}")
                                print(f"question4: {question4}")
                                print(f"answer4: {answer4}")
                                print(f"question5: {question5}")
                                print(f"answer5: {answer5}")
                                print(f"question6: {question1_gender}")
                                print(f"answer6: {answer1_gender}")
                                print(f"question7: {question2_gender}")
                                print(f"answer7: {answer2_gender}")
                                print(f"question8: {question1_age}")
                                print(f"answer8: {answer1_age}")
                                print(f"question9: {question2_age}")
                                print(f"answer9: {answer2_age}")

                                # 세션 상태에 저장
                                st.session_state.survey_title = survey_title
                                st.session_state.survey_intent = survey_intent
                                st.session_state.question1 = question1
                                st.session_state.answer1 = answer1
                                st.session_state.question2 = question2
                                st.session_state.answer2 = answer2
                                st.session_state.question3 = question3
                                st.session_state.answer3 = answer3
                                st.session_state.question4 = question4
                                st.session_state.answer4 = answer4
                                st.session_state.question5 = question5
                                st.session_state.answer5 = answer5
                                st.session_state.question1_gender = question1_gender
                                st.session_state.answer1_gender = answer1_gender
                                st.session_state.question2_gender = question2_gender
                                st.session_state.answer2_gender = answer2_gender
                                st.session_state.question1_age = question1_age
                                st.session_state.answer1_age = answer1_age
                                st.session_state.question2_age = question2_age
                                st.session_state.answer2_age = answer2_age



                                # # 버튼 추가
                                # if st.button('설문 생성하기', key='generate_survey'):
                                #     pass

                                    # # 버튼이 클릭되면 실행될 코드

                                    # # # 버튼 클릭 시 이전 페이지로 돌아가기 위한 JavaScript 호출
                                    # # st.markdown("<script>redirectToURL()</script>", unsafe_allow_html=True)

                                    # print("button click")
                                    # print(f"params={params}")

                                    #  # API 엔드포인트 설정
                                    # url = 'https://tiklemoa-client-stg.sktelecom.com/api/v2/temp/insertSurveyInfo'

                                    # headers = {
                                    #     'accept': 'application/json',
                                    #     'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJjbGllbnRJZCI6Imp1bi55b3VuZy5raW1Ac2suY29tIiwicm9sZXMiOlt7ImF1dGhvcml0eSI6IlJPTEVfQURNSU4iLCJyb2xlX2lkIjoiQURNSU4iLCJyb2xlX25tIjoiUk9MRV9BRE1JTiJ9XSwidXNlcl9pZHgiOjEyLCJ0b2tlblR5cGUiOiJvcmlnaW5hbCIsImp0aSI6Imp1bi55b3VuZy5raW1Ac2suY29tIiwic3ViIjoianVuLnlvdW5nLmtpbUBzay5jb20iLCJpYXQiOjE3MTY4MTEwMTgsImV4cCI6MTcxNjgzMjYxOH0.8rTlRSa9I_AYLfTWYV6i4fQTUTqS6WRpXPlv2piBw16vY7Znas4LuX1BJ3PWKu6TgER2ykgj7CYSOQoaOBgbsw',
                                    #     'clientId': 'jun.young.kim@sk.com',
                                    # }

                                    # # POST 요청 실행
                                    # response = requests.post(url, json=params, headers=headers)
                                    # print(f"response: {response}")
                                    # print(f"response.text: {response.text}")

                                    # # 응답 상태 코드 확인
                                    # if response.status_code == 200:
                                    #     st.success('API 호출 성공!')
                                    #     # st.write(response.json())  # 응답 내용 표시
                                    # else:
                                    #     st.error('API 호출 실패')

                                # # 설문이 종료되면 for 문을 나간다
                                # break
                            else:
                                delta_content = choice.delta.content
                                if delta_content:
                                    full_response += choice.delta.content
                                    response_slot2.text(full_response)

            except Exception as e:
                st.error(f"An error occurred: {e}")

        # st.write(content)
        # print(f"Content from the response: {content}")rint
    else:
        st.write("No content available in the response.")

st.markdown("---")

# 버튼 생성 및 클릭 이벤트 처리
if st.button("설문 생성"):
    st.session_state.button_clicked = True  # 버튼 클릭 상태 업데이트

# 버튼 클릭 상태 확인
if st.session_state.button_clicked:
    print("버튼 클릭됨")  # 콘솔에 메시지 출력

    print(f"survey_title: {st.session_state.survey_title}")
    print(f"survey_intent: {st.session_state.survey_intent}")
    print(f"question1: {st.session_state.question1}")
    print(f"answer1: {st.session_state.answer1}")
    print(f"question2: {st.session_state.question2}")
    print(f"answer2: {st.session_state.answer2}")
    print(f"question3: {st.session_state.question3}")
    print(f"answer3: {st.session_state.answer3}")
    print(f"question4: {st.session_state.question4}")
    print(f"answer4: {st.session_state.answer4}")
    print(f"question5: {st.session_state.question5}")
    print(f"answer5: {st.session_state.answer5}")
    print(f"question6: {st.session_state.question1_gender}")
    print(f"answer6: {st.session_state.answer1_gender}")
    print(f"question7: {st.session_state.question2_gender}")
    print(f"answer7: {st.session_state.answer2_gender}")
    print(f"question8: {st.session_state.question1_age}")
    print(f"answer8: {st.session_state.answer1_age}")
    print(f"question9: {st.session_state.question2_age}")
    print(f"answer9: {st.session_state.answer2_age}")

    survey_title = st.session_state.survey_title
    survey_intent = st.session_state.survey_intent
    question1 = st.session_state.question1
    answer1 = st.session_state.answer1
    question2 = st.session_state.question2
    answer2 = st.session_state.answer2
    question3 = st.session_state.question3
    answer3 = st.session_state.answer3
    question4 = st.session_state.question4
    answer4 = st.session_state.answer4
    question5 = st.session_state.question5
    answer5 = st.session_state.answer5
    question6 = st.session_state.question1_gender
    answer6 = st.session_state.answer1_gender
    question7 = st.session_state.question2_gender
    answer7 = st.session_state.answer2_gender
    question8 = st.session_state.question1_age
    answer8 = st.session_state.answer1_age
    question9 = st.session_state.question2_age
    answer9 = st.session_state.answer2_age


    sec_pageId = generate_random_string()

    params = {
        "surveyId": surveyId,
        "surveyStorageInfo": json.dumps({
            "surveyId": surveyId,
            "surveyMasters": {
                "id": surveyId_num,
                "surveyId": surveyId,
                "type": "POLL",
                "tag": None,
                "tagInfo": None,
                "introTitle": survey_title,
                "introSubTitle": None,
                "progressbarYn": None,
                "progressbarColor": None,
                "bgColor": None,
                "thumbnailImgInfo": None,
                "recruitCnt": 1,
                "bannerImgInfo": None,
                "shareYn": "Y",
                "planOpenDtti": "202405010000",
                "planCloseDtti": "202405150100",
                "planCloseChkYn": None,
                "planCloseByRespCntYn": None,
                "planCloseByRespCnt": None,
                "planPauseYn": None,
                "rewardYn": "N",
                "rewardWithTpYn": None,
                "rewardWithCstYn": None,
                "basicRewardPoint": 0,
                "additionalRewardPoint": 0,
                "customReward": None,
                "followingYn": "N",
                "questionNumType": "Q02",
                "titleViewYn": None,
                "joinRewardPoint": 0,
                "completeRewardPoint": 0,
                "intention": survey_intent,
                "externalIframeUrl": None
            },
            "pagesMasters": [{
                "actionStts": "I",
                "isNew": "Y",
                "id": None,
                "pageId": generate_random_string(),
                "headTitle": survey_title,
                "pageSeq": 1,
                "footer": "",
                "pageType": "INTRO",
                "description": "TEST",
                "bgColor": "",
                "termsId": None,
                "penelImgViewYn": None,
                "panelTermsAgYn": None,
                "upperId": None,
                "introImgInfo": None,
                "introduceImgInfo": None,
                "imgInfo": None,
                "surveyMastersId": None,
                "questionMasters": None
            }, {
                "actionStts": "I",
                "isNew": "Y",
                "id": None,
                "pageId": sec_pageId,
                "headTitle": "",
                "pageSeq": 2,
                "footer": "",
                "pageType": "QUESTION",
                "description": "",
                "bgColor": "",
                "termsId": None,
                "penelImgViewYn": None,
                "panelTermsAgYn": None,
                "upperId": None,
                "introImgInfo": None,
                "introduceImgInfo": None,
                "imgInfo": None,
                "surveyMastersId": None,
                "questionMasters": [{
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question1,
                    "subTitle": "",
                    "seq": 1,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.1",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer1)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question2,
                    "subTitle": "",
                    "seq": 2,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.2",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer2)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question3,
                    "subTitle": "",
                    "seq": 3,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.3",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer3)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question4,
                    "subTitle": "",
                    "seq": 4,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.4",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer4)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question5,
                    "subTitle": "",
                    "seq": 5,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.5",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer5)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question6,
                    "subTitle": "",
                    "seq": 6,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.6",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer6)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question7,
                    "subTitle": "",
                    "seq": 7,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.7",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer7)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question8,
                    "subTitle": "",
                    "seq": 8,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.8",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer8)
                    ],
                    "intention": ""
                }, {
                    "id": 0,
                    "isNew": "Y",
                    "actionStts": "I",
                    "pageId": sec_pageId,
                    "questionId": generate_random_string(),
                    "title": question9,
                    "subTitle": "",
                    "seq": 9,
                    "type": "SELONE",
                    "mandatoryYn": "N",
                    "maxSelect": 1,
                    "choiceDisplayOption": "FIXED",
                    "statsShowType": None,
                    "number": "Q.9",
                    "minSelect": 1,
                    "footer": "",
                    "disableExport": 0,
                    "rsSecretYn": "N",
                    "etcYn": "",
                    "ectReqYn": "",
                    "qkeyValue": "N",
                    "qkeyValueDetail": None,
                    "randomYn": "",
                    "numYn": "",
                    "viewMaxLen": "",
                    "idxNumType": "TEXT",
                    "isTimeView": "Y",
                    "imgInfo": None,
                    "lineYn": "N",
                    "emailType": "B01",
                    "choiceMasters": [
                        {
                            "id": 0,
                            "isNew": "Y",
                            "actionStts": "I",
                            "choiceId": generate_random_string(),
                            "seq": index,
                            "title": choice,
                            "type": "TEXT",
                            "minLength": 1,
                            "maxLength": 100,
                            "value": "",
                            "preGuideLabel": "",
                            "midGuideLabel": "",
                            "endGuideLabel": "",
                            "minInteger": 1,
                            "maxInteger": 100,
                            "textboxDisplay": "DEFAULT",
                            "etcYn": "N",
                            "viewMaxLen": "",
                            "typeSet": "",
                            "isOnlyNum": "N",
                            "colArr": []
                        } for index, choice in enumerate(answer9)
                    ],
                    "intention": ""
                }
            ]
            },
            {
            "id": 0,
            "isNew": "Y",
            "actionStts": "I",
            "pageId": "uOcWdgwPIuiLFZzHBqAr",
            "headTitle": "TEST",
            "description": "TEST",
            "bgColor": "",
            "termsId": 0,
            "terms": "",
            "panelImgViewYn": "",
            "penelTermsAgYn": "",
            "upperId": "",
            "pageType": "FINISH",
            "pageSeq": 3
            }
        ],
        "targetCondMasters": None,
        "surveyTesterMasters": None
        })
    }

    # API 엔드포인트 설정
    url = 'https://tiklemoa-client-stg.sktelecom.com/api/v2/temp/insertSurveyInfo'

    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJjbGllbnRJZCI6IjExMTExNDBAc2t0ZWxlY29tLmNvbSIsInJvbGVzIjpbeyJhdXRob3JpdHkiOiJST0xFX1BBUlRORVIiLCJyb2xlX2lkIjoiUEFSVE5FUiIsInJvbGVfbm0iOiJST0xFX1BBUlRORVIifV0sInVzZXJfaWR4Ijo3NSwidG9rZW5UeXBlIjoib3JpZ2luYWwiLCJqdGkiOiIxMTExMTQwQHNrdGVsZWNvbS5jb20iLCJzdWIiOiIxMTExMTQwQHNrdGVsZWNvbS5jb20iLCJpYXQiOjE3MTY4NjcwMDYsImV4cCI6MTcxNjg4ODYwNn0.M27Rk-0FqyKz8T0B7VLjlylOgx6Hm3YVMo41QuB9eGvpkoKvwWJUmaq7vwRctGlzcRXGaz8a5ooAqisq_tJrpg',
        'clientId': '1111140@sktelecom.com',
    }

     # POST 요청 실행
    response = requests.post(url, json=params, headers=headers)
    print(f"response: {response}")
    print(f"response.text: {response.text}")

    # 응답 상태 코드 확인
    if response.status_code == 200:
        st.success('API 호출 성공!')
        go_back()

    else:
        st.error('API 호출 실패')
