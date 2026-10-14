-- Демонстрационные данные сервиса «КакДостать Соседа».
-- Пароль всех пользователей: password123
-- Применять к пустой БД (после миграций или после app/db/DB.sql).

-- Пользователи
INSERT INTO users (id, email, password_hash, role) VALUES
('11111111-1111-1111-1111-111111111111', 'alice@example.com', '$2b$12$Kaw7DEKqmQSJLyAiOJHJHuz/cx/Jwf3Nxjt/in4NkJrnmHjxDtKzi', 'user'),
('22222222-2222-2222-2222-222222222222', 'bob@example.com',   '$2b$12$Kaw7DEKqmQSJLyAiOJHJHuz/cx/Jwf3Nxjt/in4NkJrnmHjxDtKzi', 'user'),
('33333333-3333-3333-3333-333333333333', 'carol@example.com', '$2b$12$Kaw7DEKqmQSJLyAiOJHJHuz/cx/Jwf3Nxjt/in4NkJrnmHjxDtKzi', 'user'),
('44444444-4444-4444-4444-444444444444', 'admin@example.com', '$2b$12$Kaw7DEKqmQSJLyAiOJHJHuz/cx/Jwf3Nxjt/in4NkJrnmHjxDtKzi', 'admin');

-- Анкеты
INSERT INTO profiles (id, user_id, first_name, last_name, age, gender, city, district, metro_station, minutes_to_metro, bio, photo_url) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', '11111111-1111-1111-1111-111111111111', 'Алиса', 'Иванова',  24, 'female', 'Москва', 'Центральный', 'Охотный Ряд',  5,  'Люблю музыку и книги',      NULL),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', '22222222-2222-2222-2222-222222222222', 'Боб',   'Петров',   27, 'male',   'Москва', 'Центральный', 'Охотный Ряд',  7,  'Спорт и путешествия',        NULL),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', '33333333-3333-3333-3333-333333333333', 'Кэрол', 'Сидорова', 29, 'female', 'Москва', 'Северный',    'Полежаевская', 10, 'Ищу соседа в свою квартиру', NULL);

-- Хобби
INSERT INTO hobbies (id, profile_id, films, music, sports, reading, gaming, books, photography, cooking, arts, table_games, travel, walking, dancing, singing) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', FALSE, TRUE,  FALSE, TRUE,  FALSE, TRUE,  FALSE, TRUE,  FALSE, FALSE, FALSE, TRUE,  FALSE, FALSE),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', TRUE,  FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE,  TRUE,  FALSE, FALSE, FALSE),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', TRUE,  TRUE,  TRUE,  TRUE,  FALSE, TRUE,  TRUE,  TRUE,  TRUE,  TRUE,  TRUE,  TRUE,  TRUE,  TRUE);

-- Привычки
INSERT INTO bad_habits (id, profile_id, smoking, pets, sleep_mode, noise_preference, guests) VALUES
('cccccccc-cccc-cccc-cccc-ccccccccccc1', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', FALSE, TRUE,  'early', 'quiet', TRUE),
('cccccccc-cccc-cccc-cccc-ccccccccccc2', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', FALSE, TRUE,  'early', 'quiet', TRUE),
('cccccccc-cccc-cccc-cccc-ccccccccccc3', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', FALSE, FALSE, 'late',  'loud',  FALSE);

-- Предпочтения к соседу
INSERT INTO preferences (id, profile_id, age_min, age_max, gender_preference, budget_max, city_preference, district_preference, metro_preference, smoking_preference, pets_preference, guests_preference, sleep_mode_preference, noise_preference) VALUES
('dddddddd-dddd-dddd-dddd-ddddddddddd1', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', 20, 35, 'male',   45000, 'Москва', ARRAY['Центральный'],               ARRAY['Охотный Ряд'],                 'no',  'yes', 'any', 'any',   'any'),
('dddddddd-dddd-dddd-dddd-ddddddddddd2', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 20, 35, 'female', 40000, 'Москва', ARRAY['Центральный'],               ARRAY['Охотный Ряд'],                 'no',  'yes', 'any', 'early', 'quiet'),
('dddddddd-dddd-dddd-dddd-ddddddddddd3', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', 18, 40, 'any',    60000, 'Москва', ARRAY['Центральный','Северный'],    ARRAY['Охотный Ряд','Полежаевская'],  'any', 'any', 'any', 'any',   'any');

-- Лайки и взаимное совпадение (Алиса <-> Боб)
INSERT INTO likes (id, from_user_id, to_user_id) VALUES
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee2', '22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111');

INSERT INTO matches (id, user1_id, user2_id) VALUES
('ffffffff-ffff-ffff-ffff-fffffffffff1', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222');

INSERT INTO chats (id, match_id) VALUES
('12121212-1212-1212-1212-121212121212', 'ffffffff-ffff-ffff-ffff-fffffffffff1');

INSERT INTO messages (id, chat_id, sender_id, content, is_read) VALUES
('13131313-1313-1313-1313-131313131311', '12121212-1212-1212-1212-121212121212', '11111111-1111-1111-1111-111111111111', 'Привет! Как насчёт вместе поискать квартиру?', TRUE),
('13131313-1313-1313-1313-131313131312', '12121212-1212-1212-1212-121212121212', '22222222-2222-2222-2222-222222222222', 'Привет! Давай, я как раз смотрю варианты.', FALSE);

-- Объявление «Ищу соседа» от Кэрол
INSERT INTO announcements (id, user_id, room_price, total_rooms, area, move_in_date, description, free) VALUES
('14141414-1414-1414-1414-141414141414', '33333333-3333-3333-3333-333333333333', 32000, 3, 72, '2026-11-01', 'Сдаю комнату в трёхкомнатной квартире, есть всё необходимое.', TRUE);

INSERT INTO addresses (id, announcement_id, city, street, house_number, district, metro_station, minutes_to_metro) VALUES
('15151515-1515-1515-1515-151515151515', '14141414-1414-1414-1414-141414141414', 'Москва', 'Полежаевская', '10', 'Северный', 'Полежаевская', 10);

INSERT INTO announcement_rules (id, announcement_id, smoking_allowed, pets_allowed, guests_allowed, sleep_mode, noise_level) VALUES
('16161616-1616-1616-1616-161616161616', '14141414-1414-1414-1414-141414141414', FALSE, TRUE, TRUE, 'any', 'quiet');

INSERT INTO announcement_amenities (id, announcement_id, internet, furniture, kitchen, washing_machine, dishwasher, balcony, elevator, air_conditioning) VALUES
('17171717-1717-1717-1717-171717171717', '14141414-1414-1414-1414-141414141414', TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, FALSE);

INSERT INTO announcement_photos (id, announcement_id, url, is_main, position) VALUES
('18181818-1818-1818-1818-181818181811', '14141414-1414-1414-1414-141414141414', 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267', TRUE, 0),
('18181818-1818-1818-1818-181818181812', '14141414-1414-1414-1414-141414141414', 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688', FALSE, 1);

-- Заявка Алисы на объявление Кэрол
INSERT INTO applications (id, announcement_id, applicant_id, message, status) VALUES
('19191919-1919-1919-1919-191919191911', '14141414-1414-1414-1414-141414141414', '11111111-1111-1111-1111-111111111111', 'Здравствуйте! Очень заинтересовало объявление.', 'pending');

-- Отзывы
INSERT INTO reviews (id, reviewer_id, reviewed_user_id, rating, comment) VALUES
('20202020-2020-2020-2020-202020202021', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222', 5, 'Отличный сосед, рекомендую!'),
('20202020-2020-2020-2020-202020202022', '22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 4, 'Аккуратная и дружелюбная.');

-- Уведомления
INSERT INTO notifications (id, user_id, type, body, is_read) VALUES
('21212121-2121-2121-2121-212121212121', '22222222-2222-2222-2222-222222222222', 'like',        'Вам поставили отметку «Мне подходит»', FALSE),
('21212121-2121-2121-2121-212121212122', '11111111-1111-1111-1111-111111111111', 'match',       'Взаимный интерес! Чат создан',          FALSE),
('21212121-2121-2121-2121-212121212123', '33333333-3333-3333-3333-333333333333', 'application', 'Новая заявка на подселение',            FALSE);

-- Избранное и просмотры
INSERT INTO favorites (id, user_id, target_type, target_id) VALUES
('23232323-2323-2323-2323-232323232321', '11111111-1111-1111-1111-111111111111', 'announcement', '14141414-1414-1414-1414-141414141414');

INSERT INTO views (id, user_id, target_type, target_id) VALUES
('24242424-2424-2424-2424-242424242421', '11111111-1111-1111-1111-111111111111', 'profile', '22222222-2222-2222-2222-222222222222');
