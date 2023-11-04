-- auto-generated definition
create table tb_message
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