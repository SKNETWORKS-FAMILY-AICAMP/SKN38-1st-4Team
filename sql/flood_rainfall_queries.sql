-- ============================================================
-- 침수 지역 및 강우 위험도 분석 조회 SQL (flood_rainfall_queries.sql)
-- 데이터: parking_flood_distance, flood_area, parking_lot, rainfall_risk
--   → 주차장별 가장 가까운 침수 대표좌표까지의 거리와 자치구별 강우 위험도 산정 결과 조회
-- parking_flood_distance 는 주차장마다 가장 가까운 침수 대표좌표 1곳입니다(806행, 1,000m 를 넘는 거리 포함).
-- 실행: mysql -u <사용자> -p --default-character-set=utf8mb4 skn_1st_4team < sql/flood_rainfall_queries.sql
--       PowerShell 은 < 를 쓸 수 없으므로 끝을 -e "source sql/flood_rainfall_queries.sql" 로 바꿉니다.
-- 먼저 sql/skn_1st_4team.sql 을 오류 없이 끝까지 적재하세요. 아래 적재 확인 문장이 그 상태를 확인합니다.
-- ============================================================

-- 연결 문자셋을 utf8mb4 로 맞춥니다. 클라이언트 문자셋이 latin1·euckr 이어도 한글 값이 깨지지 않습니다.
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

-- 1. 특정 주차장의 가장 가까운 침수 대표좌표와 거리/위험도 조회
--    flood_risk_score = 침수심 점수 × 0.6 + 거리 점수 × 0.4 (0~100 척도, 화면 계산값, 소수 2자리)
--      침수심 점수 = depth_score × 100, 거리 점수 = (1 − distance_m ÷ 전체 최대 distance_m) × 100
SELECT
    p.parking_name,
    f.address AS flood_address,
    f.depth_m,
    d.distance_m,
    d.flood_risk_score
FROM parking_flood_distance d
JOIN parking_lot p ON d.parking_lot_id = p.parking_lot_id
JOIN flood_area f ON d.flood_id = f.flood_id
WHERE d.parking_lot_id = '115-3-000004-0';

-- 2. 자치구별 강우 위험도 점수 순위 조회 (사고 상위 5개 자치구 대상)
SELECT
    district_name,
    max_rain_1h,
    max_rain_3h,
    heavy_rain_days,
    rainfall_score
FROM rainfall_risk
ORDER BY rainfall_score DESC, district_id;
