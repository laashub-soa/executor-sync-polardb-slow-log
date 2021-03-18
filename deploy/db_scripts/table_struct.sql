CREATE TABLE `polardb_slow_log`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `db_cluster_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '集群ID',
  `db_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '数据库名称',
  `db_node_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '节点ID',
  `execution_start_time` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'SQL开始执行的时间。格式为YYYY-MM-DDThh:mmZ（UTC时间）',
  `host_address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '连接数据库的客户端地址',
  `lock_times` int(0) NULL DEFAULT NULL COMMENT 'SQL锁定时长，单位为秒',
  `query_times` int(0) NULL DEFAULT NULL COMMENT 'SQL执行时长，单位为秒',
  `parse_row_counts` int(0) NULL DEFAULT NULL COMMENT '解析行数',
  `return_row_counts` int(0) NULL DEFAULT NULL COMMENT '返回行数',
  `sql_text` mediumblob NULL COMMENT '查询语句',
  `data_timestamp` int(0) NULL DEFAULT NULL COMMENT '数据的实际时间戳',
  `sql_template_id` int(0) NULL DEFAULT NULL COMMENT 'SQL模板id',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 0 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

CREATE TABLE `polardb_slow_log_template`  (
  `id` int(0) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `db_cluster_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '集群ID',
  `db_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '数据库名称',
  `db_node_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '节点ID',
  `sql_text` mediumblob NULL COMMENT '查询语句',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 0 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;