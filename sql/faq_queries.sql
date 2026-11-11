-- ============================================================
-- FAQ 정보 조회 SQL (faq_queries.sql)
-- 데이터: faq 테이블 (화면 app.py 의 FAQ 5개, FAQ001~FAQ005)
--   → 화면 'FAQ' 탭과 같은 순서의 질문/답변 목록, 카테고리별 조회, 키워드 검색
-- 테이블 이름은 덤프(skn_1st_4team.sql)와 같은 소문자입니다. 리눅스 MySQL 은 테이블 이름의 대소문자를 구분합니다.
-- 실행: mysql -u <사용자> -p --default-character-set=utf8mb4 skn_1st_4team < sql/faq_queries.sql
--       PowerShell 은 < 를 쓸 수 없으므로 끝을 -e "source sql/faq_queries.sql" 로 바꿉니다.
-- 먼저 sql/skn_1st_4team.sql 을 오류 없이 끝까지 적재하세요. 아래 적재 확인 문장이 그 상태를 확인합니다.
-- ============================================================

-- 연결 문자셋을 utf8mb4 로 맞춥니다. 클라이언트 문자셋이 latin1·euckr 이어도 한글 조건('위험지수')이 맞게 비교됩니다.
SET NAMES utf8mb4;

-- 적재 확인: 정렬판 덤프가 끝까지 들어간 DB 인지 봅니다(위험지수 열의 소수 자릿수와 테이블마다 행 수).
--   팀 덤프만 있거나 적재가 중간에 끊겼으면 ERROR 1146(새_덤프를_먼저_끝까지_적재하세요 테이블 없음)으로 멈추고 아무것도 출력하지 않습니다.
SET @skn_check = IF(
    (SELECT NUMERIC_SCALE FROM information_schema.columns WHERE table_schema = DATABASE()
       AND table_name = 'parking_risk_result' AND column_name = 'total_risk_score') = 4
    AND (SELECT COUNT(*) FROM faq) = 5 AND (SELECT COUNT(*) FROM flood_area) = 1132
    AND (SELECT COUNT(*) FROM parking_flood_distance) = 806 AND (SELECT COUNT(*) FROM parking_lot) = 806
    AND (SELECT COUNT(*) FROM parking_lowland) = 806 AND (SELECT COUNT(*) FROM parking_risk_result) = 806
    AND (SELECT COUNT(*) FROM rainfall_risk) = 5,
    'DO 0', 'SELECT * FROM `새_덤프를_먼저_끝까지_적재하세요`');
PREPARE skn_check FROM @skn_check;
EXECUTE skn_check;
DEALLOCATE PREPARE skn_check;

-- 1. 전체 FAQ 목록 조회 (화면 '전체 질문'과 같은 순서)
SELECT
    faq_id,
    category,
    question,
    answer
FROM faq
ORDER BY faq_id;

-- 2. 카테고리별 FAQ 조회 (화면 '질문 카테고리'에서 위험지수를 고른 결과와 같음)
SELECT
    faq_id,
    question,
    answer
FROM faq
WHERE category = '위험지수'
ORDER BY faq_id;

-- 3. 특정 키워드가 포함된 FAQ 검색
SELECT
    category,
    question,
    answer
FROM faq
WHERE question LIKE '%위험도%' OR answer LIKE '%위험도%'
ORDER BY faq_id;
