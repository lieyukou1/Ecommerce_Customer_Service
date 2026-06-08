SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS `property_service_demo`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON `property_service_demo`.* TO 'atguigu'@'%';
FLUSH PRIVILEGES;

USE `property_service_demo`;

DROP TABLE IF EXISTS `work_order_urge_requests`;
DROP TABLE IF EXISTS `complaint_requests`;
DROP TABLE IF EXISTS `service_progress_traces`;
DROP TABLE IF EXISTS `service_progress_records`;
DROP TABLE IF EXISTS `work_orders`;
DROP TABLE IF EXISTS `resident_service_items`;
DROP TABLE IF EXISTS `service_items`;
DROP TABLE IF EXISTS `residents`;

CREATE TABLE `residents` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `resident_id` VARCHAR(64) NOT NULL UNIQUE,
  `name` VARCHAR(100) NOT NULL,
  `resident_level` VARCHAR(32) NOT NULL,
  `mobile_masked` VARCHAR(32) NOT NULL,
  `building` VARCHAR(64) NOT NULL,
  `room_no` VARCHAR(64) NOT NULL,
  `profile_note` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `service_items` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `service_item_id` VARCHAR(64) NOT NULL UNIQUE,
  `title` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  `price` DECIMAL(10, 2) NOT NULL,
  `service_status` VARCHAR(32) NOT NULL,
  `cover_url` VARCHAR(500) NULL,
  `attributes_json` JSON NOT NULL,
  `created_at` DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `resident_service_items` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `resident_id` BIGINT NOT NULL,
  `service_item_id` BIGINT NOT NULL,
  `relation_type` VARCHAR(64) NOT NULL,
  `note` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL,
  CONSTRAINT `fk_resident_service_items_resident` FOREIGN KEY (`resident_id`) REFERENCES `residents` (`id`),
  CONSTRAINT `fk_resident_service_items_item` FOREIGN KEY (`service_item_id`) REFERENCES `service_items` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `work_orders` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `work_order_id` VARCHAR(64) NOT NULL UNIQUE,
  `resident_id` BIGINT NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `category` VARCHAR(64) NOT NULL,
  `status` VARCHAR(32) NOT NULL,
  `status_desc` VARCHAR(255) NOT NULL,
  `amount` DECIMAL(10, 2) NOT NULL,
  `priority` VARCHAR(32) NOT NULL,
  `service_address` VARCHAR(255) NOT NULL,
  `contact_name` VARCHAR(64) NOT NULL,
  `contact_phone_masked` VARCHAR(32) NOT NULL,
  `appointment_time` DATETIME NULL,
  `created_at` DATETIME NOT NULL,
  CONSTRAINT `fk_work_orders_resident` FOREIGN KEY (`resident_id`) REFERENCES `residents` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `service_progress_records` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `work_order_id` BIGINT NOT NULL,
  `service_team` VARCHAR(64) NOT NULL,
  `assignee_name` VARCHAR(64) NOT NULL,
  `assignee_phone_masked` VARCHAR(32) NOT NULL,
  `current_stage` VARCHAR(32) NOT NULL,
  `stage_desc` VARCHAR(255) NOT NULL,
  `updated_at` DATETIME NOT NULL,
  CONSTRAINT `fk_progress_records_work_order` FOREIGN KEY (`work_order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `service_progress_traces` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `service_progress_record_id` BIGINT NOT NULL,
  `trace_time` DATETIME NOT NULL,
  `trace_desc` VARCHAR(255) NOT NULL,
  CONSTRAINT `fk_progress_traces_record` FOREIGN KEY (`service_progress_record_id`) REFERENCES `service_progress_records` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `complaint_requests` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `complaint_id` VARCHAR(64) NOT NULL UNIQUE,
  `work_order_id` BIGINT NOT NULL,
  `submitted_by` VARCHAR(64) NOT NULL,
  `reason` VARCHAR(255) NOT NULL,
  `status` VARCHAR(32) NOT NULL,
  `status_desc` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL,
  CONSTRAINT `fk_complaint_work_order` FOREIGN KEY (`work_order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `work_order_urge_requests` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT,
  `urge_id` VARCHAR(64) NOT NULL UNIQUE,
  `work_order_id` BIGINT NOT NULL,
  `submitted_by` VARCHAR(64) NOT NULL,
  `reason` VARCHAR(255) NOT NULL,
  `status` VARCHAR(32) NOT NULL,
  `status_desc` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL,
  CONSTRAINT `fk_urge_work_order` FOREIGN KEY (`work_order_id`) REFERENCES `work_orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `residents` (`resident_id`, `name`, `resident_level`, `mobile_masked`, `building`, `room_no`, `profile_note`, `created_at`) VALUES
  ('r1001', '李晨', '金卡业主', '138****1234', '1号楼', '1602', '高频报修住户，近一个月多次发起维修工单。', '2026-04-01 09:00:00'),
  ('r1002', '王敏', '标准业主', '139****5678', '8号楼', '702', '主要关注社区增值服务和装修报备。', '2026-04-02 10:30:00'),
  ('r1003', '陈昊', 'PLUS业主', '137****2468', '3号楼', '2301', '有过投诉和催办记录，适合演示异常与升级处理。', '2026-04-03 19:20:00');

INSERT INTO `service_items` (`service_item_id`, `title`, `description`, `price`, `service_status`, `cover_url`, `attributes_json`, `created_at`) VALUES
  (
    'SVC1001',
    '入户深度保洁',
    '提供厨房、卫生间、客厅和卧室的整屋深度保洁服务，适合换季或入住前集中清洁。',
    168.00,
    '可预约',
    'https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=900&q=80',
    JSON_OBJECT('服务时长', '3小时', '服务范围', '90平以内', '预约方式', '提前1天'),
    '2026-04-05 09:00:00'
  ),
  (
    'SVC1002',
    '空调清洗',
    '提供挂机与柜机的基础拆洗服务，适合夏季前保养。',
    120.00,
    '可预约',
    'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=900&q=80',
    JSON_OBJECT('服务对象', '1台空调', '上门时段', '09:00-18:00', '备注', '柜机需额外加价'),
    '2026-04-06 11:00:00'
  ),
  (
    'SVC1003',
    '搬家放行登记',
    '支持住户线上提交搬家日期、车辆和人员信息，便于门岗验放。',
    0.00,
    '线上办理',
    'https://images.unsplash.com/photo-1600518464441-9154a4dea21b?auto=format&fit=crop&w=900&q=80',
    JSON_OBJECT('办理时效', '即时受理', '所需材料', '身份证、车辆信息', '适用对象', '搬入或搬出住户'),
    '2026-04-08 14:00:00'
  ),
  (
    'SVC1004',
    '装修报备',
    '提供装修资料提交、施工证办理和巡检预约等服务。',
    200.00,
    '需审核',
    'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=900&q=80',
    JSON_OBJECT('所需资料', '施工图、身份证、押金单', '审批时效', '2个工作日', '施工时间', '工作日08:00-18:00'),
    '2026-04-10 16:00:00'
  ),
  (
    'SVC1005',
    '临停车位月租咨询',
    '面向住户提供月租车位余量、价格和办理流程说明。',
    450.00,
    '名额紧张',
    'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=900&q=80',
    JSON_OBJECT('计费周期', '按月', '当前余量', '少量', '适用车辆', '7座及以下'),
    '2026-04-11 10:00:00'
  ),
  (
    'SVC1006',
    '门禁卡补办',
    '丢失门禁卡后可在线登记补办申请并到服务中心领取。',
    50.00,
    '可办理',
    'https://images.unsplash.com/photo-1558002038-1055907df827?auto=format&fit=crop&w=900&q=80',
    JSON_OBJECT('领取地点', '物业服务中心', '办理时效', '1个工作日', '押金', '无'),
    '2026-04-12 13:30:00'
  ),
  (
    'SVC1007',
    '宠物登记年审',
    '用于社区养宠备案、免疫记录更新和门禁标签绑定。',
    30.00,
    '可办理',
    'https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=900&q=80',
    JSON_OBJECT('办理周期', '按年', '所需材料', '免疫证明、宠物照片', '适用范围', '犬只和猫只'),
    '2026-04-13 15:30:00'
  );

INSERT INTO `resident_service_items` (`resident_id`, `service_item_id`, `relation_type`, `note`, `created_at`) VALUES
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1001'), '历史使用', '年初做过一次全屋保洁。', '2026-04-18 09:00:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1002'), '高频咨询', '夏季前预约空调清洗。', '2026-04-19 09:30:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1006'), '近期办理', '门禁卡补办流程咨询。', '2026-04-20 14:00:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1002'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1003'), '近期咨询', '准备下周搬家。', '2026-04-18 10:00:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1002'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1004'), '重点办理', '装修报备材料准备中。', '2026-04-19 16:30:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1002'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1005'), '增值服务', '关注月租车位是否有空位。', '2026-04-20 11:00:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1003'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1001'), '历史使用', '保洁服务后有投诉记录。', '2026-04-17 12:00:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1003'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1005'), '高频咨询', '车位月租续费和变更咨询。', '2026-04-18 12:20:00'),
  ((SELECT `id` FROM `residents` WHERE `resident_id` = 'r1003'), (SELECT `id` FROM `service_items` WHERE `service_item_id` = 'SVC1007'), '年度办理', '宠物年审快到期。', '2026-04-19 09:40:00');

INSERT INTO `work_orders` (
  `work_order_id`, `resident_id`, `title`, `category`, `status`, `status_desc`, `amount`, `priority`,
  `service_address`, `contact_name`, `contact_phone_masked`, `appointment_time`, `created_at`
) VALUES
  ('WO20260501001', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), '主卧空调不制冷', '家电维修', '待上门', '工程班已联系住户，今晚 19:30 上门检修。', 80.00, '高', '1号楼1602', '李晨', '138****1234', '2026-05-19 19:30:00', '2026-05-19 08:35:00'),
  ('WO20260501002', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), '厨房水槽下方渗水', '水电维修', '处理中', '维修师傅已完成初检，等待更换软管配件。', 60.00, '中', '1号楼1602', '李晨', '138****1234', '2026-05-19 14:00:00', '2026-05-18 10:10:00'),
  ('WO20260501003', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), '客厅灯带频闪', '照明维修', '已完成', '灯带驱动器已更换，住户确认恢复正常。', 50.00, '中', '1号楼1602', '李晨', '138****1234', '2026-05-17 20:00:00', '2026-05-17 09:00:00'),
  ('WO20260501004', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), '门禁卡失效', '门禁服务', '待受理', '服务中心已收到工单，待安排门禁专员处理。', 20.00, '低', '1号楼1602', '李晨', '138****1234', NULL, '2026-05-19 09:15:00'),
  ('WO20260501005', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1001'), '卫生间地漏返味', '保洁消杀', '已关闭', '住户改为自行处理，工单关闭。', 0.00, '低', '1号楼1602', '李晨', '138****1234', NULL, '2026-05-12 18:00:00'),
  ('WO20260502001', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1002'), '装修报备资料审核', '装修管理', '处理中', '客服管家已核对首轮资料，等待补充施工人员名单。', 200.00, '中', '8号楼702', '王敏', '139****5678', NULL, '2026-05-16 13:20:00'),
  ('WO20260502002', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1002'), '搬家车辆进场登记', '搬家服务', '已完成', '门岗已完成放行登记，搬家当天可直接核验。', 0.00, '低', '8号楼702', '王敏', '139****5678', '2026-05-20 09:00:00', '2026-05-15 09:40:00'),
  ('WO20260502003', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1002'), '咨询车位月租办理', '车位服务', '待受理', '已生成咨询工单，等待客服管家回电说明。', 450.00, '低', '8号楼702', '王敏', '139****5678', NULL, '2026-05-19 10:05:00'),
  ('WO20260502004', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1002'), '阳台推拉门松动', '门窗维修', '待上门', '工程班已确认备件，明日上午上门加固。', 90.00, '中', '8号楼702', '王敏', '139****5678', '2026-05-20 10:00:00', '2026-05-19 08:55:00'),
  ('WO20260503001', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1003'), '地下车库车位锁故障', '车位服务', '处理中', '设备班已拆检，等待电机配件送达。', 120.00, '高', '3号楼地下B2-118', '陈昊', '137****2468', '2026-05-19 17:00:00', '2026-05-18 11:30:00'),
  ('WO20260503002', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1003'), '保洁服务质量投诉跟进', '投诉处理', '待受理', '投诉单已创建，客服主管待回访。', 0.00, '高', '3号楼2301', '陈昊', '137****2468', NULL, '2026-05-19 09:25:00'),
  ('WO20260503003', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1003'), '公共走廊噪音扰民反馈', '社区管理', '已完成', '管家已与相关住户沟通并完成巡查回访。', 0.00, '中', '3号楼23层走廊', '陈昊', '137****2468', NULL, '2026-05-13 21:10:00'),
  ('WO20260503004', (SELECT `id` FROM `residents` WHERE `resident_id` = 'r1003'), '宠物登记信息更新', '宠物管理', '已关闭', '住户未补交免疫证明，工单关闭待重提。', 30.00, '低', '3号楼2301', '陈昊', '137****2468', NULL, '2026-05-08 16:45:00');

INSERT INTO `service_progress_records` (
  `work_order_id`, `service_team`, `assignee_name`, `assignee_phone_masked`, `current_stage`, `stage_desc`, `updated_at`
) VALUES
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501001'), '工程维修一班', '张工', '186****2301', '待上门', '已与住户确认晚间上门。', '2026-05-19 11:20:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501002'), '工程维修二班', '周工', '186****5612', '处理中', '待配件到场后完成更换。', '2026-05-19 09:40:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501003'), '工程维修一班', '张工', '186****2301', '已完成', '维修完成并已回访。', '2026-05-17 20:10:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501004'), '门禁客服组', '刘婷', '185****7711', '待受理', '等待门禁专员确认卡号。', '2026-05-19 09:25:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501005'), '环境服务组', '何洁', '185****9201', '已关闭', '住户主动关闭工单。', '2026-05-12 19:10:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502001'), '客服管家组', '孙倩', '187****4332', '处理中', '资料审核中，需补充施工名单。', '2026-05-18 15:00:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502002'), '门岗服务组', '高峰', '187****6211', '已完成', '车辆信息核验通过。', '2026-05-15 15:30:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502003'), '客服管家组', '孙倩', '187****4332', '待受理', '等待回呼介绍方案。', '2026-05-19 10:20:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502004'), '工程维修三班', '罗工', '186****1188', '待上门', '已排明日上午上门时间。', '2026-05-19 09:10:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503001'), '设备维保班', '沈工', '188****6682', '处理中', '待车位锁电机配件送达。', '2026-05-19 10:50:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503002'), '客服主管组', '秦岚', '188****1218', '待受理', '主管待联系住户进行回访。', '2026-05-19 09:40:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503003'), '社区巡查组', '冯超', '188****7751', '已完成', '完成上门沟通和回访。', '2026-05-14 08:30:00'),
  ((SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503004'), '客服管家组', '秦岚', '188****1218', '已关闭', '材料超时未补齐。', '2026-05-10 18:10:00');

INSERT INTO `service_progress_traces` (`service_progress_record_id`, `trace_time`, `trace_desc`) VALUES
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501001')), '2026-05-19 11:20:00', '维修师傅已联系住户，确认今晚 19:30 上门。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501001')), '2026-05-19 09:10:00', '工程班完成派单。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501001')), '2026-05-19 08:35:00', '住户提交空调不制冷报修。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501002')), '2026-05-19 09:40:00', '现场检查发现软管老化，待仓库发配件。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501002')), '2026-05-18 14:15:00', '维修师傅上门初检。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501002')), '2026-05-18 10:10:00', '工单创建并分派给工程班。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501003')), '2026-05-17 20:10:00', '更换灯带驱动器后恢复正常，住户确认完成。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501003')), '2026-05-17 18:00:00', '工程班上门检修。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501003')), '2026-05-17 09:00:00', '工单提交。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501004')), '2026-05-19 09:25:00', '服务中心已记录失效卡号，待专员核验。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501004')), '2026-05-19 09:15:00', '住户提交门禁卡失效工单。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501005')), '2026-05-12 19:10:00', '住户表示自行购买除味剂处理，申请关闭工单。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501005')), '2026-05-12 18:00:00', '工单创建。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502001')), '2026-05-18 15:00:00', '客服管家提醒补交施工人员名单和垃圾清运承诺书。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502001')), '2026-05-17 09:30:00', '首轮资料审核通过。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502001')), '2026-05-16 13:20:00', '住户提交装修报备申请。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502002')), '2026-05-15 15:30:00', '车辆、司机和搬运人员信息核验通过。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502002')), '2026-05-15 10:00:00', '门岗收到搬家放行单。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502002')), '2026-05-15 09:40:00', '住户提交搬家登记。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502003')), '2026-05-19 10:20:00', '客服管家待回呼说明当前车位月租余量与价格。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502003')), '2026-05-19 10:05:00', '住户提交车位月租咨询。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502004')), '2026-05-19 09:10:00', '已通知师傅明日上午携带滑轮配件上门。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502004')), '2026-05-19 08:55:00', '住户提交阳台门松动工单。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503001')), '2026-05-19 10:50:00', '车位锁电机已申请领料，预计下午到场。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503001')), '2026-05-18 17:00:00', '设备班上门拆检，确认电机故障。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503001')), '2026-05-18 11:30:00', '住户提交车位锁故障工单。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503002')), '2026-05-19 09:40:00', '客服主管待电话回访，核实保洁服务现场情况。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503002')), '2026-05-19 09:25:00', '住户提交服务质量投诉。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503003')), '2026-05-14 08:30:00', '客服完成回访，住户反馈噪音已消除。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503003')), '2026-05-13 22:00:00', '夜间巡查人员到场提醒相关住户。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503003')), '2026-05-13 21:10:00', '住户提交噪音扰民反馈。'),

  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503004')), '2026-05-10 18:10:00', '住户超时未补交免疫证明，系统关闭工单。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503004')), '2026-05-09 10:00:00', '客服提醒补齐免疫证明。'),
  ((SELECT `id` FROM `service_progress_records` WHERE `work_order_id` = (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503004')), '2026-05-08 16:45:00', '住户提交宠物登记更新申请。');

INSERT INTO `complaint_requests` (
  `complaint_id`, `work_order_id`, `submitted_by`, `reason`, `status`, `status_desc`, `created_at`
) VALUES
  (
    'C202605160001',
    (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503002'),
    'resident',
    '上次保洁服务后地面残留明显，希望重新核查服务质量。',
    'processing',
    '客服主管已受理，正在安排复核回访。',
    '2026-05-19 09:30:00'
  ),
  (
    'C202605120002',
    (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501005'),
    'resident',
    '返味问题曾多次出现，希望评估公共管道是否存在隐患。',
    'completed',
    '环境组已完成说明并向住户反馈排查结论。',
    '2026-05-12 18:40:00'
  ),
  (
    'C202605140003',
    (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503003'),
    'resident',
    '夜间噪音多次发生，希望加强巡查。',
    'completed',
    '社区管家已完成楼层巡查安排并回访。',
    '2026-05-14 08:10:00'
  );

INSERT INTO `work_order_urge_requests` (
  `urge_id`, `work_order_id`, `submitted_by`, `reason`, `status`, `status_desc`, `created_at`
) VALUES
  (
    'U202605190001',
    (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260501001'),
    'resident',
    '天气炎热，家里有老人，希望尽快安排空调检修。',
    'submitted',
    '催办申请已提交，工程班会优先协调时间。',
    '2026-05-19 10:00:00'
  ),
  (
    'U202605180002',
    (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260503001'),
    'resident',
    '车辆晚间需要出入，车位锁故障影响使用。',
    'submitted',
    '设备班已收到催办提醒，正在跟进配件。',
    '2026-05-19 08:20:00'
  ),
  (
    'U202605190003',
    (SELECT `id` FROM `work_orders` WHERE `work_order_id` = 'WO20260502004'),
    'resident',
    '家里有小孩，担心阳台门继续松动存在安全风险。',
    'submitted',
    '催办申请已提交，工程班将优先上门。',
    '2026-05-19 09:30:00'
  );
