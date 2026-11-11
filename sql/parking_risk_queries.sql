-- ============================================================
-- 주차장 위험도 분석 결과 조회 SQL (parking_risk_queries.sql)
-- 데이터: parking_risk_result, parking_lot, parking_lowland, parking_flood_distance, flood_area
--   → 연도별 종합 위험도 순위, 위험 등급('높음' 등), 저지대 점수, 화면과 같은 순서의 전체 조회
-- 실행: mysql -u <사용자> -p --default-character-set=utf8mb4 skn_1st_4team < sql/parking_risk_queries.sql
--       PowerShell 은 < 를 쓸 수 없으므로 끝을 -e "source sql/parking_risk_queries.sql" 로 바꿉니다.
-- 먼저 sql/skn_1st_4team.sql 을 오류 없이 끝까지 적재하세요. 아래 적재 확인 문장이 그 상태를 확인합니다.
-- ============================================================

-- 연결 문자셋을 utf8mb4 로 맞춥니다. 클라이언트 문자셋이 latin1·euckr 이어도 한글 조건('높음')이 맞게 비교됩니다.
SET NAMES utf8mb4;

-- 적재 확인: 정렬판 덤프가 끝까지 들어간 DB 인지 봅니다(위험지수 열의 정수 형식과 테이블마다 행 수).
--   팀 덤프만 있거나 적재가 중간에 끊겼으면 ERROR 1146(새_덤프를_먼저_끝까지_적재하세요 테이블 없음)으로 멈추고 아무것도 출력하지 않습니다.
SET @skn_check = IF(
    (SELECT NUMERIC_SCALE FROM information_schema.columns WHERE table_schema = DATABASE()
       AND table_name = 'parking_risk_result' AND column_name = 'total_risk_score') = 0
    AND (SELECT COUNT(*) FROM faq) = 27 AND (SELECT COUNT(*) FROM flood_area) = 1132
    AND (SELECT COUNT(*) FROM parking_flood_distance) = 806 AND (SELECT COUNT(*) FROM parking_lot) = 806
    AND (SELECT COUNT(*) FROM parking_lowland) = 806 AND (SELECT COUNT(*) FROM parking_risk_result) = 806
    AND (SELECT COUNT(*) FROM rainfall_risk) = 5,
    'DO 0', 'SELECT * FROM `새_덤프를_먼저_끝까지_적재하세요`');
PREPARE skn_check FROM @skn_check;
EXECUTE skn_check;
DEALLOCATE PREPARE skn_check;

-- 1. 분석 연도별 주차장 위험도 종합 순위 조회
--    2025년 자료 중 점수 CSV에서 최종 위험지수를 가져온 주차장이 나옵니다.
--    점수가 같으면 순위도 같습니다(같은 순위 안에서는 화면 순서 result_id 로 정렬).
SELECT
    r.risk_rank,
    p.parking_name,
    p.address,
    r.total_risk_score,
    r.risk_grade,
    r.flood_risk_score,
    r.rainfall_risk_score,
    r.lowland_risk_score,
    r.analysis_year
FROM parking_risk_result r
JOIN parking_lot p ON r.parking_lot_id = p.parking_lot_id
WHERE r.analysis_year = 2025 AND r.total_risk_score IS NOT NULL
ORDER BY r.risk_rank ASC, r.result_id ASC;

-- 2. 위험 등급이 '높음'인 주차장 리스트 조회 (화면과 같은 기준: 위험지수 60 이상 80 미만)
--    80점 이상은 '매우 높음'으로 저장됩니다. 둘 다 보려면 WHERE r.risk_grade IN ('매우 높음', '높음') 으로 바꾸세요.
SELECT
    p.parking_name,
    p.address,
    r.total_risk_score,
    r.risk_grade
FROM parking_risk_result r
JOIN parking_lot p ON r.parking_lot_id = p.parking_lot_id
WHERE r.risk_grade = '높음'
ORDER BY r.total_risk_score DESC, r.result_id ASC;

-- 3. 저지대 점수(lowland_score)가 높은 상위 주차장 조회
--    100점인 주차장이 10곳보다 많으므로 같은 점수 안에서는 주차장 관리번호 순으로 고릅니다.
SELECT
    p.parking_name,
    p.address,
    l.lowland_score
FROM parking_lowland l
JOIN parking_lot p ON l.parking_lot_id = p.parking_lot_id
ORDER BY l.lowland_score DESC, l.parking_lot_id ASC
LIMIT 10;

-- 4. 화면(프론트엔드)과 같은 순서로 전체 주차장 위험도 조회
--    result_id 가 화면의 주차장 번호입니다. 같은 점수의 정렬 순서와 상위·하위 3곳이 이 순서를 따르므로 ORDER BY result_id 로 읽습니다.
--    정수 위험지수는 total_risk_score 입니다. 아래 수식은 상세 화면의 참고 지표에 적용합니다.
--    침수심 점수 = depth_score × 100,
--    거리 점수 = (1 − distance_m ÷ 전체 최대 distance_m) × 100, 강수위험도 = rainfall_risk_score, 저지대 = lowland_score
SELECT
    r.result_id,
    p.parking_lot_id,
    p.parking_name,
    p.address,
    p.latitude,
    p.longitude,
    r.total_risk_score,
    r.risk_grade,
    r.risk_rank,
    r.analysis_year,
    r.rainfall_risk_score,
    l.lowland_score,
    d.flood_id,
    d.distance_m,
    d.flood_risk_score,
    f.depth_m,
    f.depth_score
FROM parking_risk_result r
JOIN parking_lot p ON r.parking_lot_id = p.parking_lot_id
LEFT JOIN parking_lowland l ON l.parking_lot_id = r.parking_lot_id
LEFT JOIN parking_flood_distance d ON d.parking_lot_id = r.parking_lot_id
LEFT JOIN flood_area f ON f.flood_id = d.flood_id
ORDER BY r.result_id;
