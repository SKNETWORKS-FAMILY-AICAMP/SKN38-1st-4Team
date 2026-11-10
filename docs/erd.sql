CREATE TABLE `자치구 강수 위험도` (
	`district_id`	INT	NOT NULL,
	`district_name`	VARCHAR(20)	NOT NULL,
	`max_rain_1h`	DECIMAL(7,2)	NULL,
	`max_rain_3h`	DECIMAL(7,2)	NULL,
	`heavy_rain_days`	INT	NULL,
	`rainfall_score`	DECIMAL(5,2)	NULL
);

CREATE TABLE `자주 묻는 질문` (
	`faq_id`	VARCHAR(20)	NOT NULL,
	`category`	VARCHAR(50)	NULL,
	`question`	VARCHAR(255)	NULL,
	`answer`	TEXT	NULL
);

CREATE TABLE `주차장 위험도 분석 결과` (
	`result_id`	INT	NOT NULL,
	`parking_lot_id`	INT	NULL,
	`analysis_year`	YEAR	NULL,
	`flood_risk_score`	DECIMAL(5,2)	NULL,
	`rainfall_risk_score`	DECIMAL(5,2)	NULL,
	`lowland_risk_score`	DECIMAL(5,2)	NULL,
	`total_risk_score`	DECIMAL(5,2)	NULL,
	`risk_grade`	VARCHAR(20)	NULL,
	`risk_rank`	INT	NULL,
	`calculated_at`	DATETIME	NULL
);

CREATE TABLE `주차장` (
	`parking_lot_id`	VARCHAR(50)	NULL,
	`parking_name`	VARCHAR(50)	NULL,
	`address`	VARCHAR(50)	NULL,
	`latitude`	DECIMAL(10,7)	NULL,
	`longitude`	DECIMAL(10,7)	NULL,
	`district_id`	INT	NOT NULL
);

CREATE TABLE `자치구` (
	`district_id`	INT	NOT NULL,
	`district_name`	VARCHAR(50)	NULL
);

CREATE TABLE `USER` (
	`user_id`	VARCHAR(20)	NOT NULL,
	`username`	VARCHAR(50)	NULL,
	`password_hash`	VARCHAR(255)	NULL,
	`created_at`	DATETIME	NULL
);

CREATE TABLE `주차장 저지대 정보` (
	`parking_lot_id`	VARCHAR(50)	NULL,
	`lowland_score`	DECIMAL(5,2)	NULL
);

CREATE TABLE `침수 구역 정보` (
	`flood_id`	INT	NOT NULL,
	`address`	VARCHAR(200)	NULL,
	`latitude`	DECIMAL(10,7)	NULL,
	`longitude`	DECIMAL(10,7)	NULL,
	`depth_score`	DECIMAL(5,2)	NULL
);

CREATE TABLE `주차장 -침수구역 거리정보` (
	`parking_lot_id`	INT	NOT NULL,
	`flood_id`	INT	NOT NULL,
	`distance_m`	DECIMAL(10,2)	NULL,
	`flood_risk_score`	DECIMAL(5,2)	NULL
);

CREATE TABLE `FLOOD_HISTORY` (
	`flood_area_name`	VARCHAR(255)	NULL,
	`flood_depth`	DECIMAL(5,2)	NULL,
	`flood_area`	DECIMAL(12,4)	NULL,
	`avg_elevation`	DECIMAL(10,5)	NULL,
	`address`	VARCHAR(255)	NULL,
	`latitude`	DECIMAL(10,7)	NULL,
	`longitude`	DECIMAL(10,7)	NULL
);

CREATE TABLE `PARKING_ELEVATION` (
	`parking_id`	VARCHAR(20)	NULL,
	`parking_name`	VARCHAR(100)	NULL,
	`address`	VARCHAR(255)	NULL,
	`latitude`	DECIMAL(10,7)	NULL,
	`longitude`	DECIMAL(10,7)	NULL,
	`lowland_score`	DECIMAL(7,4)	NULL
);

CREATE TABLE `RAINFALL` (
	`station_id`	INT	NULL,
	`district`	VARCHAR(20)	NULL,
	`year`	YEAR	NULL,
	`max_1hr_rainfall`	DECIMAL(7,2)	NULL,
	`max_3hr_rainfall`	DECIMAL(7,2)	NULL,
	`heavy_rain_days`	INT	NULL
);

ALTER TABLE `자치구 강수 위험도` ADD CONSTRAINT `PK_자치구 강수 위험도` PRIMARY KEY (
	`district_id`
);

ALTER TABLE `자주 묻는 질문` ADD CONSTRAINT `PK_자주 묻는 질문` PRIMARY KEY (
	`faq_id`
);

ALTER TABLE `주차장 위험도 분석 결과` ADD CONSTRAINT `PK_주차장 위험도 분석 결과` PRIMARY KEY (
	`result_id`,
	`parking_lot_id`
);

ALTER TABLE `주차장` ADD CONSTRAINT `PK_주차장` PRIMARY KEY (
	`parking_lot_id`
);

ALTER TABLE `자치구` ADD CONSTRAINT `PK_자치구` PRIMARY KEY (
	`district_id`
);

ALTER TABLE `USER` ADD CONSTRAINT `PK_USER` PRIMARY KEY (
	`user_id`
);

ALTER TABLE `주차장 저지대 정보` ADD CONSTRAINT `PK_주차장 저지대 정보` PRIMARY KEY (
	`parking_lot_id`
);

ALTER TABLE `침수 구역 정보` ADD CONSTRAINT `PK_침수 구역 정보` PRIMARY KEY (
	`flood_id`
);

ALTER TABLE `주차장 -침수구역 거리정보` ADD CONSTRAINT `PK_주차장 -침수구역 거리정보` PRIMARY KEY (
	`parking_lot_id`,
	`flood_id`
);

ALTER TABLE `FLOOD_HISTORY` ADD CONSTRAINT `PK_FLOOD_HISTORY` PRIMARY KEY (
	`flood_area_name`
);

ALTER TABLE `PARKING_ELEVATION` ADD CONSTRAINT `PK_PARKING_ELEVATION` PRIMARY KEY (
	`parking_id`
);

ALTER TABLE `RAINFALL` ADD CONSTRAINT `PK_RAINFALL` PRIMARY KEY (
	`station_id`
);

ALTER TABLE `자치구 강수 위험도` ADD CONSTRAINT `FK_자치구_TO_자치구 강수 위험도_1` FOREIGN KEY (
	`district_id`
)
REFERENCES `자치구` (
	`district_id`
);

ALTER TABLE `주차장 위험도 분석 결과` ADD CONSTRAINT `FK_주차장 저지대 정보_TO_주차장 위험도 분석 결과_1` FOREIGN KEY (
	`parking_lot_id`
)
REFERENCES `주차장 저지대 정보` (
	`parking_lot_id`
);

ALTER TABLE `주차장 저지대 정보` ADD CONSTRAINT `FK_주차장_TO_주차장 저지대 정보_1` FOREIGN KEY (
	`parking_lot_id`
)
REFERENCES `주차장` (
	`parking_lot_id`
);

ALTER TABLE `주차장 -침수구역 거리정보` ADD CONSTRAINT `FK_침수 구역 정보_TO_주차장 -침수구역 거리정보_1` FOREIGN KEY (
	`flood_id`
)
REFERENCES `침수 구역 정보` (
	`flood_id`
);

