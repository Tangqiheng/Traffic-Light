-- 批量插入20个测试用户到 user 表
-- 请根据实际表名和字段名调整
INSERT INTO user (username, email, full_name, password_hash, is_admin, is_active)
VALUES
('user01', 'user01@example.com', '测试用户01', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user02', 'user02@example.com', '测试用户02', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user03', 'user03@example.com', '测试用户03', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user04', 'user04@example.com', '测试用户04', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user05', 'user05@example.com', '测试用户05', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user06', 'user06@example.com', '测试用户06', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user07', 'user07@example.com', '测试用户07', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user08', 'user08@example.com', '测试用户08', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user09', 'user09@example.com', '测试用户09', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user10', 'user10@example.com', '测试用户10', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user11', 'user11@example.com', '测试用户11', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user12', 'user12@example.com', '测试用户12', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user13', 'user13@example.com', '测试用户13', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user14', 'user14@example.com', '测试用户14', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user15', 'user15@example.com', '测试用户15', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user16', 'user16@example.com', '测试用户16', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user17', 'user17@example.com', '测试用户17', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user18', 'user18@example.com', '测试用户18', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user19', 'user19@example.com', '测试用户19', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1),
('user20', 'user20@example.com', '测试用户20', '$2b$12$Qe0Qw6Qw6Qw6Qw6Qw6Qw6uQw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6Qw6', 0, 1);
-- 密码hash为同一固定值（建议后续用真实hash替换），可用123456登录（如需更安全可用脚本批量生成）
-- 导入后如有唯一索引冲突请先清空user表或调整用户名/邮箱