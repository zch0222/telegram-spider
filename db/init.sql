-- auto-generated definition
create table IF NOT EXISTS tb_message
(
    id              bigint unsigned auto_increment comment 'id'
        primary key,
    channel         varchar(250)                       null comment '频道地址',
    channel_name    varchar(500)                       null,
    sender_id       varchar(250)                       null,
    sender_username varchar(250)                       null,
    message_id      bigint unsigned                    null comment '消息id',
    date            datetime                           null comment '消息日期',
    message_text    varchar(2000)                      null comment '消息文本',
    link            varchar(500)                       null comment '链接',
    create_time     datetime default CURRENT_TIMESTAMP null comment '创建时间',
    update_time     datetime default CURRENT_TIMESTAMP null comment '更新时间'
)
    collate = utf8mb4_unicode_ci;

-- auto-generated definition
create table IF NOT EXISTS tb_sub_group
(
    id              bigint unsigned auto_increment comment 'id'
        primary key,
    group_type      tinyint(1) not null comment '群组类型:0 群聊 1 频道',
    group_id        varchar(250)                       null comment '群组id',
    group_name      varchar(250)                       null comment '群组名称',
    group_link      varchar(500)                       null comment '链接',
    create_time     datetime default CURRENT_TIMESTAMP null comment '创建时间',
    update_time     datetime default CURRENT_TIMESTAMP null comment '更新时间'
)
    collate = utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tb_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tb_yt_dlp_task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(1000) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, downloading, completed, error
    title VARCHAR(500),
    file_path VARCHAR(500),
    total_bytes BIGINT,
    downloaded_bytes BIGINT,
    progress DECIMAL(5, 2) DEFAULT 0.00,
    speed VARCHAR(50), -- e.g., "1.5 MiB/s"
    eta VARCHAR(50), -- e.g., "00:05"
    error_msg TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
