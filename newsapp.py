import streamlit as st
import requests

# ============================================
# 🔑 네이버 API 인증 정보
# ============================================
CLIENT_ID = "1YkQSO3BhLEXJ0I8GmcP"
CLIENT_SECRET = "9eqpJwqGkI"


# ------------------------------------------------
# 1️⃣ 뉴스 제목에서 HTML 태그 제거 함수
# ------------------------------------------------
def clean_title(title):
    """
    네이버 뉴스 API는
    검색어가 포함된 부분을 <b>태그</b>로 감싸서 줍니다.

    이 함수는 그 태그를 제거해서
    사람이 읽기 쉬운 제목으로 만들어 줍니다.
    """
    # <b> 태그 제거
    title = title.replace("<b>", "")
    title = title.replace("</b>", "")
    return title


# ------------------------------------------------
# 2️⃣ 네이버 뉴스 검색 함수
# ------------------------------------------------
def search_news(keyword, display=5, sort="sim"):
    """
    네이버 뉴스 API를 사용해
    입력한 키워드로 뉴스 검색하기

    매개변수:
        keyword (str): 검색할 단어
        display (int): 결과 개수
        sort (str): 정렬 방식 (sim: 정확도순, date: 최신순)
    """
    # 네이버 뉴스 검색 API 주소
    url = "https://openapi.naver.com/v1/search/news.json"

    # 네이버 API는 요청 헤더에
    # Client ID와 Secret을 반드시 포함해야 합니다
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    # 검색 조건(옵션)
    params = {
        "query": keyword,
        "display": display,
        "sort": sort
    }

    # API 호출 (GET 요청)
    response = requests.get(url, headers=headers, params=params)

    return response


# ============================================
# 3️⃣ Streamlit 앱 UI
# ============================================

# 페이지 설정
st.set_page_config(
    page_title="네이버 뉴스 검색",
    page_icon="📰",
    layout="wide"
)

# 제목
st.title("📰 네이버 뉴스 검색 프로그램")
st.markdown("---")

# Client ID 확인
if CLIENT_ID == "" or CLIENT_SECRET == "":
    st.error("⚠️ 먼저 CLIENT_ID와 CLIENT_SECRET을 설정하세요!")
    st.info("""
    📝 **발급 방법:**
    1. https://developers.naver.com 접속
    2. 애플리케이션 등록
    3. 검색 API 사용 신청
    4. 발급받은 ID와 Secret을 코드에 입력
    """)
else:
    # 사이드바에 옵션 설정
    with st.sidebar:
        st.header("⚙️ 검색 옵션")
        
        # 결과 개수 선택
        display_count = st.slider(
            "결과 개수",
            min_value=1,
            max_value=100,
            value=10,
            step=1
        )
        
        # 정렬 방식 선택
        sort_option = st.radio(
            "정렬 방식",
            options=["sim", "date"],
            format_func=lambda x: "정확도순" if x == "sim" else "최신순",
            index=0
        )
        
        st.markdown("---")
        st.info("💡 **사용 예시**\n- 인공지능\n- 날씨\n- 스포츠")

    # 검색어 입력
    col1, col2 = st.columns([4, 1])
    with col1:
        keyword = st.text_input(
            "🔍 검색어를 입력하세요",
            placeholder="예: 인공지능, 날씨, 스포츠"
        )
    with col2:
        search_button = st.button("검색", type="primary", use_container_width=True)

    # 검색 실행
    if search_button or keyword:
        if keyword:
            with st.spinner(f"🔍 '{keyword}' 뉴스 검색 중..."):
                response = search_news(keyword, display_count, sort_option)

            # 응답 결과 확인
            if response.status_code == 200:
                # JSON 응답을 파이썬 딕셔너리로 변환
                data = response.json()
                items = data.get("items", [])

                if items:
                    st.success(f"📰 '{keyword}' 관련 뉴스 **{len(items)}**건 검색됨")
                    st.markdown("---")

                    # 뉴스 하나씩 출력
                    for i, item in enumerate(items, 1):
                        # 제목 가져오기 + HTML 태그 제거
                        title = clean_title(item.get("title", ""))
                        description = clean_title(item.get("description", ""))
                        link = item.get("link", "")
                        pub_date = item.get("pubDate", "")

                        # 뉴스 카드 형태로 표시
                        with st.container():
                            st.markdown(f"### {i}. {title}")
                            st.markdown(f"📝 {description}")
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.markdown(f"🕐 {pub_date}")
                            with col_b:
                                st.link_button("기사 보기", link, use_container_width=True)
                            st.markdown("---")
                else:
                    st.warning("검색 결과가 없어요.")

            # 인증 오류
            elif response.status_code == 401:
                st.error("❌ 인증 오류! Client ID와 Client Secret을 확인하세요.")

            # 호출 한도 초과
            elif response.status_code == 429:
                st.error("❌ 호출 한도 초과! 잠시 후 다시 시도하세요.")

            # 기타 오류
            else:
                st.error(f"❌ 오류 발생: {response.status_code}")
        else:
            st.warning("검색어를 입력해주세요.")