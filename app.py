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
def calculate_commission(total_devices, config, use_shinhan):
    commission = 0
    
    # 기본 수수료
    commission += total_devices * (config['commission']['basic1'] + config['commission']['basic2'])
    
    # 5대 이상 조건
    if total_devices >= 5:
        commission += config['commission']['cond1_over5']
    
    # 구간별 추가 수수료
    if 5 <= total_devices <= 10:
        commission += config['commission']['cond2_range']['5-10']
    elif 11 <= total_devices <= 20:
        commission += config['commission']['cond2_range']['11-20']
    elif 21 <= total_devices <= 30:
        commission += config['commission']['cond2_range']['21-30']
    elif 31 <= total_devices <= 40:
        commission += config['commission']['cond2_range']['31-40']
    elif total_devices >= 41:
        commission += config['commission']['cond2_range']['41-']
    
    # 신한은행 주거래 통장
    if use_shinhan:
        commission += config['commission']['shinhan_bonus']
    
    return commission

# 일시불 처리 가능 대수 계산
def calculate_lump_sum_devices(store_device_count, device_type, commission, config):
    if device_type == "normal":
        lump_sum_price = config['prices']['store_device']['normal']['lump_sum']
    else:  # calc
        lump_sum_price = config['prices']['store_device']['calc']['lump_sum']
    
    possible_devices = math.floor(commission / lump_sum_price)
    return min(possible_devices, store_device_count)

def main():
    st.set_page_config(page_title="하이오더 월 비용 계산기", layout="wide")
    
    config = load_config()
    
    # 헤더 영역
    header_col1, header_col2 = st.columns([4, 1])
    with header_col1:
        st.title("하이오더 월 비용 계산기")
    with header_col2:
        if st.button("관리자 페이지로 이동", type="secondary", use_container_width=True):
            st.session_state.page = "admin"
    
    # 세션 상태 초기화
    if "board_type" not in st.session_state:
        st.session_state.board_type = "10인치"
    if "device_type" not in st.session_state:
        st.session_state.device_type = "일반형"
    
    # 기본 페이지 (사용자용)
    if "page" not in st.session_state or st.session_state.page == "main":
        # 입력 컨테이너
        input_container = st.container()
        
        with input_container:
            # 알림판 선택
            st.subheader("알림판 선택 (필수)")
            board_type = st.radio(
                "알림판 크기를 선택하세요:",
                ["10인치", "15인치"],
                format_func=lambda x: f"{x} (월 `{config['prices']['board']['inch'+x[:2]]:,}`원)",
                horizontal=True,
                index=0 if st.session_state.board_type == "10인치" else 1
            )
            
            st.markdown("---")
            
            # 매장용 기기 종류
            st.subheader("매장용 기기 선택")
            device_type = st.radio(
                "매장용 기기 종류를 선택하세요:",
                ["일반형", "계산형"],
                format_func=lambda x: f"{x} (월 `{config['prices']['store_device']['normal' if x=='일반형' else 'calc']['monthly']:,}`원)",
                horizontal=True,
                index=0 if st.session_state.device_type == "일반형" else 1
            )
            
            device_key = "normal" if device_type == "일반형" else "calc"
            
            st.caption(f"선택된 기기: {device_type} (월 `{config['prices']['store_device'][device_key]['monthly']:,}`원)")
            
            st.markdown("---")
            
            # 매장용 기기 개수
            st.subheader("매장용 기기 개수")
            store_device_count = st.number_input(
                "매장용 기기 수량을 입력하세요:",
                min_value=1,
                value=10,
                step=1
            )
            
            st.markdown("---")
            
            # 신한은행 주거래 통장
            st.subheader("신한은행 주거래 통장")
            use_shinhan = st.checkbox(
                f"신한은행 주거래 통장 사용 (수수료 +`{config['commission']['shinhan_bonus']/10000:,.0f}`만원)"
            )
            
            st.markdown("---")
            
            # 계산하기 버튼
            if st.button("계산하기", type="primary", use_container_width=True):
                # 총 기기 수 (알림판 1대 + 매장용 기기)
                total_devices = store_device_count + 1
                
                # 수수료 계산
                commission = calculate_commission(total_devices, config, use_shinhan)
                
                # 일시불 처리 가능 대수 계산
                lump_sum_devices = calculate_lump_sum_devices(
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
                remaining_devices = store_device_count - lump_sum_devices
                device_monthly = config['prices']['store_device'][device_key]['monthly']
                store_device_monthly = remaining_devices * device_monthly
                
                # 총 월 비용
                total_monthly = monthly_service_fee + board_monthly + store_device_monthly
                
                # 기기당 월 예상 금액
                per_device_monthly = total_monthly / total_devices
                
                # 결과 표시
                st.markdown("---")
                st.subheader("계산 결과")
                st.markdown(f"### 기기당 월 예상 금액: {per_device_monthly:,.0f}원")
                
                # 자세히 보기
                with st.expander("자세히 보기"):
                    st.markdown(f"""
                    ### 1. 기본 정보
                    - **총 기기 수**: {total_devices}대
                      - 알림판: 1대 ({board_type}, 월 `{board_monthly:,}`원)
                      - 매장용 기기: {store_device_count}대 ({device_type}, 월 `{device_monthly:,}`원)

                    ### 2. 수수료 계산 상세
                    #### 2.1 기본 수수료
                    - 기본 수수료 1: {total_devices:,}대 × `{config['commission']['basic1']:,}`원 = {total_devices * config['commission']['basic1']:,}원
                    - 기본 수수료 2: {total_devices:,}대 × `{config['commission']['basic2']:,}`원 = {total_devices * config['commission']['basic2']:,}원
                    
                    #### 2.2 조건부 수수료
                    """)

                    # 수수료 상세 내역 표 생성
                    commission_details = []
                    
                    # 기본 수수료
                    base_commission = total_devices * (config['commission']['basic1'] + config['commission']['basic2'])
                    commission_details.append(["기본 수수료", f"{base_commission:,}원"])
                    
                    # 5대 이상 조건
                    if total_devices >= 5:
                        commission_details.append(["5대 이상 보너스", f"`{config['commission']['cond1_over5']:,}`원"])
                    
                    # 구간별 추가 수수료
                    range_bonus = 0
                    range_text = ""
                    if 5 <= total_devices <= 10:
                        range_bonus = config['commission']['cond2_range']['5-10']
                        range_text = "5-10대"
                    elif 11 <= total_devices <= 20:
                        range_bonus = config['commission']['cond2_range']['11-20']
                        range_text = "11-20대"
                    elif 21 <= total_devices <= 30:
                        range_bonus = config['commission']['cond2_range']['21-30']
                        range_text = "21-30대"
                    elif 31 <= total_devices <= 40:
                        range_bonus = config['commission']['cond2_range']['31-40']
                        range_text = "31-40대"
                    elif total_devices >= 41:
                        range_bonus = config['commission']['cond2_range']['41-']
                        range_text = "41대 이상"
                    
                    if range_bonus > 0:
                        commission_details.append([f"구간별 보너스 ({range_text})", f"`{range_bonus:,}`원"])
                    
                    # 신한은행 보너스
                    if use_shinhan:
                        commission_details.append(["신한은행 주거래 보너스", f"`{config['commission']['shinhan_bonus']:,}`원"])
                    
                    # 총 수수료
                    commission_details.append(["총 수수료", f"{commission:,}원"])
                    
                    # 표 생성 및 표시
                    df = pd.DataFrame(commission_details, columns=["구분", "금액"])
                    st.table(df)
                    
                    st.markdown(f"""
                    ### 3. 일시불 처리 계산
                    - 매장용 기기 일시불 가격: `{config['prices']['store_device'][device_key]['lump_sum']:,}`원
                    - 총 수수료: {commission:,}원
                    - 일시불 처리 가능 대수: {lump_sum_devices}대
                      - 계산식: min(⌊수수료 ÷ 일시불가격⌋, 매장용기기수)
                      - = min(⌊{commission:,} ÷ `{config['prices']['store_device'][device_key]['lump_sum']:,}`⌋, {store_device_count})
                      - = min({math.floor(commission/config['prices']['store_device'][device_key]['lump_sum'])}, {store_device_count})
                      - = {lump_sum_devices}

                    ### 4. 월 비용 상세 계산
                    """)
                    
                    # 월 비용 상세 표 생성
                    monthly_details = [
                        ["구분", "계산식", "금액"],
                        ["1. 월 서비스 이용료", f"`{config['service_fee']:,}`원 × {total_devices}대", f"{monthly_service_fee:,}원"],
                        ["2. 알림판 할부금", f"{board_type} 할부금 (`{board_monthly:,}`원)", f"{board_monthly:,}원"],
                        ["3. 매장용 기기 할부금", f"`{device_monthly:,}`원 × {remaining_devices}대", f"{store_device_monthly:,}원"],
                        ["월 총액", "1 + 2 + 3", f"{total_monthly:,}원"]
                    ]
                    
                    df_monthly = pd.DataFrame(monthly_details[1:], columns=monthly_details[0])
                    st.table(df_monthly)
                    
                    st.markdown(f"""
                    ### 5. 기기당 월 예상 금액 계산
                    - 계산식: 월 총액 ÷ 총 기기 수
                    - = {total_monthly:,}원 ÷ {total_devices}대
                    - = {per_device_monthly:,.0f}원

                    ### 6. 36개월 총 비용 예상
                    - 월 고정 비용: {total_monthly:,}원
                    - 36개월 총 비용: {total_monthly * 36:,}원
                    - 일시불 처리 비용: {lump_sum_devices}대 × `{config['prices']['store_device'][device_key]['lump_sum']:,}`원 = {lump_sum_devices * config['prices']['store_device'][device_key]['lump_sum']:,}원
                    """)
    
    # 관리자 페이지
    elif st.session_state.page == "admin":
        st.title("관리자 설정")
        
        # 메인 페이지로 돌아가기 버튼
        if st.button("메인 페이지로 돌아가기", type="secondary", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
        
        st.markdown("---")
        
        # 관리자 인증
        admin_code = st.text_input("관리자 코드를 입력하세요:", type="password")
        
        if admin_code == config['admin_code']:
            st.success("인증되었습니다.")
            
            st.markdown("---")
            
            # 가격 설정
            st.subheader("매장용 기기 가격 설정")
            
            # 일반형 매장용 기기
            st.markdown("##### 일반형 매장용 기기")
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
            
            # 계산형 매장용 기기
            st.markdown("##### 계산형 매장용 기기")
            config['prices']['store_device']['calc']['monthly'] = st.number_input(
                "월 할부금 (계산형)",
                value=config['prices']['store_device']['calc']['monthly'],
                step=1000
            )
            config['prices']['store_device']['calc']['lump_sum'] = st.number_input(
                "일시불 가격 (계산형)",
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
            config['commission']['cond1_over5'] = st.number_input(
                "5대 이상 추가 수수료",
                value=config['commission']['cond1_over5'],
                step=10000
            )
            
            # 구간별 수수료
            st.markdown("##### 구간별 추가 수수료")
            config['commission']['cond2_range']['5-10'] = st.number_input(
                "5-10대",
                value=config['commission']['cond2_range']['5-10'],
                step=10000
            )
            config['commission']['cond2_range']['11-20'] = st.number_input(
                "11-20대",
                value=config['commission']['cond2_range']['11-20'],
                step=10000
            )
            config['commission']['cond2_range']['21-30'] = st.number_input(
                "21-30대",
                value=config['commission']['cond2_range']['21-30'],
                step=10000
            )
            config['commission']['cond2_range']['31-40'] = st.number_input(
                "31-40대",
                value=config['commission']['cond2_range']['31-40'],
                step=10000
            )
            config['commission']['cond2_range']['41-'] = st.number_input(
                "41대 이상",
                value=config['commission']['cond2_range']['41-'],
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
            
            st.markdown("---")
            
            # 저장 버튼
            if st.button("설정 저장", type="primary", use_container_width=True):
                save_config(config)
                st.success("설정이 저장되었습니다.")

if __name__ == "__main__":
    main() 