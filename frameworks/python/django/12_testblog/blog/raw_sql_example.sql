-- Пример ручного SQL-запроса, которым можно было бы получить ленту сообщений --
-- Пусть id пользователя, для которого делаем ленту, userid=2 --

SELECT * FROM blog_post

    -- Приджойнить подписки нашего пользователя для будущей фильтрации --
    JOIN blog_subsribe
    ON blog_post.user_id = blog_subsribe.user_to_id AND blog_subsribe.user_from_id = 2

WHERE
        -- фильтр по свежести сообщения относительно подписки --
        blog_post.datetime >= blog_subsribe.datetime
        
        -- фильтр по прочитанным постам --
    AND blog_post.id NOT IN (SELECT post_id from blog_myuser_read_posts WHERE myuser_id = 2)

ORDER BY blog_post. datetime DESC