CREATE TABLE `ex_gyms` (
    `gym_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
    `ex` tinyint(1) NOT NULL,
    `pass` tinyint(1) NOT NULL,
    PRIMARY KEY (`gym_id`)
)