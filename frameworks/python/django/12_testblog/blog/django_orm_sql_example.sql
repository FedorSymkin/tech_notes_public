-- Пример запроса, который генерируется django ORM для получения ленты сообщений --
-- Пусть id пользователя, для которого делаем ленту, userid=2 --

-- ======================================================== --
-- Это основной запрос --

SELECT "blog_post"."id",
       "blog_post"."user_id",
       "blog_post"."title",
       "blog_post"."content",
       "blog_post"."datetime"
FROM "blog_post"
INNER JOIN "blog_myuser" ON ("blog_post"."user_id" = "blog_myuser"."id")
INNER JOIN "blog_subsribe" ON ("blog_myuser"."id" = "blog_subsribe"."user_to_id")
WHERE ("blog_subsribe"."datetime" <= ("blog_post"."datetime")
       AND "blog_subsribe"."user_from_id" = 2
       AND NOT ("blog_post"."id" IN
                  (SELECT U0."post_id"
                   FROM "blog_myuser_read_posts" U0
                   WHERE U0."myuser_id" = 2)))
ORDER BY "blog_post"."datetime" DESC;

-- ======================================================== --
-- Это избыточный запрос --

SELECT "blog_myuser"."id",
       "blog_myuser"."password",
       "blog_myuser"."last_login",
       "blog_myuser"."is_superuser",
       "blog_myuser"."username",
       "blog_myuser"."first_name",
       "blog_myuser"."last_name",
       "blog_myuser"."email",
       "blog_myuser"."is_staff",
       "blog_myuser"."is_active",
       "blog_myuser"."date_joined"
FROM "blog_myuser"
WHERE "blog_myuser"."id" IN (1,
                             4);

-- ======================================================== --
-- Это избыточный запрос --

SELECT "blog_subsribe"."id",
       "blog_subsribe"."user_from_id",
       "blog_subsribe"."user_to_id",
       "blog_subsribe"."datetime"
FROM "blog_subsribe"
WHERE "blog_subsribe"."user_to_id" IN (1,
                                       4);
