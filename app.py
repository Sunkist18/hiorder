import streamlit as st
import json
import math
import pandas as pd

# 설정 파일 로드
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# 수수료 계산 함수
def calculate_commission(total_devices, config, use_shinhan, use_internet_new, use_internet_kt, use_tanggua=False):
    commission = 0
    
    # 기본 수수료
    commission += total_devices * (config['commission']['basic1'] + config['commission']['basic2'])
    
    # 구간별 추가 수수료
    if 5 <= total_devices <= 9:
        commission += config['commission']['range']['5-9']
    elif 10 <= total_devices <= 19:
        commission += config['commission']['range']['10-19']
    elif 20 <= total_devices <= 29:
        commission += config['commission']['range']['20-29']
    elif total_devices >= 30:
        commission += config['commission']['range']['30+']
    
    # 신한은행 주거래 통장
    if use_shinhan:
        commission += config['commission']['shinhan_bonus']
    
    # 땡겨요 어플 설치
    if use_tanggua:
        commission += config['commission']['tanggua_bonus']
    
    # 인터넷 신규/기존KT 수수료
    if use_internet_new:
        commission += config['commission']['internet_new'] + config['commission']['internet_kt']
    elif use_internet_kt:
        commission += config['commission']['internet_kt']
    
    return commission

def apply_custom_css():
    st.markdown("""
        <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
        <style>
            /* 기본 폰트 설정 */
            * {
                font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
            }
            
            /* 마크다운 헤더 크기 및 마진 조정 */
            .stMarkdown h1 {
                font-size: 1.8em !important;
                font-weight: 700 !important;
                margin: 0.5em 0 !important;
            }
            
            .stMarkdown h2 {
                font-size: 1.5em !important;
                font-weight: 600 !important;
                margin: 0.4em 0 !important;
            }
            
            .stMarkdown h3 {
                font-size: 1.2em !important;
                font-weight: 600 !important;
                margin: 0.3em 0 !important;
            }
            
            /* 강조 색상 설정 */
            .stMarkdown a, 
            .stMarkdown strong,
            .stMarkdown em {
                color: rgb(0, 113, 255) !important;
            }
            
            /* 버든 버튼 기본 스타일 (button과 download_button 모두 포함) */
            .stButton button,
            .stDownloadButton button {
                background-color: rgb(0, 113, 255) !important;
                color: white !important;
                border: none !important;
                padding: 0.5rem 1rem !important;
                border-radius: 4px !important;
                transition: all 0.3s ease !important;
            }
            
            /* 버튼 호버 효과 */
            .stButton button:hover,
            .stDownloadButton button:hover {
                background-color: rgb(0, 90, 204) !important;
                color: white !important;
                border: none !important;
            }
            
            /* 사이드바 버튼 특별 스타일 */
            .sidebar .stButton button {
                width: 100% !important;
                text-align: left !important;
                background-color: transparent !important;
                color: rgb(0, 113, 255) !important;
                border: 1px solid rgb(0, 113, 255) !important;
                margin-bottom: 0.2rem !important;
            }
            
            /* 사이드바 버튼 호버 효과 */
            .sidebar .stButton button:hover {
                background-color: rgba(0, 113, 255, 0.1) !important;
                color: rgb(0, 113, 255) !important;
            }
            
            /* 선택된 항목 강조 */
            .stSelectbox:focus,
            .stTextInput:focus {
                border-color: rgb(0, 113, 255) !important;
            }
            
            /* 프로그레스 바 색상 */
            .stProgress > div > div > div > div {
                background-color: rgb(0, 113, 255) !important;
            }
            
            /* 체크박스, 라디오 버튼 등의 강조 색상 */
            .stCheckbox:checked,
            .stRadio:checked {
                background-color: rgb(0, 113, 255) !important;
            }
            
            /* 코드 블록 스타일링 */
            code {
                color: rgb(0, 113, 255) !important;
                background-color: rgba(0, 113, 255, 0.1) !important;
                padding: 0.2em 0.4em !important;
                border-radius: 3px !important;
            }
            
            /* 로그인 폼 스타일링 */
            .login-form {
                max-width: 400px;
                margin: 0 auto;
                padding: 2rem;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            .login-form input {
                width: 100%;
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)


# 일시불 처리 가능 대수 계산
def calculate_lump_sum_devices(store_device_count, device_type, commission, config):
    if device_type == "normal":
        lump_sum_price = config['prices']['store_device']['normal']['lump_sum']
    else:  # calc
        lump_sum_price = config['prices']['store_device']['calc']['lump_sum']
    
    possible_devices = math.floor(commission / lump_sum_price)
    actual_devices = min(possible_devices, store_device_count)
    remaining_commission = commission - (actual_devices * lump_sum_price)
    
    return actual_devices, remaining_commission

def main():
    st.set_page_config(page_title="하이오더 월 비용 계산기", layout="wide")
    apply_custom_css()
    
    config = load_config()
    
    # 사이드바에 페이지 이동 버튼 추가
    with st.sidebar:
        st.markdown("### 메뉴")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 메인", use_container_width=True):
                st.session_state.page = "main"
        with col2:
            if st.button("⚙️ 관리자", use_container_width=True):
                st.session_state.page = "admin"
    
    # 메인 타이틀
    st.title("하이오더 계산기")
    st.markdown("<p style='font-size: 14px; margin-top: -15px; color: gray;'>3월정책반영</p>", unsafe_allow_html=True)
    
    # 세션 상태 초기화
    if "board_type" not in st.session_state:
        st.session_state.board_type = "15인치"
    if "device_type" not in st.session_state:
        st.session_state.device_type = "후불형"
    if "store_device_count" not in st.session_state:
        st.session_state.store_device_count = 10
    if "use_shinhan" not in st.session_state:
        st.session_state.use_shinhan = False
    if "use_tanggua" not in st.session_state:
        st.session_state.use_tanggua = False
    if "use_internet_new" not in st.session_state:
        st.session_state.use_internet_new = False
    if "use_internet_kt" not in st.session_state:
        st.session_state.use_internet_kt = False
    if "custom_commission" not in st.session_state:
        st.session_state.custom_commission = False
    if "custom_commission_amount" not in st.session_state:
        st.session_state.custom_commission_amount = 0
    if "commission" not in st.session_state:
        st.session_state.commission = 0
    if "calculation_done" not in st.session_state:
        st.session_state.calculation_done = False
    if "input_changed" not in st.session_state:
        st.session_state.input_changed = False
    
    # 입력값 변경 감지 함수
    def on_input_change():
        if st.session_state.calculation_done:
            st.session_state.input_changed = True
    
    # 기본 페이지 (사용자용)
    if "page" not in st.session_state or st.session_state.page == "main":
        # 입력 컨테이너
        input_container = st.container()
        
        with input_container:
            # 알림판 선택
            st.subheader("알림판 선택 (필수)")
            board_type = st.radio(
                "알림판 크기를 선택하세요:",
                ["15인치", "10인치"],
                format_func=lambda x: f"{x} (월 `{config['prices']['board']['inch'+x[:2]]:,}`원)",
                horizontal=True,
                index=0 if st.session_state.board_type == "15인치" else 1,
                key="board_type_radio",
                on_change=on_input_change
            )
            st.session_state.board_type = board_type
            
            st.caption(f"선택된 기기: **{board_type}** (월 `{config['prices']['board']['inch'+board_type[:2]]:,}`원)")
            
            st.markdown("---")
            
            # 입력값 변경 감지 시 경고 메시지 표시
            if st.session_state.input_changed:
                st.warning("⚠️ 입력값이 변경되었습니다. 변경된 값으로 다시 계산하려면 '계산하기' 버튼을 눌러주세요.")
            
            # 매장용 기기 종류
            st.subheader("결제방식 선택")
            device_type = st.radio(
                "결제방식을 선택하세요:",
                ["후불형", "선불형"],
                format_func=lambda x: f"{x} (월 `{config['prices']['store_device']['normal' if x=='후불형' else 'calc']['monthly']:,}`원)",
                horizontal=True,
                index=0 if st.session_state.device_type == "후불형" else 1,
                key="device_type_radio",
                on_change=on_input_change
            )
            st.session_state.device_type = device_type
            
            device_key = "normal" if device_type == "후불형" else "calc"
            
            st.caption(f"선택된 결제방식: **{device_type}** (월 `{config['prices']['store_device'][device_key]['monthly']:,}`원)")
            
            st.markdown("---")
            
            # 매장용 기기 개수
            st.subheader("테이블 개수")
            store_device_count = st.number_input(
                "테이블 수량을 입력하세요:",
                min_value=1,
                value=st.session_state.store_device_count,
                step=1,
                key="store_device_count_input",
                on_change=on_input_change
            )
            st.session_state.store_device_count = store_device_count
            
            st.markdown("---")
            
            # 신한은행 주거래 통장
            st.subheader("신한은행 주거래 통장")
            use_shinhan = st.checkbox(
                f"**신한은행 주거래 통장** 사용 (수수료 +`{config['commission']['shinhan_bonus']:,}`원)",
                value=st.session_state.use_shinhan,
                key="use_shinhan_checkbox",
                on_change=on_input_change
            )
            st.session_state.use_shinhan = use_shinhan
            
            use_tanggua = st.checkbox(
                f"**땡겨요어플설치** (수수료 +`{config['commission']['tanggua_bonus']:,}`원)",
                value=st.session_state.use_tanggua,
                key="use_tanggua_checkbox",
                on_change=on_input_change
            )
            st.session_state.use_tanggua = use_tanggua
            
            st.markdown("---")
            
            # 인터넷 관련 체크박스
            st.subheader("인터넷 결합")
            
            internet_kt_fee = config['commission']['internet_kt']
            internet_new_fee = config['commission']['internet_new']
            monthly_discount = config['internet']['monthly_discount']
            
            use_internet_new = st.checkbox(
                f"**인터넷 신규** 신청 (수수료 +`{internet_new_fee:,}`원, 월 `{monthly_discount:,}`원 할인)",
                value=st.session_state.use_internet_new,
                key="use_internet_new_checkbox",
                on_change=on_input_change
            )
            st.session_state.use_internet_new = use_internet_new
            
            use_internet_kt = st.checkbox(
                f"**기존 KT 인터넷** 사용 (으랏차차 패키지 +`{internet_kt_fee:,}`원, 월 `{monthly_discount:,}`원 할인)",
                value=use_internet_new or st.session_state.use_internet_kt,
                disabled=use_internet_new,
                key="use_internet_kt_checkbox",
                on_change=on_input_change
            )
            st.session_state.use_internet_kt = use_internet_kt
            
            if use_internet_new:
                st.caption(f"👆 인터넷 신규 신청 시 으랏차차 패키지(`{internet_kt_fee:,}`원)가 자동으로 포함됩니다.")
            
            st.markdown("---")
            
            # 계산하기 버튼
            if st.button("계산하기", type="primary", use_container_width=True):
                # 입력값 변경 플래그 초기화
                st.session_state.input_changed = False
                
                # 총 기기 수 (알림판 1대 + 매장용 기기)
                total_devices = store_device_count + 1
                
                # 수수료 계산
                commission = calculate_commission(total_devices, config, use_shinhan, use_internet_new, use_internet_kt, use_tanggua)
                st.session_state.commission = commission
                st.session_state.calculation_done = True
                st.session_state.custom_commission_amount = commission  # 기본값 설정
                
                # 일시불 처리 가능 대수 계산
                actual_devices, remaining_commission = calculate_lump_sum_devices(
                    store_device_count,
                    device_key,
                    commission,
                    config
                )
                
                # 월 비용 계산
                monthly_service_fee = total_devices * config['service_fee']
                
                # 알림판 월 할부금
                board_monthly = config['prices']['board']['inch10' if board_type == "10인치" else 'inch15']
                
                # 매장용 기기 월 할부금 (일시불 처리 후 남은 기기만)
                remaining_devices = store_device_count - actual_devices
                device_monthly = config['prices']['store_device'][device_key]['monthly']
                store_device_monthly = remaining_devices * device_monthly
                
                # 총 월 비용
                total_monthly = monthly_service_fee + board_monthly + store_device_monthly
                
                # 남은 수수료를 36개월로 나누어 월 비용에서 차감
                monthly_commission_discount = remaining_commission / 36
                
                # 인터넷 결합 할인 적용
                internet_discount = config['internet']['monthly_discount'] if (use_internet_new or use_internet_kt) else 0
                
                final_monthly = total_monthly - monthly_commission_discount - internet_discount
                
                # 기기당 월 예상 금액
                per_device_monthly = final_monthly / total_devices
                
                # 계산 관련 값들을 세션 상태에 저장
                st.session_state.total_devices = total_devices
                st.session_state.board_monthly = board_monthly
                st.session_state.board_type = board_type
                st.session_state.device_monthly = device_monthly
                st.session_state.device_type = device_type
                st.session_state.store_device_count = store_device_count
                st.session_state.device_key = device_key
                st.session_state.monthly_service_fee = monthly_service_fee
                st.session_state.remaining_devices = remaining_devices
                st.session_state.store_device_monthly = store_device_monthly
                st.session_state.total_monthly = total_monthly
                st.session_state.monthly_commission_discount = monthly_commission_discount
                st.session_state.internet_discount = internet_discount
                st.session_state.final_monthly = final_monthly
                st.session_state.per_device_monthly = per_device_monthly
                st.session_state.actual_devices = actual_devices
                st.session_state.remaining_commission = remaining_commission
            
            # 계산 결과 표시 (세션 상태에 저장된 값 사용)
            if "calculation_done" in st.session_state and st.session_state.calculation_done:
                st.markdown("---")
                st.subheader("계산 결과")
                
                # 기기당 월 예상 금액
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"### 기기당 월 예상 금액: **{st.session_state.per_device_monthly:,.0f}**원")
                    st.caption(f"36개월 총 비용: `{st.session_state.final_monthly * 36:,}`원")
                
                with col2:
                    # 수수료별도적용 체크박스 상태 유지
                    custom_commission = st.checkbox(
                        "수수료별도적용", 
                        value=st.session_state.custom_commission,
                        key="custom_commission_checkbox"
                    )
                    st.session_state.custom_commission = custom_commission
                    
                    if custom_commission:
                        st.markdown(f"**원래 총 수수료**: {st.session_state.commission:,}원")
                        
                        # 최대값을 더 높게 설정하여 더 큰 수수료도 입력 가능하게 함
                        max_commission = max(int(st.session_state.commission) * 2, int(st.session_state.commission) + 1000000)
                        
                        custom_commission_amount = st.number_input(
                            "적용할 수수료 금액",
                            min_value=0,
                            max_value=max_commission,
                            value=int(st.session_state.custom_commission_amount) if st.session_state.custom_commission_amount > 0 else int(st.session_state.commission),
                            step=100000,
                            key="custom_commission_amount_input"
                        )
                        st.session_state.custom_commission_amount = custom_commission_amount
                        
                        # 사용자 지정 수수료로 재계산
                        if custom_commission_amount != st.session_state.commission:
                            try:
                                # 일시불 처리 가능 대수 재계산
                                actual_devices_custom, remaining_commission_custom = calculate_lump_sum_devices(
                                    st.session_state.store_device_count,
                                    st.session_state.device_key,
                                    custom_commission_amount,
                                    config
                                )
                                
                                # 월 비용 재계산
                                remaining_devices_custom = st.session_state.store_device_count - actual_devices_custom
                                store_device_monthly_custom = remaining_devices_custom * st.session_state.device_monthly
                                
                                total_monthly_custom = st.session_state.monthly_service_fee + st.session_state.board_monthly + store_device_monthly_custom
                                monthly_commission_discount_custom = remaining_commission_custom / 36
                                
                                final_monthly_custom = total_monthly_custom - monthly_commission_discount_custom - st.session_state.internet_discount
                                
                                per_device_monthly_custom = final_monthly_custom / st.session_state.total_devices
                                
                                # 수수료 차이와 월 예상금액 차이 계산
                                commission_diff = custom_commission_amount - st.session_state.commission
                                monthly_diff = per_device_monthly_custom - st.session_state.per_device_monthly
                                
                                # 결과를 색상으로 구분하여 표시
                                st.markdown(f"### 재계산된 기기당 월 예상 금액: **{per_device_monthly_custom:,.0f}**원")
                                
                                st.caption(f"36개월 총 비용: `{final_monthly_custom * 36:,}`원")
                                
                                # 월 비용 상세 표 생성 (수수료별도적용)
                                monthly_details_custom = [
                                    ["구분", "계산식", "금액"],
                                    ["1. 월 서비스 이용료", f"`{config['service_fee']:,}`원 × `{st.session_state.total_devices}`대", f"`{st.session_state.monthly_service_fee:,}`원"],
                                    ["2. 알림판 할부금", f"{st.session_state.board_type} 할부금 (`{st.session_state.board_monthly:,}`원)", f"`{st.session_state.board_monthly:,}`원"],
                                    ["3. 매장용 기기 할부금", f"`{st.session_state.device_monthly:,}`원 × `{remaining_devices_custom}`대", f"`{store_device_monthly_custom:,}`원"],
                                    ["4. 남은 수수료 할인", f"(`{remaining_commission_custom:,}`원 ÷ 36개월)", f"-`{monthly_commission_discount_custom:,.0f}`원"]
                                ]
                                
                                if st.session_state.internet_discount > 0:
                                    monthly_details_custom.append(["5. 인터넷 결합 할인", f"월 고정 할인", f"-`{st.session_state.internet_discount:,}`원"])
                                
                                monthly_details_custom.append(["월 총액", "1 + 2 + 3 - 4 - 5", f"`{final_monthly_custom:,.0f}`원"])
                                
                                df_monthly_custom = pd.DataFrame(monthly_details_custom[1:], columns=monthly_details_custom[0])
                                st.table(df_monthly_custom)
                                
                                st.markdown(f"""
                                ### 5. 기기당 월 예상 금액 계산 (수수료별도적용)
                                - 계산식: 월 총액 ÷ 총 기기 수
                                - = `{final_monthly_custom:,.0f}`원 ÷ `{st.session_state.total_devices}`대
                                - = `{per_device_monthly_custom:,.0f}`원

                                ### 6. 36개월 총 비용 예상 (수수료별도적용)
                                - 월 고정 비용: `{final_monthly_custom:,.0f}`원
                                - 36개월 총 비용: `{final_monthly_custom * 36:,}`원
                                - 일시불 처리 비용: `{actual_devices_custom}`대 × `{config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`원 = `{actual_devices_custom * config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`원
                                - 남은 수수료: `{remaining_commission_custom:,}`원 (월 `{monthly_commission_discount_custom:,.0f}`원씩 36개월 할인)
                                
                                ### 7. 원래 계산과 비교
                                - 원래 기기당 월 예상 금액: `{st.session_state.per_device_monthly:,.0f}`원
                                - 재계산된 기기당 월 예상 금액: `{per_device_monthly_custom:,.0f}`원
                                - 차이: `{per_device_monthly_custom - st.session_state.per_device_monthly:,.0f}`원
                                """)
                            
                            except Exception as e:
                                st.error(f"계산 중 오류가 발생했습니다: {str(e)}")
                                st.info("수수료 금액을 다시 확인해주세요.")
                            
                            # 수수료별도적용 상세 내역 표시 (새로 추가)
                            with st.expander("수수료별도적용 자세히 보기"):
                                st.info("이 섹션은 사용자가 직접 설정한 수수료 금액으로 계산한 결과를 보여줍니다.")
                                st.markdown(f"""
                                ### 1. 기본 정보 (수수료별도적용)
                                - 총 기기 수: `{st.session_state.total_devices}`대
                                  - 알림판: `1`대 ({st.session_state.board_type}, 월 `{st.session_state.board_monthly:,}`원)
                                  - 매장용 기기: `{st.session_state.store_device_count}`대 ({st.session_state.device_type}, 월 `{st.session_state.device_monthly:,}`원)

                                ### 2. 수수료 계산 상세 (수수료별도적용)
                                - 적용 수수료: `{custom_commission_amount:,}`원 (원래 수수료: `{st.session_state.commission:,}`원)
                                  - 수수료 변동액: `{custom_commission_amount - st.session_state.commission:,}`원
                                
                                ### 3. 일시불 처리 계산 (수수료별도적용)
                                - 매장용 기기 일시불 가격: `{config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`원
                                - 총 수수료: `{custom_commission_amount:,}`원
                                - 일시불 처리 가능 대수: `{actual_devices_custom}`대 (원래: `{st.session_state.actual_devices}`대)
                                  - 계산식: min(⌊수수료 ÷ 일시불가격⌋, 매장용기기수)
                                  - = min(⌊`{custom_commission_amount:,}` ÷ `{config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`⌋, `{st.session_state.store_device_count}`)
                                  - = min(`{math.floor(custom_commission_amount/config['prices']['store_device'][st.session_state.device_key]['lump_sum'])}`, `{st.session_state.store_device_count}`)
                                  - = `{actual_devices_custom}`

                                ### 4. 월 비용 상세 계산 (수수료별도적용)
                                """)
                
                # 자세히 보기
                with st.expander("기본 계산 자세히 보기"):
                    st.info("이 섹션은 기본 계산 방식으로 산출된 결과를 상세하게 보여줍니다.")
                    st.markdown(f"""
                    ### 1. 기본 정보
                    - 총 기기 수: `{st.session_state.total_devices}`대
                      - 알림판: `1`대 ({st.session_state.board_type}, 월 `{st.session_state.board_monthly:,}`원)
                      - 매장용 기기: `{st.session_state.store_device_count}`대 ({st.session_state.device_type}, 월 `{st.session_state.device_monthly:,}`원)

                    ### 2. 수수료 계산 상세
                    #### 2.1 기본 수수료
                    - 기본 수수료 1: `{st.session_state.total_devices:,}`대 × `{config['commission']['basic1']:,}`원 = `{st.session_state.total_devices * config['commission']['basic1']:,}`원
                    - 기본 수수료 2: `{st.session_state.total_devices:,}`대 × `{config['commission']['basic2']:,}`원 = `{st.session_state.total_devices * config['commission']['basic2']:,}`원
                    
                    #### 2.2 조건부 수수료
                    """)

                    # 수수료 상세 내역 표 생성
                    commission_details = []
                    
                    # 기본 수수료
                    base_commission = st.session_state.total_devices * (config['commission']['basic1'] + config['commission']['basic2'])
                    commission_details.append(["기본 수수료", f"`{base_commission:,}`원"])
                    
                    # 구간별 추가 수수료
                    range_bonus = 0
                    range_text = ""
                    if 5 <= st.session_state.total_devices <= 9:
                        range_bonus = config['commission']['range']['5-9']
                        range_text = "5-9대"
                    elif 10 <= st.session_state.total_devices <= 19:
                        range_bonus = config['commission']['range']['10-19']
                        range_text = "10-19대"
                    elif 20 <= st.session_state.total_devices <= 29:
                        range_bonus = config['commission']['range']['20-29']
                        range_text = "20-29대"
                    elif st.session_state.total_devices >= 30:
                        range_bonus = config['commission']['range']['30+']
                        range_text = "30대 이상"
                    
                    if range_bonus > 0:
                        commission_details.append([f"구간별 보너스 ({range_text})", f"`{range_bonus:,}`원"])
                    
                    # 신한은행 보너스
                    if use_shinhan:
                        commission_details.append(["신한은행 주거래 보너스", f"`{config['commission']['shinhan_bonus']:,}`원"])
                    
                    # 땡겨요 앱 설치 보너스
                    if use_tanggua:
                        commission_details.append(["땡겨요 앱 설치 보너스", f"`{config['commission']['tanggua_bonus']:,}`원"])
                    
                    # 인터넷 관련 수수료
                    if use_internet_new:
                        commission_details.append(["인터넷 신규 신청 보너스", f"`{config['commission']['internet_new']:,}`원"])
                        commission_details.append(["KT 인터넷 기본 수수료", f"`{config['commission']['internet_kt']:,}`원"])
                    elif use_internet_kt:
                        commission_details.append(["기존 KT 인터넷 보너스", f"`{config['commission']['internet_kt']:,}`원"])
                    
                    # 총 수수료
                    commission_details.append(["총 수수료", f"`{st.session_state.commission:,}`원"])
                    
                    # 표 생성 및 표시
                    df = pd.DataFrame(commission_details, columns=["구분", "금액"])
                    st.table(df)
                    
                    st.markdown(f"""
                    ### 3. 일시불 처리 계산
                    - 매장용 기기 일시불 가격: `{config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`원
                    - 총 수수료: `{st.session_state.commission:,}`원
                    - 일시불 처리 가능 대수: `{st.session_state.actual_devices}`대
                      - 계산식: min(⌊수수료 ÷ 일시불가격⌋, 매장용기기수)
                      - = min(⌊`{st.session_state.commission:,}` ÷ `{config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`⌋, `{st.session_state.store_device_count}`)
                      - = min(`{math.floor(st.session_state.commission/config['prices']['store_device'][st.session_state.device_key]['lump_sum'])}`, `{st.session_state.store_device_count}`)
                      - = `{st.session_state.actual_devices}`

                    ### 4. 월 비용 상세 계산
                    """)
                    
                    # 월 비용 상세 표 생성
                    monthly_details = [
                        ["구분", "계산식", "금액"],
                        ["1. 월 서비스 이용료", f"`{config['service_fee']:,}`원 × `{st.session_state.total_devices}`대", f"`{st.session_state.monthly_service_fee:,}`원"],
                        ["2. 알림판 할부금", f"{st.session_state.board_type} 할부금 (`{st.session_state.board_monthly:,}`원)", f"`{st.session_state.board_monthly:,}`원"],
                        ["3. 매장용 기기 할부금", f"`{st.session_state.device_monthly:,}`원 × `{st.session_state.remaining_devices}`대", f"`{st.session_state.store_device_monthly:,}`원"],
                        ["4. 남은 수수료 할인", f"(`{st.session_state.remaining_commission:,}`원 ÷ 36개월)", f"-`{st.session_state.monthly_commission_discount:,.0f}`원"]
                    ]
                    
                    if st.session_state.internet_discount > 0:
                        monthly_details.append(["5. 인터넷 결합 할인", f"월 고정 할인", f"-`{st.session_state.internet_discount:,}`원"])
                    
                    monthly_details.append(["월 총액", "1 + 2 + 3 - 4 - 5", f"`{st.session_state.final_monthly:,.0f}`원"])
                    
                    df_monthly = pd.DataFrame(monthly_details[1:], columns=monthly_details[0])
                    st.table(df_monthly)
                    
                    st.markdown(f"""
                    ### 5. 기기당 월 예상 금액 계산
                    - 계산식: 월 총액 ÷ 총 기기 수
                    - = `{st.session_state.final_monthly:,.0f}`원 ÷ `{st.session_state.total_devices}`대
                    - = `{st.session_state.per_device_monthly:,.0f}`원

                    ### 6. 36개월 총 비용 예상
                    - 월 고정 비용: `{st.session_state.final_monthly:,.0f}`원
                    - 36개월 총 비용: `{st.session_state.final_monthly * 36:,}`원
                    - 일시불 처리 비용: `{st.session_state.actual_devices}`대 × `{config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`원 = `{st.session_state.actual_devices * config['prices']['store_device'][st.session_state.device_key]['lump_sum']:,}`원
                    - 남은 수수료: `{st.session_state.remaining_commission:,}`원 (월 `{st.session_state.monthly_commission_discount:,.0f}`원씩 36개월 할인)
                    """)
    
    # 관리자 페이지
    elif st.session_state.page == "admin":
        st.title("관리자 설정")
        
        # 관리자 인증
        admin_code = st.text_input("관리자 코드를 입력하세요:", type="password")
        
        if admin_code == config['admin_code']:
            st.success("인증되었습니다.")
            
            st.markdown("---")
            
            # 가격 설정
            st.subheader("매장용 기기 가격 설정")
            
            # 후불형 매장용 기기
            st.markdown("##### 후불형 매장용 기기")
            config['prices']['store_device']['normal']['monthly'] = st.number_input(
                "월 할부금",
                value=config['prices']['store_device']['normal']['monthly'],
                step=1000
            )
            config['prices']['store_device']['normal']['lump_sum'] = st.number_input(
                "일시불 가격",
                value=config['prices']['store_device']['normal']['lump_sum'],
                step=10000
            )
            
            st.markdown("---")
            
            # 선불형 매장용 기기
            st.markdown("##### 선불형 매장용 기기")
            config['prices']['store_device']['calc']['monthly'] = st.number_input(
                "월 할부금 (선불형)",
                value=config['prices']['store_device']['calc']['monthly'],
                step=1000
            )
            config['prices']['store_device']['calc']['lump_sum'] = st.number_input(
                "일시불 가격 (선불형)",
                value=config['prices']['store_device']['calc']['lump_sum'],
                step=10000
            )
            
            st.markdown("---")
            
            # 알림판 설정
            st.subheader("알림판 가격 설정")
            config['prices']['board']['inch10'] = st.number_input(
                "10인치 월 할부금",
                value=config['prices']['board']['inch10'],
                step=1000
            )
            config['prices']['board']['inch15'] = st.number_input(
                "15인치 월 할부금",
                value=config['prices']['board']['inch15'],
                step=1000
            )
            
            st.markdown("---")
            
            # 서비스 이용료
            st.subheader("서비스 이용료 설정")
            config['service_fee'] = st.number_input(
                "월 서비스 이용료 (기기당)",
                value=config['service_fee'],
                step=1000
            )
            
            st.markdown("---")
            
            # 수수료 설정
            st.subheader("수수료 설정")
            
            # 기본 수수료
            st.markdown("##### 기본 수수료 (기기당)")
            config['commission']['basic1'] = st.number_input(
                "기본 수수료 1",
                value=config['commission']['basic1'],
                step=1000
            )
            config['commission']['basic2'] = st.number_input(
                "기본 수수료 2",
                value=config['commission']['basic2'],
                step=1000
            )
            
            st.markdown("---")
            
            # 조건부 수수료
            st.markdown("##### 조건부 수수료")
            
            # 구간별 수수료
            st.markdown("##### 구간별 추가 수수료")
            
            # 새로운 구간별 수수료 설정
            config['commission']['range']['5-9'] = st.number_input(
                "5~9대", 
                value=config['commission']['range']['5-9'], 
                step=10000
            )
            config['commission']['range']['10-19'] = st.number_input(
                "10~19대", 
                value=config['commission']['range']['10-19'], 
                step=10000
            )
            config['commission']['range']['20-29'] = st.number_input(
                "20~29대", 
                value=config['commission']['range']['20-29'], 
                step=10000
            )
            config['commission']['range']['30+'] = st.number_input(
                "30대 이상", 
                value=config['commission']['range']['30+'], 
                step=10000
            )
            
            st.markdown("---")
            
            # 신한은행 보너스
            st.markdown("##### 신한은행 주거래 통장 보너스")
            config['commission']['shinhan_bonus'] = st.number_input(
                "신한은행 주거래 통장 보너스",
                value=config['commission']['shinhan_bonus'],
                step=10000
            )
            
            # 땡겨요 앱 설치 보너스
            st.markdown("##### 땡겨요 앱 설치 보너스")
            config['commission']['tanggua_bonus'] = st.number_input(
                "땡겨요 앱 설치 보너스",
                value=config['commission']['tanggua_bonus'],
                step=10000
            )
            
            st.markdown("---")
            
            # 인터넷 관련 수수료
            st.markdown("##### 인터넷 관련 수수료")
            config['commission']['internet_new'] = st.number_input(
                "인터넷 신규 신청 수수료",
                value=config['commission']['internet_new'],
                step=10000
            )
            config['commission']['internet_kt'] = st.number_input(
                "기존 KT 인터넷 수수료",
                value=config['commission']['internet_kt'],
                step=10000
            )
            
            st.markdown("---")
            
            # 저장 버튼
            if st.button("설정 저장", type="primary", use_container_width=True):
                save_config(config)
                
                # 설정 변경 시 세션 상태 초기화
                for key in ["calculation_done", "input_changed", "commission"]:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.success("설정이 저장되었습니다. 메인 페이지로 돌아가서 다시 계산해주세요.")

if __name__ == "__main__":
    main() 